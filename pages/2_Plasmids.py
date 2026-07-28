import sqlite3

import streamlit as st

from db_utils import add_plasmid, get_connection, initialize_database, read_df

st.title("Plasmids")

conn = get_connection()
initialize_database(conn)

st.subheader("Current Plasmids")
df = read_df(conn, """
    SELECT p.*, u.Shortcut 
    FROM PLASMIDS p 
    LEFT JOIN USERS u ON p.Creator = u.User_ID 
    ORDER BY Plasmid_Key DESC
""")
df = df.drop('Creator', axis=1)  # Drop Creator ID
df = df.rename(columns={'Shortcut': 'Creator'})  # Rename Shortcut to Creator
df = df.iloc[:, 1:]  # Hide first column (Plasmid_Key)
st.dataframe(df, use_container_width=True, selection_mode="rows")

st.divider()

try:
    add_plasmid(conn)
except sqlite3.IntegrityError as exc:
    st.error(f"Database constraint error: {exc}")
