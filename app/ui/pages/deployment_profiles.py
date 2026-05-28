"""Deployment profile comparison page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.ui.mock_data import get_state


def render() -> None:
    """Render the deployment profiles page."""
    state = get_state()
    st.title("Deployment Profiles")
    st.caption("Compare cloud and self-hosted managed-agent operating models.")

    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Feature": item.capability,
                    "Cloud": item.cloud,
                    "Self-hosted": item.self_hosted,
                }
                for item in state.deployment_features
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )
