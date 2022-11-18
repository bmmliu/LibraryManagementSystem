import pandas as pd
import psycopg2

import streamlit as st

@st.cache
def get_config(filename="local.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}

@st.cache
def query_db(sql: str):
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