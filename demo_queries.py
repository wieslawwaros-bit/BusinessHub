import sqlite3
from pathlib import Path
DB = Path(__file__).resolve().parent / "procurement_demo.db"
GROUPS = {'company': "'All'", 'supplier': 'supplier_name',
          'category': 'category', 'month': 'substr(order_date,1,7)',
          'year': 'substr(order_date,1,4)'}
METRICS = {'spend_pln': 'DESC', 'variance_pln': 'DESC',
           'variance_pct': 'DESC', 'on_time_pct': 'ASC',
           'quality_issue_pct': 'DESC', 'transactions': 'DESC',
           'average_delay_days': 'DESC', 'period': 'ASC'}

def query(sql, params=()):
    if not DB.is_file():
        raise FileNotFoundError(DB)
    with sqlite3.connect(DB.as_uri() + '?mode=ro', uri=True) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(r) for r in conn.execute(sql, params)]


def filters(year=None, category=None, supplier=None, material_id=None):
    clauses, args = ['1=1'], []
    if year is not None:
        if str(year) not in ('2025', '2026'):
            raise ValueError('Year must be 2025 or 2026')
        clauses.append('substr(order_date,1,4)=?')
        args.append(str(year))
    for col, val in [('category', category), ('supplier_name', supplier), ('material_id', material_id)]:
        if val is not None:
            if not isinstance(val, str) or len(val) > 150:
                raise ValueError('Invalid filter')
            clauses.append(col + ' = ? COLLATE NOCASE')
            args.append(val)
    return ' AND '.join(clauses), args


def performance(group_by='supplier', metric='variance_pln', year=None,
                category=None, supplier=None, limit=10, min_transactions=1):
    group = GROUPS[group_by]
    direction = METRICS[metric]
    limit = max(1, min(24, int(limit)))
    minimum = max(1, int(min_transactions))
    where, args = filters(year, category, supplier)
    order = 'group_name ASC' if metric == 'period' else f'{metric} {direction}, group_name ASC'
    rows = query(f'''SELECT {group} AS group_name, COUNT(*) AS transactions,
        COUNT(DISTINCT supplier_id) AS suppliers,
        MIN(order_date) AS period_start, MAX(order_date) AS period_end,
        ROUND(SUM(actual_value_pln),2) AS spend_pln,
        ROUND(SUM(variance_pln),2) AS variance_pln,
        ROUND(100.0*SUM(variance_pln)/NULLIF(SUM(budget_value_pln),0),2) AS variance_pct,
        ROUND(100.0*AVG(on_time),2) AS on_time_pct,
        ROUND(100.0*AVG(quality_issue),2) AS quality_issue_pct,
        ROUND(AVG(delay_days),2) AS average_delay_days
        FROM procurement_transactions WHERE {where}
        GROUP BY {group} HAVING COUNT(*) >= ? ORDER BY {order} LIMIT ?''',
        args + [minimum, limit])
    return {'rows': rows, 'group_by': group_by, 'metric': metric, 'limit': limit,
            'min_transactions': minimum, 'note': 'Transaction-based KPIs. Positive variance = overspending. PLN. 2026 ends 2026-11-15.'}


def price_history(material_id, year=None):
    where, args = filters(year, material_id=material_id)
    return {'rows': query(f'''SELECT substr(order_date,1,7) AS month,
        material_id, material_name, currency, unit, COUNT(*) AS transactions,
        SUM(quantity) AS quantity,
        ROUND(SUM(actual_unit_price*quantity)/NULLIF(SUM(quantity),0),4) AS weighted_unit_price
        FROM procurement_transactions WHERE {where} AND quantity>0
        GROUP BY month, material_id, material_name, currency, unit
        ORDER BY month, currency, unit LIMIT 100''', args),
        'note': 'Compare only identical material, currency and unit. Quantity-weighted prices.'}


def lookup(kind, search=''):
    cols = {'category': ('category', 'category'), 'supplier': ('supplier_name', 'supplier_name'),
            'material': ('material_id', 'material_name')}
    key, name = cols[kind]
    return {'rows': query(f'''SELECT DISTINCT {key} AS id, {name} AS name
        FROM procurement_transactions WHERE {name} LIKE ? OR {key} LIKE ?
        ORDER BY id LIMIT 25''', ['%'+str(search)+'%']*2), 'limit': 25}


def concentration(year=None, category=None, limit=10):
    where, args = filters(year, category)
    limit = max(1, min(20, int(limit)))
    rows = query(f'''WITH s AS (SELECT supplier_name, SUM(actual_value_pln) AS spend
        FROM procurement_transactions WHERE {where} GROUP BY supplier_name),
        t AS (SELECT SUM(spend) AS total FROM s)
        SELECT supplier_name, ROUND(spend,2) AS spend_pln,
        ROUND(100.0*spend/NULLIF(total,0),2) AS share_pct
        FROM s CROSS JOIN t ORDER BY spend DESC, supplier_name ASC LIMIT ?''', args+[limit])
    total = query(f'SELECT SUM(actual_value_pln) AS total FROM procurement_transactions WHERE {where}', args)[0]['total']
    total = total or 0
    return {'rows': rows, 'total_spend_pln': round(total, 2),
            'top_5_share_pct': round(100*sum(r['spend_pln'] for r in rows[:5])/total,2) if total and limit>=5 else None,
            'top_10_share_pct': round(100*sum(r['spend_pln'] for r in rows[:10])/total,2) if total and limit>=10 else None,
            'top_share_pct_approx': round(100*sum(r['spend_pln'] for r in rows)/total,2) if total else None, 'limit': limit}


def delivery_comparison(min_transactions=30, limit=10):
    return {'rows': query('''WITH s AS (SELECT supplier_name, substr(order_date,1,4) AS yr,
      COUNT(*) AS n, AVG(on_time)*100 AS pct FROM procurement_transactions
      WHERE substr(order_date,1,4) IN ('2025','2026') GROUP BY supplier_name,yr)
      SELECT a.supplier_name,a.n AS transactions_2025,b.n AS transactions_2026,
      ROUND(a.pct,2) AS on_time_2025,ROUND(b.pct,2) AS on_time_2026,
      ROUND(b.pct-a.pct,2) AS change_pp FROM s a JOIN s b ON a.supplier_name=b.supplier_name
      WHERE a.yr='2025' AND b.yr='2026' AND a.n>=? AND b.n>=?
      ORDER BY change_pp ASC LIMIT ?''', [max(1,int(min_transactions))]*2+[max(1,min(20,int(limit)))]),
      'note':'Full 2025 vs available 2026 through November 15; minimum transactions in each year.'}


def material_variances(year=None, category=None, limit=10):
    where,args=filters(year,category)
    return {'rows':query(f'''SELECT material_id, material_name, COUNT(*) AS transactions,
      ROUND(SUM(variance_pln),2) AS variance_pln, ROUND(SUM(actual_value_pln),2) AS spend_pln
      FROM procurement_transactions WHERE {where} GROUP BY material_id, material_name
      ORDER BY variance_pln DESC LIMIT ?''', args+[max(1,min(20,int(limit)))]),
      'note':'Total budget variance in PLN, not isolated unit price effect.'}

