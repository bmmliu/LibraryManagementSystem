import streamlit as st

from router import router, navigate
from login import login_required

@router(path="/")
def render():
    # only for demo purpose
    import demo
    st.button("Go to Demo Page", on_click=navigate(path="/demo", args={ "id": "A-Demo-ID" }))

    st.markdown("# This is the book searching page.")
    st.button("Go to Statstics Page", on_click=navigate(path="/stats"))
    st.button(f"Read More About Book: Test Book 1", on_click=navigate(path="/details", args={ "isbn": "9781612681122" }))

if __name__ == "__main__":
    render()
