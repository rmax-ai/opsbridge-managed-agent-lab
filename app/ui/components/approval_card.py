"""Reusable approval card component."""

from __future__ import annotations

from typing import Callable

import streamlit as st

from app.ui.mock_data import ApprovalCardData


def render_approval_card(
    approval: ApprovalCardData,
    on_approve: Callable[[str], None],
    on_deny: Callable[[str], None],
) -> None:
    """Render a single approval request card."""
    with st.container(border=True):
        title_col, status_col = st.columns([4, 1])
        title_col.subheader(approval.action_name.title())
        status_col.metric("Rubric", approval.rubric_status.replace("_", " ").title())

        meta_col, policy_col = st.columns(2)
        meta_col.markdown(
            "\n".join(
                [
                    f"**Agent:** {approval.agent}",
                    f"**Incident:** {approval.incident_id}",
                    f"**Decision:** {approval.decision.title()}",
                ]
            )
        )
        policy_col.markdown(
            "\n".join(
                [
                    f"**Policy classification:** `{approval.policy_classification}`",
                    f"**Arguments:** `{approval.arguments}`",
                ]
            )
        )

        st.caption("Supporting evidence")
        for item in approval.supporting_evidence:
            st.write(f"- {item}")

        approve_col, deny_col = st.columns(2)
        approve_col.button(
            "Approve",
            key=f"approve-{approval.id}",
            type="primary",
            disabled=approval.decision != "pending",
            on_click=on_approve,
            args=(approval.id,),
        )
        deny_col.button(
            "Deny",
            key=f"deny-{approval.id}",
            disabled=approval.decision != "pending",
            on_click=on_deny,
            args=(approval.id,),
        )
