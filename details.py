import streamlit as st

from router import router
from utils import query_db
from login import login_required

@router(path="/details")
@login_required
def render():
    st.markdown("# Book Details")
    st.markdown("This is details page.")
    st.write("Args: id=" + st.session_state["args"]["id"])


if __name__ == "__main__":
    render()