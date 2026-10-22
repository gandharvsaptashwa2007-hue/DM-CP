"""Small shared playback controls for the new learning modules."""

import streamlit as st


def set_position(key: str, value: int) -> None:
    st.session_state[key] = value


def playback(prefix: str, count: int, noun: str = "Step") -> int:
    """Render bounded controls for a nonempty trace; return its current index."""
    key = f"{prefix}_position"
    st.session_state.setdefault(key, 0)
    position = min(st.session_state[key], count - 1)
    st.progress((position + 1) / count, text=f"{noun} {position + 1} of {count}")
    cols = st.columns(4)
    for col, name, suffix, target, disabled in (
        (cols[0], "Previous", "previous", position - 1, position == 0),
        (cols[1], "Next step", "next", position + 1, position == count - 1),
        (cols[2], "Show all steps", "show_all", count - 1, False),
        (cols[3], "Start over", "restart", 0, False),
    ):
        col.button(name, key=f"{prefix}_{suffix}", on_click=set_position,
                   args=(key, target), disabled=disabled)
    return position
