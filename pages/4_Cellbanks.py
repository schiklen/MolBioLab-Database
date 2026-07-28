import sqlite3
from datetime import date

import pandas as pd
import streamlit as st

from db_utils import add_cellbank, get_connection, initialize_database, read_df, get_lookup_options, update_record

st.title("Cellbanks")

conn = get_connection()
initialize_database(conn)

st.subheader("Current Cellbanks")
df_full = read_df(conn, """
    SELECT c.*, u.Shortcut 
    FROM CELLBANKS c 
    LEFT JOIN USERS u ON c.Creator = u.User_ID 
    ORDER BY Cellbank_Key DESC
""")
df = df_full.copy()
df = df.drop('Creator', axis=1)  # Drop Creator ID
df = df.rename(columns={'Shortcut': 'Creator'})  # Rename Shortcut to Creator
df_display = df.iloc[:, 1:]  # Hide first column (Cellbank_Key)
st.dataframe(df_display, use_container_width=True, hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
    key="cellbank_dataframe")

st.divider()

# Initialize session state for tracking updates
if "cellbank_update_mode" not in st.session_state:
    st.session_state.cellbank_update_mode = False

# Check if a row is selected and update_mode is off
if hasattr(st.session_state, 'cellbank_dataframe') and st.session_state.cellbank_dataframe['selection']['rows'] and not st.session_state.cellbank_update_mode:
    st.session_state.cellbank_update_mode = True

if st.session_state.cellbank_update_mode and hasattr(st.session_state, 'cellbank_dataframe') and st.session_state.cellbank_dataframe['selection']['rows']:
    selected_idx = st.session_state.cellbank_dataframe['selection']['rows'][0]
    selected_row = df.iloc[selected_idx]
    cellbank_key = int(selected_row['Cellbank_Key'])  # Convert to Python int
    
    st.subheader("Update Cellbank")
    strains = get_lookup_options(conn, "ECOLI_STRAINS", "Ecoli_Strain_Key", ["Ecoli_Strain_Number", "Ecoli_Strain_Name"])
    creators = get_lookup_options(conn, "USERS", "User_ID", ["Name"])
    
    with st.form("update_cellbank"):
        strain_id = int(selected_row['Strain'])
        strain_index = next(i for i, (sid, _) in enumerate(strains) if sid == strain_id)
        strain = st.selectbox("Strain", strains, format_func=lambda x: x[1], index=strain_index)[0]
        creator_id = int(df_full.iloc[selected_idx]['Creator'])  # Convert to Python int
        creator = st.selectbox("Creator", creators, format_func=lambda x: x[1], index=next(i for i, (cid, _) in enumerate(creators) if cid == creator_id))[0]
        created = st.date_input("Date of creation", value=pd.to_datetime(selected_row['Date_of_creation']).date() if selected_row['Date_of_creation'] else date.today(), key="cellbank_date")
        submitted = st.form_submit_button("Update Cellbank")
        if submitted:
            update_record(
                conn,
                "CELLBANKS",
                "Cellbank_Key",
                cellbank_key,
                {
                    "Strain": int(strain),
                    "Creator": int(creator),
                    "Date_of_creation": created.isoformat(),
                },
            )
            st.success("Cellbank updated.")
            # Reset update mode to show Add form on next render
            st.session_state.cellbank_update_mode = False
            st.rerun()
    
    # Delete button
    col1, col2 = st.columns([1, 10])
    with col1:
        if st.button("🗑️ Delete", key=f"delete_cellbank_{cellbank_key}"):
            # Initialize confirmation state
            if "delete_cellbank_confirm" not in st.session_state:
                st.session_state.delete_cellbank_confirm = False
            st.session_state.delete_cellbank_confirm = True
    
    # Show confirmation dialog
    if st.session_state.get("delete_cellbank_confirm", False):
        st.warning(f"⚠️ Are you sure you want to delete this cellbank? (Cellbank #{int(selected_row['Cellbank_Key'])})")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✓ Yes, Delete", key=f"confirm_delete_cellbank_{cellbank_key}"):
                try:
                    conn.execute("DELETE FROM CELLBANKS WHERE Cellbank_Key = ?", (cellbank_key,))
                    conn.commit()
                    st.success("Cellbank deleted successfully!")
                    st.session_state.cellbank_update_mode = False
                    st.session_state.delete_cellbank_confirm = False
                    st.rerun()
                except sqlite3.IntegrityError as e:
                    st.error(f"Cannot delete: {e}")
                    st.session_state.delete_cellbank_confirm = False
        with col2:
            if st.button("✗ Cancel", key=f"cancel_delete_cellbank_{cellbank_key}"):
                st.session_state.delete_cellbank_confirm = False
                st.rerun()
    
    # Delete button
    col1, col2 = st.columns([1, 10])
    with col1:
        if st.button("🗑️ Delete", key=f"delete_cellbank_{cellbank_key}"):
            # Initialize confirmation state
            if "delete_cellbank_confirm" not in st.session_state:
                st.session_state.delete_cellbank_confirm = False
            st.session_state.delete_cellbank_confirm = True
    
    # Show confirmation dialog
    if st.session_state.get("delete_cellbank_confirm", False):
        st.warning(f"⚠️ Are you sure you want to delete this cellbank? (Cellbank #{int(selected_row['Cellbank_Key'])})")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✓ Yes, Delete", key=f"confirm_delete_cellbank_{cellbank_key}"):
                try:
                    conn.execute("DELETE FROM CELLBANKS WHERE Cellbank_Key = ?", (cellbank_key,))
                    conn.commit()
                    st.success("Cellbank deleted successfully!")
                    st.session_state.cellbank_update_mode = False
                    st.session_state.delete_cellbank_confirm = False
                    st.rerun()
                except sqlite3.IntegrityError as e:
                    st.error(f"Cannot delete: {e}")
                    st.session_state.delete_cellbank_confirm = False
        with col2:
            if st.button("✗ Cancel", key=f"cancel_delete_cellbank_{cellbank_key}"):
                st.session_state.delete_cellbank_confirm = False
                st.rerun()
else:
    try:
        add_cellbank(conn)
    except sqlite3.IntegrityError as exc:
        st.error(f"Database constraint error: {exc}")
