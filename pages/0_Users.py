import sqlite3

import streamlit as st

from db_utils import add_user, get_connection, initialize_database, read_df

st.title("Users")

conn = get_connection()
initialize_database(conn)

st.subheader("Current Users")
st.dataframe(read_df(conn, "SELECT * FROM USERS ORDER BY User_ID DESC"), use_container_width=True)

st.divider()

try:
    add_user(conn)
except sqlite3.IntegrityError as exc:
    st.error(f"Database constraint error: {exc}")
