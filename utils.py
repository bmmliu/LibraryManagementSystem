import pandas as pd
import psycopg2

from configparser import ConfigParser
import streamlit as st

def wipe_state(state=""):
    if state in st.session_state:
        del st.session_state[state]

@st.cache
def get_config(filename="local.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}

def exec_db(sql: str):
    print("Do Query:", sql)

    db_info = get_config()
    conn = psycopg2.connect(**db_info)

    cur = conn.cursor()
    cur.execute(sql)

    conn.commit()
    cur.close()
    conn.close()

def query_db(sql: str):
    print("Do Query:", sql)

    db_info = get_config()
    conn = psycopg2.connect(**db_info)

    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()

    column_names = [desc[0] for desc in cur.description]
    conn.commit()

    cur.close()
    conn.close()

    df = pd.DataFrame(data=data, columns=column_names)
    return df

def init_state(states={}):
    for k in states:
        if k not in st.session_state:
            st.session_state[k] = states[k]
