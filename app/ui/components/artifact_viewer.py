"""Reusable artifact display helpers."""

from __future__ import annotations

import json
from typing import Mapping

import streamlit as st


def render_markdown_artifact(title: str, content: str) -> None:
    """Render a markdown-like artifact inside an expander."""
    with st.expander(title, expanded=False):
        st.markdown(content)


def render_json_artifact(title: str, payload: Mapping[str, str]) -> None:
    """Render a JSON artifact inside an expander."""
    with st.expander(title, expanded=False):
        st.code(json.dumps(dict(payload), indent=2), language="json")
