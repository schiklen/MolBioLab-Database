import sqlite3
from datetime import date

import pandas as pd
import streamlit as st

from db_utils import add_oligo, get_connection, initialize_database, read_df, update_record, get_user_shortcuts, validate_iupac_dna

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
    creators = get_user_shortcuts(conn)
    
    with st.form("update_oligo"):
        # First row: Oligo Number (1/8), Oligo Name (5/8), Creator (1/8), Date (1/8)
        col1, col2, col3, col4 = st.columns([1, 5, 1, 1])
        with col1:
            primer_number = st.number_input("Oligo Number", value=int(selected_row['Primer_Number']), min_value=1, step=1)
        with col2:
            primer_name = st.text_input("Oligo Name", value=selected_row['Primer_Name'])
        with col3:
            creator_id = int(df_full.iloc[selected_idx]['Creator'])  # Convert to Python int
            creator = st.selectbox("Creator", creators, format_func=lambda x: x[1], index=next(i for i, (cid, _) in enumerate(creators) if cid == creator_id))[0]
        with col4:
            created = st.date_input("Date of creation", value=pd.to_datetime(selected_row['Date_of_creation']).date() if selected_row['Date_of_creation'] else date.today(), key="oligo_date")
        
        # Additional fields
        nt_sequence = st.text_input("Sequence", value=selected_row['nt_Sequence'], max_chars=120, help="IUPAC DNA characters only (A, C, G, T, U, R, Y, W, S, M, K, H, B, D, V, N)")
        comments = st.text_area("Comments", value=selected_row['Comments'] if selected_row['Comments'] else "", key="oligo_comments")
        submitted = st.form_submit_button("Update Oligo")
        if submitted:
            if not primer_name.strip() or not nt_sequence.strip():
                st.error("Oligo name and sequence are required.")
            elif not validate_iupac_dna(nt_sequence.strip()):
                st.error("Sequence contains invalid characters. Only IUPAC DNA codes allowed.")
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
    
    # Delete button
    col1, col2 = st.columns([1, 10])
    with col1:
        if st.button("🗑️ Delete", key=f"delete_oligo_{primer_key}"):
            # Initialize confirmation state
            if "delete_oligo_confirm" not in st.session_state:
                st.session_state.delete_oligo_confirm = False
            st.session_state.delete_oligo_confirm = True
    
    # Show confirmation dialog
    if st.session_state.get("delete_oligo_confirm", False):
        st.warning(f"⚠️ Are you sure you want to delete this oligo? (Oligo #{int(selected_row['Primer_Number'])} - {selected_row['Primer_Name']})")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✓ Yes, Delete", key=f"confirm_delete_oligo_{primer_key}"):
                try:
                    conn.execute("DELETE FROM PRIMERS WHERE Primer_Key = ?", (primer_key,))
                    conn.commit()
                    st.success("Oligo deleted successfully!")
                    st.session_state.oligo_update_mode = False
                    st.session_state.delete_oligo_confirm = False
                    st.rerun()
                except sqlite3.IntegrityError as e:
                    st.error(f"Cannot delete: {e}")
                    st.session_state.delete_oligo_confirm = False
        with col2:
            if st.button("✗ Cancel", key=f"cancel_delete_oligo_{primer_key}"):
                st.session_state.delete_oligo_confirm = False
                st.rerun()
else:
    try:
        add_oligo(conn)
    except sqlite3.IntegrityError as exc:
        st.error(f"Database constraint error: {exc}")
