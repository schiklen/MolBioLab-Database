import sqlite3

import streamlit as st

from db_utils import add_oligo, get_connection, initialize_database, read_df

st.title("Oligos")

conn = get_connection()
initialize_database(conn)

st.subheader("Current Oligos")
df = read_df(conn, """
    SELECT p.*, u.Shortcut 
    FROM PRIMERS p 
    LEFT JOIN USERS u ON p.Creator = u.User_ID 
    ORDER BY Primer_Key DESC
""")
df = df.drop('Creator', axis=1)  # Drop Creator ID
df = df.rename(columns={'Shortcut': 'Creator'})  # Rename Shortcut to Creator
df = df.iloc[:, 1:]  # Hide first column (Primer_Key)
st.dataframe(df, use_container_width=True, selection_mode="rows")

st.divider()

try:
    add_oligo(conn)
except sqlite3.IntegrityError as exc:
    st.error(f"Database constraint error: {exc}")
