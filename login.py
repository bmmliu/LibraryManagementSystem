import streamlit as st
import hashlib
from utils import query_db

def wipe_state(state=""):
    if state in st.session_state:
        del st.session_state[state]

def login_required(func):
    def wrapper(*args, **kwargs):
        def password_entered():
            # use admin and nimda as username / password first, may check in database later
            username = st.session_state["username"].replace("'", "")
            password = hashlib.md5(st.session_state["password"].encode()).hexdigest()
            user = query_db(f"SELECT ssn FROM people WHERE username='{username}' AND password='{password}'")
            if not user.empty:
                st.session_state["logined_user"] = user.loc[0]['ssn']
            else:
                st.session_state["password_incorrect"] = True

        if "logined_user" in st.session_state:
            wipe_state("username")
            wipe_state("password")
            wipe_state("password_incorrect")

            return func(*args, **kwargs)

        if "password_incorrect" in st.session_state:
            st.error("😕 Password incorrect")

        st.markdown("# Please login to continue:")
        st.markdown("> You can use **username**: `demo` and **password**: `demo` to login:")
        st.text_input("Username", type="default", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=password_entered)

        return None

    return wrapper
