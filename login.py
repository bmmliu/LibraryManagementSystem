import streamlit as st

def check_password():
    def password_entered():
        # use admin and nimda as username / password first, may check in database later
        if st.session_state["username"] == "admin" and st.session_state["password"] == "nimda": # check login st.session_state["password"] == st.secrets["password"]
            st.session_state["logined_user"] = 1 # some userid
        else:
            st.session_state["password_incorrect"] = True

    if "logined_user" in st.session_state:
        del st.session_state["username"]
        del st.session_state["password"]
        del st.session_state["password_incorrect"]
        return st.session_state["logined_user"]

    if "password_incorrect" in st.session_state:
        st.error("😕 Password incorrect")

    st.text_input("Username", type="default", key="username")
    st.text_input("Password", type="password", key="password")
    st.button("Login", on_click=password_entered)

    return None
