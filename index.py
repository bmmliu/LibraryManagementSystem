import streamlit as st

from router import router, navigate
from utils import query_db
from login import login_required

@router(path="/")
def render():
    st.write("This is index page.")
    st.button("Go to Details Page", on_click=navigate(path="/details", args={ "id": "test" }))

if __name__ == "__main__":
    render()
