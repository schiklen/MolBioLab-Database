#!/usr/bin/env python3
"""Convert plasmids.csv to SQL INSERT statements."""

import csv
import sys
from pathlib import Path

def csv_to_sql():
    csv_file = Path(__file__).parent / "plasmids.csv"
    sql_file = Path(__file__).parent / "plasmids.sql"
    
    if not csv_file.exists():
        print(f"Error: {csv_file} not found", file=sys.stderr)
        return False
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            with open(sql_file, 'w', encoding='utf-8') as sql_out:
                for row in reader:
                    # Handle NULL values
                    plasmid_number = row['Plasmid_Number']
                    plasmid_name = row['Plasmid_Name'].replace("'", "''")
                    dna_sequence = row['DNA_Sequence'].replace("'", "''")
                    creator = row['Creator']
                    date_of_creation = f"'{row['Date_of_creation']}'" if row['Date_of_creation'].strip() else "NULL"
                    comments = f"'{row['Comments'].replace(chr(39), chr(39)*2)}'" if row['Comments'].strip() else "NULL"
                    
                    sql = f"INSERT INTO PLASMIDS (Plasmid_Number, Plasmid_Name, DNA_Sequence, Creator, Date_of_creation, Comments) VALUES ({plasmid_number}, '{plasmid_name}', '{dna_sequence}', {creator}, {date_of_creation}, {comments});\n"
                    sql_out.write(sql)
        
        print(f"Generated {sql_file}")
        return True
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    sys.exit(0 if csv_to_sql() else 1)
