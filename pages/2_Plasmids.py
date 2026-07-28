import sqlite3
from datetime import date

import pandas as pd
import streamlit as st

from db_utils import add_plasmid, get_connection, initialize_database, read_df, get_lookup_options, update_record

st.title("Plasmids")

conn = get_connection()
initialize_database(conn)

st.subheader("Current Plasmids")
df_full = read_df(conn, """
    SELECT p.*, u.Shortcut 
    FROM PLASMIDS p 
    LEFT JOIN USERS u ON p.Creator = u.User_ID 
    ORDER BY Plasmid_Key DESC
""")
df = df_full.copy()
df = df.drop('Creator', axis=1)  # Drop Creator ID
df = df.rename(columns={'Shortcut': 'Creator'})  # Rename Shortcut to Creator
df_display = df.iloc[:, 1:]  # Hide first column (Plasmid_Key)
st.dataframe(df_display, use_container_width=True, hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
    key="plasmid_dataframe")

st.divider()

# Initialize session state for tracking updates
if "update_mode" not in st.session_state:
    st.session_state.update_mode = False

# Check if a row is selected and update_mode is off
if hasattr(st.session_state, 'plasmid_dataframe') and st.session_state.plasmid_dataframe['selection']['rows'] and not st.session_state.update_mode:
    st.session_state.update_mode = True

if st.session_state.update_mode and hasattr(st.session_state, 'plasmid_dataframe') and st.session_state.plasmid_dataframe['selection']['rows']:
    selected_idx = st.session_state.plasmid_dataframe['selection']['rows'][0]
    selected_row = df.iloc[selected_idx]
    plasmid_key = int(selected_row['Plasmid_Key'])  # Convert to Python int
    
    st.subheader("Update Plasmid")
    creators = get_lookup_options(conn, "USERS", "User_ID", ["Name"])
    
    with st.form("update_plasmid"):
        plasmid_number = st.number_input("Plasmid Number", value=int(selected_row['Plasmid_Number']), min_value=1, step=1)
        plasmid_name = st.text_input("Plasmid Name", value=selected_row['Plasmid_Name'])
        dna_sequence = st.text_area("DNA Sequence", value=selected_row['DNA_Sequence'])
        creator_id = int(df_full.iloc[selected_idx]['Creator'])  # Convert to Python int
        creator = st.selectbox("Creator", creators, format_func=lambda x: x[1], index=next(i for i, (cid, _) in enumerate(creators) if cid == creator_id))[0]
        created = st.date_input("Date of creation", value=pd.to_datetime(selected_row['Date_of_creation']).date() if selected_row['Date_of_creation'] else date.today(), key="plasmid_date")
        comments = st.text_area("Comments", value=selected_row['Comments'] if selected_row['Comments'] else "", key="plasmid_comments")
        submitted = st.form_submit_button("Update Plasmid")
        if submitted:
            if not plasmid_name.strip() or not dna_sequence.strip():
                st.error("Plasmid name and sequence are required.")
            else:
                update_record(
                    conn,
                    "PLASMIDS",
                    "Plasmid_Key",
                    plasmid_key,
                    {
                        "Plasmid_Number": int(plasmid_number),
                        "Plasmid_Name": plasmid_name.strip(),
                        "DNA_Sequence": dna_sequence.strip(),
                        "Creator": int(creator),
                        "Date_of_creation": created.isoformat(),
                        "Comments": comments.strip() or None,
                    },
                )
                st.success("Plasmid updated.")
                # Reset update mode to show Add form on next render
                st.session_state.update_mode = False
                st.rerun()
else:
    try:
        add_plasmid(conn)
    except sqlite3.IntegrityError as exc:
        st.error(f"Database constraint error: {exc}")
