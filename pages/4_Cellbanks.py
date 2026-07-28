import sqlite3

import streamlit as st

from db_utils import add_cellbank, get_connection, initialize_database, read_df

st.title("Cellbanks")

conn = get_connection()
initialize_database(conn)

st.subheader("Current Cellbanks")
df = read_df(conn, """
    SELECT c.*, u.Shortcut 
    FROM CELLBANKS c 
    LEFT JOIN USERS u ON c.Creator = u.User_ID 
    ORDER BY Cellbank_Key DESC
""")
df = df.drop('Creator', axis=1)  # Drop Creator ID
df = df.rename(columns={'Shortcut': 'Creator'})  # Rename Shortcut to Creator
df = df.iloc[:, 1:]  # Hide first column (Cellbank_Key)
st.dataframe(df, use_container_width=True, hide_index=True,
    on_select="rerun",
    selection_mode="single-row")

st.divider()

try:
    add_cellbank(conn)
except sqlite3.IntegrityError as exc:
    st.error(f"Database constraint error: {exc}")
