"""Control room page for starting and monitoring investigations."""

from __future__ import annotations

import streamlit as st

from app.ui.components.event_timeline import render_event_timeline
from app.ui.mock_data import EventItem, get_state, save_state


def _start_investigation() -> None:
    """Update the mock state to reflect a new investigation start."""
    state = get_state()
    state.outcome_status = "Running"
    state.interrupted = False
    filename = state.uploaded_filename or "incident-briefing.txt"
    state.event_feed.insert(
        0,
        EventItem(
            timestamp=state.event_feed[0].timestamp,
            event_type="user.start",
            summary=f"Investigation restarted for {state.selected_incident}.",
            details=f"Operator launched a new run with supporting file `{filename}`.",
            agent="Operator",
        ),
    )
    save_state(state)


def _interrupt_run() -> None:
    """Mark the current run as interrupted."""
    state = get_state()
    state.interrupted = True
    state.outcome_status = "Blocked"
    state.event_feed.insert(
        0,
        EventItem(
            timestamp=state.event_feed[0].timestamp,
            event_type="user.interrupt",
            summary="Operator interrupted the active investigation.",
            details="Coordinator should stop further tool execution and await review.",
            agent="Operator",
        ),
    )
    save_state(state)


def render() -> None:
    """Render the control room page."""
    state = get_state()
    st.title("Control Room")
    st.caption("Run a governed incident investigation using managed-agent mock state.")

    summary_cols = st.columns(4)
    summary_cols[0].metric("Active Incident", state.selected_incident)
    summary_cols[1].metric("Outcome Status", state.outcome_status)
    summary_cols[2].metric(
        "Pending Approvals", str(sum(item.decision == "pending" for item in state.approvals))
    )
    summary_cols[3].metric("Specialists", str(len(state.specialists)))

    with st.container(border=True):
        left_col, right_col = st.columns([2, 1])
        selected_incident = left_col.selectbox(
            "Scenario",
            options=["INC-042", "INC-043", "INC-044"],
            index=["INC-042", "INC-043", "INC-044"].index(state.selected_incident),
        )
        upload = left_col.file_uploader(
            "Attach supporting artifact",
            type=["txt", "json", "md", "log"],
            help="Mock-only uploader; files remain in the browser session.",
        )
        if upload is not None:
            state.uploaded_filename = upload.name
        state.selected_incident = selected_incident

        right_col.markdown("**Current artifact**")
        right_col.write(state.uploaded_filename or "No file uploaded")
        right_col.button("Start Investigation", type="primary", on_click=_start_investigation)
        right_col.button("Interrupt", on_click=_interrupt_run)
        badge_color = {
            "Running": "#2dd4bf",
            "Blocked": "#f59e0b",
            "Completed": "#22c55e",
        }[state.outcome_status]
        right_col.markdown(
            f"""
            <div style="margin-top:1rem;padding:0.75rem 1rem;border-radius:0.75rem;
            background:{badge_color}22;border:1px solid {badge_color};color:{badge_color};font-weight:600;">
                Outcome: {state.outcome_status}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("Tool Call Timeline")
    timeline_cols = st.columns(len(state.tool_timeline))
    for index, item in enumerate(state.tool_timeline):
        timeline_cols[index].markdown(
            f"""
            <div style="padding:1rem;border-radius:1rem;background:#111827;border:1px solid #334155;height:180px;">
                <div style="font-size:0.8rem;color:#94a3b8;">{item.timestamp}</div>
                <div style="font-size:1rem;font-weight:700;margin:0.35rem 0;">{item.tool_name}</div>
                <div style="color:#e2e8f0;">{item.summary}</div>
                <div style="margin-top:0.75rem;color:#2dd4bf;">{item.status.title()}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_event_timeline(state.event_feed, title="Live Agent Event Feed")
    save_state(state)
