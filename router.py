import streamlit as st

from utils import init_state, wipe_state

routers = {}
routers_config = {}

def get_path_arg(path="/"):
    if path in st.session_state["path_args"]:
        return st.session_state["path_args"][path] or {}
    return {}

def router(path="", hide_back=False):
    def decorator_wrapper(func):
        routers[path] = func
        routers_config[path] = {
            "hide_back": hide_back,
        }
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
    fncfg = {}
    if current_path in routers:
        fn = routers[current_path]
        fncfg = routers_config[current_path]
    
    if fn:
        try:
            # call rendering function
            st.session_state["args"] = get_path_arg(current_path)
            try:
                fn()
            except Exception as e:
                print("Component Error:", e)

            # render back footer
            if not fncfg["hide_back"] and current_path != "/":
                st.markdown("""<hr /><style>button[kind="secondary"]:last-of-type {
                    float: right;
                }</style>""", unsafe_allow_html=True)
                st.button("🏠 Back to Home", key="bk", on_click=navigate(path="/"))
            
            # clean up
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

