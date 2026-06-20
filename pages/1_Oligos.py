import sqlite3

import streamlit as st

from db_utils import add_oligo, get_connection, initialize_database, read_df

st.title("Oligos")

conn = get_connection()
initialize_database(conn)

st.subheader("Current Oligos")
st.dataframe(read_df(conn, "SELECT * FROM PRIMERS ORDER BY Primer_Key DESC"), use_container_width=True)

st.divider()

try:
    add_oligo(conn)
except sqlite3.IntegrityError as exc:
    st.error(f"Database constraint error: {exc}")
