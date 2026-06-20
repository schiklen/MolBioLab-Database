import sqlite3

import streamlit as st

from db_utils import add_ecoli_strain, get_connection, initialize_database, read_df

st.title("E. coli Strains")

conn = get_connection()
initialize_database(conn)

st.subheader("Current E. coli Strains")
st.dataframe(read_df(conn, "SELECT * FROM ECOLI_STRAINS ORDER BY Ecoli_Strain_Key DESC"), use_container_width=True)

st.divider()

try:
    add_ecoli_strain(conn)
except sqlite3.IntegrityError as exc:
    st.error(f"Database constraint error: {exc}")
