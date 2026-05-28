"""Reusable event timeline component."""

from __future__ import annotations

from typing import Iterable

import streamlit as st

from app.ui.mock_data import EventItem


def render_event_timeline(events: Iterable[EventItem], title: str = "Event Feed") -> None:
    """Render an expander-based event timeline."""
    st.subheader(title)
    for event in events:
        label = f"{event.timestamp} • {event.event_type} • {event.agent}"
        with st.expander(label, expanded=event.event_type == "approval.required"):
            left_col, right_col = st.columns([1, 3])
            left_col.caption("Summary")
            left_col.write(event.summary)
            right_col.caption("Details")
            right_col.write(event.details)
