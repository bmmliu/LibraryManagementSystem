import streamlit as st

from utils import init_state, wipe_state

routers = {}

def get_path_arg(path="/"):
    if path in st.session_state["path_args"]:
        return st.session_state["path_args"][path] or {}
    return {}

def router(path=""):
    def decorator_wrapper(func):
        routers[path] = func
        return func
    return decorator_wrapper

def init():
    init_state({
        "current_path": "/",
        "path_args": {},
        "logined_user": 124123,
    })

def handle():
    init()

    current_path = "/"
    if "current_path" in st.session_state:
        current_path = st.session_state["current_path"]
    
    fn = None
    if current_path in routers:
        fn = routers[current_path]
    
    if fn:
        try:
            st.session_state["args"] = get_path_arg(current_path)
            fn()
            wipe_state("args")
        except Exception as e:
            print("Unexpected Error:", e)

def args(name="", default=""):
    if name not in st.session_state["args"]:
        return default
    return st.session_state["args"][name]

# navigate to a page, return a callback function
# you can pass in path and argument to the handler
def navigate(path="/", args={}):
    def wrapper():
        st.session_state["current_path"] = path
        st.session_state["path_args"][path] = args
    return wrapper

