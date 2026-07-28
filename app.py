import streamlit as st

from db_utils import get_connection, initialize_database

st.set_page_config(page_title="Lab DB", layout="wide")


def show_home() -> None:
	st.title("Home")
	conn = get_connection()
	initialize_database(conn)
	st.write("Welcome to the Labdatabase.")
	st.markdown("""
This is a simple Molecular Biology Lab database application built with Streamlit and SQLite.
			 """)
	st.subheader("Page Overview")
	st.markdown(
		"""
| Page | Description |
| --- | --- |
| Home | Landing page with project overview and navigation help. |
| Users | Manage lab users and creator entries. |
| Oligos | View and add oligo (primer) records. |
| Plasmids | View and add plasmid records. |
| _E. coli_ Strains | View and add _E. coli_ strain records. |
| Cellbanks | View and add cellbank entries linked to strains and users. |
"""
	)

navigation = st.navigation(
	[
		st.Page(show_home, title="Home"),
		st.Page("pages/0_Users.py", title="Users"),
		st.Page("pages/1_Oligos.py", title="Oligos"),
		st.Page("pages/2_Plasmids.py", title="Plasmids"),
		st.Page("pages/3_Ecoli_Strains.py", title="*E. coli* Strains"),
		st.Page("pages/4_Cellbanks.py", title="Cellbanks"),
	]
)

navigation.run()
