import streamlit as st

def wipe_state(state=""):
    if state in st.session_state:
        del st.session_state[state]

routers = {}

def router(path=""):
    def decorator_wrapper(func):
        routers[path] = func
        return func
    return decorator_wrapper

def handle():
    current_path = "/"
    if "current_path" in st.session_state:
        current_path = st.session_state["current_path"]
    
    fn = None
    if current_path in routers:
        fn = routers[current_path]
    
    if fn:
        try:
            fn()
            wipe_state("args")
        except Exception:
            pass

# navigate to a page, return a callback function
# you can pass in path and argument to the handler
def navigate(path="/", args={}):
    def wrapper():
        st.session_state["current_path"] = path
        st.session_state["args"] = args
    return wrapper