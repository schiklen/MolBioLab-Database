import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "molbio.db"
SQL_SCHEMA_PATH = BASE_DIR / "create_database.sql"


@st.cache_resource
def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database(conn: sqlite3.Connection) -> None:
    with open(SQL_SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()


def read_df(conn: sqlite3.Connection, query: str, params: tuple = ()) -> pd.DataFrame:
    return pd.read_sql_query(query, conn, params=params)


def get_lookup_options(conn: sqlite3.Connection, table: str, key_col: str, label_cols: list[str]) -> list[tuple[int, str]]:
    cols = ", ".join([key_col] + label_cols)
    rows = conn.execute(f"SELECT {cols} FROM {table} ORDER BY {key_col}").fetchall()
    options = []
    for row in rows:
        label = " | ".join(str(row[col]) for col in label_cols if row[col] is not None)
        options.append((row[key_col], f"{row[key_col]} - {label}" if label else str(row[key_col])))
    return options


def get_next_available_number(conn: sqlite3.Connection, table: str, number_col: str) -> int:
    """Get the lowest free integer > 1 for a given table and column."""
    rows = conn.execute(f"SELECT {number_col} FROM {table} ORDER BY {number_col}").fetchall()
    used_numbers = {row[0] for row in rows if row[0] is not None}
    
    next_num = 1
    while next_num in used_numbers:
        next_num += 1
    return next_num


def insert_record(conn: sqlite3.Connection, table: str, data: dict) -> None:
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?" for _ in data])
    # Convert all values to native Python types to avoid numpy type issues
    values = tuple(int(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v for v in data.values())
    conn.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
    conn.commit()


def update_record(conn: sqlite3.Connection, table: str, key_col: str, key_val, data: dict) -> None:
    """Update a record in the database."""
    set_clause = ", ".join([f"{col} = ?" for col in data.keys()])
    # Convert all values to native Python types to avoid numpy type issues
    values = [int(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v for v in data.values()]
    values = values + [int(key_val) if isinstance(key_val, (int, float)) and not isinstance(key_val, bool) else key_val]
    query = f"UPDATE {table} SET {set_clause} WHERE {key_col} = ?"
    result = conn.execute(query, values)
    conn.commit()


def add_user(conn: sqlite3.Connection) -> None:
    st.subheader("Add User")
    with st.form("add_user"):
        name = st.text_input("Name")
        shortcut = st.text_input("Shortcut")
        ad_user = st.text_input("AD user")
        submitted = st.form_submit_button("Save User")
        if submitted:
            if not name.strip():
                st.error("Name is required.")
                return
            insert_record(
                conn,
                "USERS",
                {"Name": name.strip(), "Shortcut": shortcut.strip() or None, "Network_ID": ad_user.strip() or None},
            )
            st.success("User added.")


def add_oligo(conn: sqlite3.Connection) -> None:
    st.subheader("Add Oligo")
    creators = get_lookup_options(conn, "USERS", "User_ID", ["Name"])
    if not creators:
        st.info("Create at least one user first.")
        return

    # Get the next available oligo number
    next_oligo_number = get_next_available_number(conn, "PRIMERS", "Primer_Number")

    with st.form("add_oligo"):
        # First row: Oligo Number (1/8), Oligo Name (5/8), Creator (1/8), Date (1/8)
        col1, col2, col3, col4 = st.columns([1, 5, 1, 1])
        with col1:
            primer_number = st.number_input("Oligo Number", min_value=1, step=1, value=next_oligo_number)
        with col2:
            primer_name = st.text_input("Oligo Name")
        with col3:
            creator = st.selectbox("Creator", creators, format_func=lambda x: x[1])[0]
        with col4:
            created = st.date_input("Date of creation", value=date.today())
        
        # Additional fields
        nt_sequence = st.text_area("nt Sequence")
        comments = st.text_area("Comments")
        submitted = st.form_submit_button("Save Oligo")
        if submitted:
            if not primer_name.strip() or not nt_sequence.strip():
                st.error("Oligo name and sequence are required.")
                return
            insert_record(
                conn,
                "PRIMERS",
                {
                    "Primer_Number": int(primer_number),
                    "Primer_Name": primer_name.strip(),
                    "nt_Sequence": nt_sequence.strip(),
                    "Creator": int(creator),
                    "Date_of_creation": created.isoformat(),
                    "Comments": comments.strip() or None,
                },
            )
            st.success("Oligo added.")


def add_plasmid(conn: sqlite3.Connection) -> None:
    st.subheader("Add Plasmid")
    creators = get_lookup_options(conn, "USERS", "User_ID", ["Name"])
    if not creators:
        st.info("Create at least one user first.")
        return

    # Get the next available plasmid number
    next_plasmid_number = get_next_available_number(conn, "PLASMIDS", "Plasmid_Number")

    with st.form("add_plasmid"):
        plasmid_number = st.number_input("Plasmid Number", min_value=1, step=1, value=next_plasmid_number)
        plasmid_name = st.text_input("Plasmid Name")
        dna_sequence = st.text_area("DNA Sequence")
        creator = st.selectbox("Creator", creators, format_func=lambda x: x[1])[0]
        created = st.date_input("Date of creation", value=date.today(), key="plasmid_date")
        comments = st.text_area("Comments", key="plasmid_comments")
        submitted = st.form_submit_button("Save Plasmid")
        if submitted:
            if not plasmid_name.strip() or not dna_sequence.strip():
                st.error("Plasmid name and sequence are required.")
                return
            insert_record(
                conn,
                "PLASMIDS",
                {
                    "Plasmid_Number": int(plasmid_number),
                    "Plasmid_Name": plasmid_name.strip(),
                    "DNA_Sequence": dna_sequence.strip(),
                    "Creator": int(creator),
                    "Date_of_creation": created.isoformat(),
                    "Comments": comments.strip() or None,
                },
            )
            st.success("Plasmid added.")


def add_ecoli_strain(conn: sqlite3.Connection) -> None:
    st.subheader("Add E. coli Strain")
    creators = get_lookup_options(conn, "USERS", "User_ID", ["Name"])
    strains = get_lookup_options(conn, "ECOLI_STRAINS", "Ecoli_Strain_Key", ["Ecoli_Strain_Number", "Ecoli_Strain_Name"])
    if not creators:
        st.info("Create at least one user first.")
        return

    # Get the next available strain number
    next_strain_number = get_next_available_number(conn, "ECOLI_STRAINS", "Ecoli_Strain_Number")

    with st.form("add_strain"):
        strain_number = st.number_input("Strain Number", min_value=1, step=1, value=next_strain_number)
        strain_name = st.text_input("Strain Name")
        parent = st.selectbox("Parent strain", [(None, "None")] + strains, format_func=lambda x: x[1])[0]
        genotype = st.text_area("Genotype")
        creator = st.selectbox("Creator", creators, format_func=lambda x: x[1])[0]
        created = st.date_input("Date of creation", value=date.today(), key="strain_date")
        comments = st.text_area("Comments", key="strain_comments")
        submitted = st.form_submit_button("Save Strain")
        if submitted:
            insert_record(
                conn,
                "ECOLI_STRAINS",
                {
                    "Ecoli_Strain_Number": int(strain_number),
                    "Parent": parent,
                    "Ecoli_Strain_Name": strain_name.strip() or None,
                    "Genotype": genotype.strip() or None,
                    "Creator": int(creator),
                    "Date_of_creation": created.isoformat(),
                    "Comments": comments.strip() or None,
                },
            )
            st.success("Strain added.")


def add_cellbank(conn: sqlite3.Connection) -> None:
    st.subheader("Add Cellbank")
    strains = get_lookup_options(conn, "ECOLI_STRAINS", "Ecoli_Strain_Key", ["Ecoli_Strain_Number", "Ecoli_Strain_Name"])
    creators = get_lookup_options(conn, "USERS", "User_ID", ["Name"])

    if not strains or not creators:
        st.info("Create users and strains first.")
        return

    with st.form("add_cellbank"):
        strain = st.selectbox("Strain", strains, format_func=lambda x: x[1])[0]
        creator = st.selectbox("Creator", creators, format_func=lambda x: x[1])[0]
        created = st.date_input("Date of creation", value=date.today(), key="cellbank_date")
        submitted = st.form_submit_button("Save Cellbank")
        if submitted:
            insert_record(
                conn,
                "CELLBANKS",
                {
                    "Strain": int(strain),
                    "Creator": int(creator),
                    "Date_of_creation": created.isoformat(),
                },
            )
            st.success("Cellbank added.")
