"""Main Streamlit entry point for the OpsBridge demo UI."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from app.ui.mock_data import get_state
from app.ui.pages import (
    approval_inbox,
    audit_ledger,
    control_room,
    deployment_profiles,
    memory_lab,
    outcome_inspector,
    thread_explorer,
)


PageRenderer = Callable[[], None]


def _apply_theme() -> None:
    """Apply shared page configuration and dark-mode CSS."""
    st.set_page_config(
        page_title="OpsBridge Control Plane",
        page_icon=":satellite:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(14, 165, 233, 0.14), transparent 28%),
                    radial-gradient(circle at top right, rgba(34, 197, 94, 0.08), transparent 24%),
                    linear-gradient(180deg, #020617 0%, #0f172a 100%);
                color: #e5eefb;
            }
            [data-testid="stSidebar"] {
                background: rgba(15, 23, 42, 0.96);
                border-right: 1px solid rgba(148, 163, 184, 0.18);
            }
            [data-testid="stMetric"] {
                background: rgba(15, 23, 42, 0.82);
                border: 1px solid rgba(51, 65, 85, 0.9);
                padding: 0.9rem 1rem;
                border-radius: 1rem;
            }
            div[data-testid="stExpander"] {
                border: 1px solid rgba(51, 65, 85, 0.9);
                border-radius: 1rem;
                background: rgba(15, 23, 42, 0.7);
            }
            div[data-testid="stDataFrame"] {
                border-radius: 1rem;
                overflow: hidden;
                border: 1px solid rgba(51, 65, 85, 0.9);
            }
            .stButton > button {
                border-radius: 999px;
                border: 1px solid rgba(71, 85, 105, 1);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _page_registry() -> dict[str, PageRenderer]:
    """Return the sidebar page registry."""
    return {
        "Control Room": control_room.render,
        "Thread Explorer": thread_explorer.render,
        "Approval Inbox": approval_inbox.render,
        "Outcome Inspector": outcome_inspector.render,
        "Audit Ledger": audit_ledger.render,
        "Memory Lab": memory_lab.render,
        "Deployment Profiles": deployment_profiles.render,
    }


def main() -> None:
    """Run the Streamlit UI."""
    _apply_theme()
    state = get_state()
    pages = _page_registry()

    with st.sidebar:
        st.title("OpsBridge")
        st.caption("Claude Managed Agents demo")
        st.metric("Active Run", state.active_run_id)
        selected_page = st.radio("Navigate", options=list(pages.keys()))
        st.markdown("---")
        st.write("Profiles")
        st.write("`cloud_demo`")
        st.write("`self_hosted_demo`")

    pages[selected_page]()


if __name__ == "__main__":
    main()
