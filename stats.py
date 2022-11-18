import streamlit as st

from router import router, args
from utils import query_db
from login import login_required

@router(path="/stats")
@login_required
def render():
    st.markdown("# 📈 Statistics Page")
    