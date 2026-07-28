
# Remove old database to start new
rm -f molbio.db

sqlite3 molbio.db < create_database.sql

# Generate SQL scripts from CSV files
python3 data/csv_to_sql_users.py
python3 data/csv_to_sql_oligos.py
python3 data/csv_to_sql_plasmids.py
python3 data/csv_to_sql_strains.py

# Populate the database with data from CSV files
sqlite3 molbio.db < data/users.sql
sqlite3 molbio.db < data/oligos.sql
sqlite3 molbio.db < data/plasmids.sql
sqlite3 molbio.db < data/strains.sql

streamlit run app.py
