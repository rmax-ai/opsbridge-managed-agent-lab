"""Approval inbox page for governed tool confirmations."""

from __future__ import annotations

import streamlit as st

from app.ui.components.approval_card import render_approval_card
from app.ui.mock_data import ApprovalCardData, get_state, save_state


def _update_decision(approval_id: str, decision: str) -> None:
    """Persist a decision for the chosen approval item."""
    state = get_state()
    approvals: list[ApprovalCardData] = []
    for approval in state.approvals:
        if approval.id == approval_id:
            approvals.append(approval.model_copy(update={"decision": decision}))
        else:
            approvals.append(approval)
    state.approvals = approvals
    save_state(state)


def _approve(approval_id: str) -> None:
    """Approve a pending item."""
    _update_decision(approval_id, "approved")


def _deny(approval_id: str) -> None:
    """Deny a pending item."""
    _update_decision(approval_id, "denied")


def render() -> None:
    """Render the approval inbox page."""
    state = get_state()
    st.title("Approval Inbox")
    st.caption("Review governed write actions before the managed agent can proceed.")

    pending = sum(item.decision == "pending" for item in state.approvals)
    approved = sum(item.decision == "approved" for item in state.approvals)
    denied = sum(item.decision == "denied" for item in state.approvals)

    metrics = st.columns(3)
    metrics[0].metric("Pending", str(pending))
    metrics[1].metric("Approved", str(approved))
    metrics[2].metric("Denied", str(denied))

    for approval in state.approvals:
        render_approval_card(approval, on_approve=_approve, on_deny=_deny)
