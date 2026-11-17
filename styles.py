
import streamlit as st


def apply_custom_styles():
    """Wspólne style aplikacji BusinessHub."""

    st.markdown(
        """
        <style>

        /* Narrower sidebar */
        [data-testid="stSidebar"] {
            width: 200px !important;
            min-width: 200px !important;
        }

        [data-testid="stSidebar"][aria-expanded="true"] {
            width: 200px !important;
            min-width: 200px !important;
        }

        /* More compact navigation */
        [data-testid="stSidebarNav"] {
            padding-top: 0.5rem;
        }

        /* Main content */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
