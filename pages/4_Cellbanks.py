import sqlite3

import streamlit as st

from db_utils import add_cellbank, get_connection, initialize_database, read_df

st.title("Cellbanks")

conn = get_connection()
initialize_database(conn)

st.subheader("Current Cellbanks")
st.dataframe(read_df(conn, "SELECT * FROM CELLBANKS ORDER BY Cellbank_Key DESC"), use_container_width=True)

st.divider()

try:
    add_cellbank(conn)
except sqlite3.IntegrityError as exc:
    st.error(f"Database constraint error: {exc}")
