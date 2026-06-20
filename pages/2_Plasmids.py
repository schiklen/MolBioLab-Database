import sqlite3

import streamlit as st

from db_utils import add_plasmid, get_connection, initialize_database, read_df

st.title("Plasmids")

conn = get_connection()
initialize_database(conn)

st.subheader("Current Plasmids")
st.dataframe(read_df(conn, "SELECT * FROM PLASMIDS ORDER BY Plasmid_Key DESC"), use_container_width=True)

st.divider()

try:
    add_plasmid(conn)
except sqlite3.IntegrityError as exc:
    st.error(f"Database constraint error: {exc}")
