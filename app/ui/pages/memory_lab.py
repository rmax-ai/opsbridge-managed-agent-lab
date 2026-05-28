"""Memory lab page for store browsing and dream adoption flows."""

from __future__ import annotations

import streamlit as st

from app.ui.components.artifact_viewer import render_markdown_artifact
from app.ui.mock_data import MemoryStore, get_state, save_state


def _adopt_version(store_name: str, version: str) -> None:
    """Promote a dream candidate into the operator learnings store."""
    state = get_state()
    stores: list[MemoryStore] = []
    for store in state.memory_stores:
        if store.name == store_name and store.mode == "read-write":
            updated_entries = [
                entry.model_copy(update={"summary": f"{entry.summary} (adopted)"})
                if entry.version == version
                else entry
                for entry in store.entries
            ]
            stores.append(store.model_copy(update={"entries": updated_entries}))
        else:
            stores.append(store)
    state.memory_stores = stores
    save_state(state)


def _discard_version(store_name: str, version: str) -> None:
    """Discard a dream candidate from a writable store."""
    state = get_state()
    stores: list[MemoryStore] = []
    for store in state.memory_stores:
        if store.name == store_name and store.mode == "read-write":
            updated_entries = [entry for entry in store.entries if entry.version != version]
            stores.append(store.model_copy(update={"entries": updated_entries}))
        else:
            stores.append(store)
    state.memory_stores = stores
    save_state(state)


def render() -> None:
    """Render the memory lab page."""
    state = get_state()
    st.title("Memory Lab")
    st.caption(
        "Browse read-only reference memory, inspect writable learnings, and evaluate dream candidates."
    )

    dream_cols = st.columns(3)
    dream_cols[0].metric("Stores", str(len(state.memory_stores)))
    dream_cols[1].metric(
        "Writable Stores", str(sum(store.mode == "read-write" for store in state.memory_stores))
    )
    dream_cols[2].button("Run Dream Synthesis", type="primary")

    selected_store_name = st.selectbox(
        "Memory store", options=[store.name for store in state.memory_stores]
    )
    selected_store = next(
        store for store in state.memory_stores if store.name == selected_store_name
    )

    with st.container(border=True):
        left_col, right_col = st.columns([2, 1])
        left_col.markdown(f"**Mode:** {selected_store.mode}")
        left_col.write(selected_store.description)
        right_col.metric("Versions", str(len(selected_store.entries)))

    selected_version_id = st.selectbox(
        "Version",
        options=[entry.version for entry in selected_store.entries],
    )
    selected_version = next(
        entry for entry in selected_store.entries if entry.version == selected_version_id
    )

    render_markdown_artifact(
        "Before / After Diff",
        "\n".join(
            [
                f"**Summary:** {selected_version.summary}",
                f"**Created:** {selected_version.created_at}",
                "",
                "```diff",
                f"- {selected_version.content_before}",
                f"+ {selected_version.content_after}",
                "```",
            ]
        ),
    )

    if selected_store.mode == "read-write":
        action_cols = st.columns(2)
        action_cols[0].button(
            "Adopt",
            type="primary",
            on_click=_adopt_version,
            args=(selected_store.name, selected_version.version),
        )
        action_cols[1].button(
            "Discard",
            on_click=_discard_version,
            args=(selected_store.name, selected_version.version),
        )
