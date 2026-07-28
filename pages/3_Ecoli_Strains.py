import sqlite3

import streamlit as st

from db_utils import add_ecoli_strain, get_connection, initialize_database, read_df

st.title("_E. coli_ Strains")

conn = get_connection()
initialize_database(conn)

st.subheader("Current _E. coli_ Strains")
df = read_df(conn, """
    SELECT e.*, u.Shortcut 
    FROM ECOLI_STRAINS e 
    LEFT JOIN USERS u ON e.Creator = u.User_ID 
    ORDER BY Ecoli_Strain_Key DESC
""")
df = df.drop('Creator', axis=1)  # Drop Creator ID
df = df.rename(columns={'Shortcut': 'Creator'})  # Rename Shortcut to Creator
df = df.iloc[:, 1:]  # Hide first column (Ecoli_Strain_Key)
st.dataframe(df, use_container_width=True, selection_mode="rows")

st.divider()

try:
    add_ecoli_strain(conn)
except sqlite3.IntegrityError as exc:
    st.error(f"Database constraint error: {exc}")
