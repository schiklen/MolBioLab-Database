import sqlite3
from datetime import date

import pandas as pd
import streamlit as st

from db_utils import add_oligo, get_connection, initialize_database, read_df, get_lookup_options, update_record

st.title("Oligos")

conn = get_connection()
initialize_database(conn)

st.subheader("Current Oligos")
df_full = read_df(conn, """
    SELECT p.*, u.Shortcut 
    FROM PRIMERS p 
    LEFT JOIN USERS u ON p.Creator = u.User_ID 
    ORDER BY Primer_Key DESC
""")
df = df_full.copy()
df = df.drop('Creator', axis=1)  # Drop Creator ID
df = df.rename(columns={'Shortcut': 'Creator'})  # Rename Shortcut to Creator
df_display = df.iloc[:, 1:]  # Hide first column (Primer_Key)
st.dataframe(df_display, use_container_width=True, hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
    key="oligo_dataframe")

st.divider()

# Initialize session state for tracking updates
if "oligo_update_mode" not in st.session_state:
    st.session_state.oligo_update_mode = False

# Check if a row is selected and update_mode is off
if hasattr(st.session_state, 'oligo_dataframe') and st.session_state.oligo_dataframe['selection']['rows'] and not st.session_state.oligo_update_mode:
    st.session_state.oligo_update_mode = True

if st.session_state.oligo_update_mode and hasattr(st.session_state, 'oligo_dataframe') and st.session_state.oligo_dataframe['selection']['rows']:
    selected_idx = st.session_state.oligo_dataframe['selection']['rows'][0]
    selected_row = df.iloc[selected_idx]
    primer_key = int(selected_row['Primer_Key'])  # Convert to Python int
    
    st.subheader("Update Oligo")
    creators = get_lookup_options(conn, "USERS", "User_ID", ["Name"])
    
    with st.form("update_oligo"):
        primer_number = st.number_input("Oligo Number", value=int(selected_row['Primer_Number']), min_value=1, step=1)
        primer_name = st.text_input("Oligo Name", value=selected_row['Primer_Name'])
        nt_sequence = st.text_area("nt Sequence", value=selected_row['nt_Sequence'])
        creator_id = int(df_full.iloc[selected_idx]['Creator'])  # Convert to Python int
        creator = st.selectbox("Creator", creators, format_func=lambda x: x[1], index=next(i for i, (cid, _) in enumerate(creators) if cid == creator_id))[0]
        created = st.date_input("Date of creation", value=pd.to_datetime(selected_row['Date_of_creation']).date() if selected_row['Date_of_creation'] else date.today(), key="oligo_date")
        comments = st.text_area("Comments", value=selected_row['Comments'] if selected_row['Comments'] else "", key="oligo_comments")
        submitted = st.form_submit_button("Update Oligo")
        if submitted:
            if not primer_name.strip() or not nt_sequence.strip():
                st.error("Oligo name and sequence are required.")
            else:
                update_record(
                    conn,
                    "PRIMERS",
                    "Primer_Key",
                    primer_key,
                    {
                        "Primer_Number": int(primer_number),
                        "Primer_Name": primer_name.strip(),
                        "nt_Sequence": nt_sequence.strip(),
                        "Creator": int(creator),
                        "Date_of_creation": created.isoformat(),
                        "Comments": comments.strip() or None,
                    },
                )
                st.success("Oligo updated.")
                # Reset update mode to show Add form on next render
                st.session_state.oligo_update_mode = False
                st.rerun()
else:
    try:
        add_oligo(conn)
    except sqlite3.IntegrityError as exc:
        st.error(f"Database constraint error: {exc}")
