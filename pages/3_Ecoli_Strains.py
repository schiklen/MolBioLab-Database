import sqlite3
from datetime import date

import pandas as pd
import streamlit as st

from db_utils import add_ecoli_strain, get_connection, initialize_database, read_df, get_lookup_options, update_record

st.title("_E. coli_ Strains")

conn = get_connection()
initialize_database(conn)

st.subheader("Current _E. coli_ Strains")
df_full = read_df(conn, """
    SELECT e.*, u.Shortcut 
    FROM ECOLI_STRAINS e 
    LEFT JOIN USERS u ON e.Creator = u.User_ID 
    ORDER BY Ecoli_Strain_Key DESC
""")
df = df_full.copy()
df = df.drop('Creator', axis=1)  # Drop Creator ID
df = df.rename(columns={'Shortcut': 'Creator'})  # Rename Shortcut to Creator
df_display = df.iloc[:, 1:]  # Hide first column (Ecoli_Strain_Key)
st.dataframe(df_display, use_container_width=True, hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
    key="strain_dataframe")

st.divider()

# Initialize session state for tracking updates
if "strain_update_mode" not in st.session_state:
    st.session_state.strain_update_mode = False

# Check if a row is selected and update_mode is off
if hasattr(st.session_state, 'strain_dataframe') and st.session_state.strain_dataframe['selection']['rows'] and not st.session_state.strain_update_mode:
    st.session_state.strain_update_mode = True

if st.session_state.strain_update_mode and hasattr(st.session_state, 'strain_dataframe') and st.session_state.strain_dataframe['selection']['rows']:
    selected_idx = st.session_state.strain_dataframe['selection']['rows'][0]
    selected_row = df.iloc[selected_idx]
    strain_key = int(selected_row['Ecoli_Strain_Key'])  # Convert to Python int
    
    st.subheader("Update _E. coli_ Strain")
    creators = get_lookup_options(conn, "USERS", "User_ID", ["Name"])
    strains = get_lookup_options(conn, "ECOLI_STRAINS", "Ecoli_Strain_Key", ["Ecoli_Strain_Number", "Ecoli_Strain_Name"])
    
    with st.form("update_strain"):
        strain_number = st.number_input("Strain Number", value=int(selected_row['Ecoli_Strain_Number']), min_value=1, step=1)
        strain_name = st.text_input("Strain Name", value=selected_row['Ecoli_Strain_Name'] if selected_row['Ecoli_Strain_Name'] else "")
        parent_id = selected_row['Parent']
        parent_index = 0
        if pd.notna(parent_id):
            try:
                parent_index = next(i for i, (pid, _) in enumerate(strains) if pid == int(parent_id)) + 1
            except StopIteration:
                parent_index = 0
        parent = st.selectbox("Parent strain", [(None, "None")] + strains, format_func=lambda x: x[1], index=parent_index)[0]
        genotype = st.text_area("Genotype", value=selected_row['Genotype'] if selected_row['Genotype'] else "")
        creator_id = int(df_full.iloc[selected_idx]['Creator'])  # Convert to Python int
        creator = st.selectbox("Creator", creators, format_func=lambda x: x[1], index=next(i for i, (cid, _) in enumerate(creators) if cid == creator_id))[0]
        created = st.date_input("Date of creation", value=pd.to_datetime(selected_row['Date_of_creation']).date() if selected_row['Date_of_creation'] else date.today(), key="strain_date")
        comments = st.text_area("Comments", value=selected_row['Comments'] if selected_row['Comments'] else "", key="strain_comments")
        submitted = st.form_submit_button("Update Strain")
        if submitted:
            update_record(
                conn,
                "ECOLI_STRAINS",
                "Ecoli_Strain_Key",
                strain_key,
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
            st.success("Strain updated.")
            # Reset update mode to show Add form on next render
            st.session_state.strain_update_mode = False
            st.rerun()
    
    # Delete button
    col1, col2 = st.columns([1, 10])
    with col1:
        if st.button("🗑️ Delete", key=f"delete_strain_{strain_key}"):
            # Initialize confirmation state
            if "delete_strain_confirm" not in st.session_state:
                st.session_state.delete_strain_confirm = False
            st.session_state.delete_strain_confirm = True
    
    # Show confirmation dialog
    if st.session_state.get("delete_strain_confirm", False):
        st.warning(f"⚠️ Are you sure you want to delete this strain? (Strain #{int(selected_row['Ecoli_Strain_Number'])} - {selected_row['Ecoli_Strain_Name']})")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✓ Yes, Delete", key=f"confirm_delete_strain_{strain_key}"):
                try:
                    conn.execute("DELETE FROM ECOLI_STRAINS WHERE Ecoli_Strain_Key = ?", (strain_key,))
                    conn.commit()
                    st.success("Strain deleted successfully!")
                    st.session_state.strain_update_mode = False
                    st.session_state.delete_strain_confirm = False
                    st.rerun()
                except sqlite3.IntegrityError as e:
                    st.error(f"Cannot delete: {e}")
                    st.session_state.delete_strain_confirm = False
        with col2:
            if st.button("✗ Cancel", key=f"cancel_delete_strain_{strain_key}"):
                st.session_state.delete_strain_confirm = False
                st.rerun()
else:
    try:
        add_ecoli_strain(conn)
    except sqlite3.IntegrityError as exc:
        st.error(f"Database constraint error: {exc}")
