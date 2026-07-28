#!/usr/bin/env python3
"""Convert users.csv to SQL INSERT statements."""

import csv
import sys
from pathlib import Path

def csv_to_sql():
    csv_file = Path(__file__).parent / "users.csv"
    sql_file = Path(__file__).parent / "users.sql"
    
    if not csv_file.exists():
        print(f"Error: {csv_file} not found", file=sys.stderr)
        return False
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            with open(sql_file, 'w', encoding='utf-8') as sql_out:
                for row in reader:
                    # Handle NULL values
                    user_id = row['User_ID']
                    name = row['Name'].replace("'", "''")  # Escape single quotes
                    shortcut = f"'{row['Shortcut'].replace(chr(39), chr(39)*2)}'" if row['Shortcut'].strip() else "NULL"
                    network_id = f"'{row['Network_ID'].replace(chr(39), chr(39)*2)}'" if row['Network_ID'].strip() else "NULL"
                    
                    sql = f"INSERT INTO USERS (User_ID, Name, Shortcut, Network_ID) VALUES ({user_id}, '{name}', {shortcut}, {network_id});\n"
                    sql_out.write(sql)
        
        print(f"Generated {sql_file}")
        return True
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    sys.exit(0 if csv_to_sql() else 1)
