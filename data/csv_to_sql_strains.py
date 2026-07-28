#!/usr/bin/env python3
"""Convert strains.csv to SQL INSERT statements."""

import csv
import sys
from pathlib import Path

def csv_to_sql():
    csv_file = Path(__file__).parent / "strains.csv"
    sql_file = Path(__file__).parent / "strains.sql"
    
    if not csv_file.exists():
        print(f"Error: {csv_file} not found", file=sys.stderr)
        return False
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            with open(sql_file, 'w', encoding='utf-8') as sql_out:
                for row in reader:
                    # Handle NULL values
                    ecoli_strain_number = row['Ecoli_Strain_Number']
                    parent = f"{row['Parent']}" if row['Parent'].strip() else "NULL"
                    ecoli_strain_name = row['Ecoli_Strain_Name'].replace("'", "''")
                    genotype = row['Genotype'].replace("'", "''") if row['Genotype'].strip() else ""
                    genotype_value = f"'{genotype}'" if genotype else "NULL"
                    creator = row['Creator']
                    date_of_creation = f"'{row['Date_of_creation']}'" if row['Date_of_creation'].strip() else "NULL"
                    comments = f"'{row['Comments'].replace(chr(39), chr(39)*2)}'" if row['Comments'].strip() else "NULL"
                    
                    sql = f"INSERT INTO ECOLI_STRAINS (Ecoli_Strain_Number, Parent, Ecoli_Strain_Name, Genotype, Creator, Date_of_creation, Comments) VALUES ({ecoli_strain_number}, {parent}, '{ecoli_strain_name}', {genotype_value}, {creator}, {date_of_creation}, {comments});\n"
                    sql_out.write(sql)
        
        print(f"Generated {sql_file}")
        return True
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    sys.exit(0 if csv_to_sql() else 1)
