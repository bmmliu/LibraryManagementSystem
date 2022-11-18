import streamlit as st

def wipe_state(state=""):
    if state in st.session_state:
        del st.session_state[state]

def login_required(func):
    def wrapper(*args, **kwargs):
        def password_entered():
            # use admin and nimda as username / password first, may check in database later
            print("Login Via:", st.session_state["username"], st.session_state["password"])
            if st.session_state["username"] == "admin" and st.session_state["password"] == "nimda": # check login st.session_state["password"] == st.secrets["password"]
                st.session_state["logined_user"] = 1 # some userid
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
        st.text_input("Username", type="default", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=password_entered)

        return None

    return wrapper
