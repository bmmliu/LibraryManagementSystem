import streamlit as st

from router import router, args, navigate
from utils import query_db, exec_db
from login import login_required

@router(path="/user")
@login_required
def render():
    user_ssn = st.session_state["logined_user"]
    user_first_name = st.session_state["logined_user_username"]
    user_role = st.session_state["logined_user_role"]
    title = "# 🎓 Hello " + str(user_first_name)
    st.markdown(title)

    "## Show book borrowed"
    st.markdown("### 📚 Book Borrowed")
    try:
        book_borrowed = query_db(f"SELECT b.title, b.subtitle, b.isbn, r.event_date as borrowed_date, r.lid, r.location FROM booking_records r LEFT JOIN books b ON r.isbn = b.isbn WHERE r.ssn = '{user_ssn}' AND r.ret_date IS NULL ;")
        if not book_borrowed.empty:
            st.markdown("""<style>button[kind="primary"] {
                float: right;
            }</style>""", unsafe_allow_html=True)
            for book in book_borrowed.to_dict('records'):
                st.markdown("<hr />", unsafe_allow_html=True)
                isbn = book['isbn']
                title = (book['title'] + ' ' + book['subtitle']).strip()
                date = book['borrowed_date']
                lid = book['lid']
                location = book['location']

                st.markdown(f"##### *{title}*")
                st.markdown(f"""
                    - **ISBN:** `{isbn}`
                    - **Borrowed Date:** `{date}`
                    - **Borrowed From:** `{lid}` - `{location}`
                """)
                st.button(f"Return {isbn}", type="primary", on_click=navigate(path="/details", args={ "isbn": isbn }))
        else:
            st.error("You have not borrowed any book yet.")
    except:
        st.error("You have not borrowed any book yet.")
