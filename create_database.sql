-- Aktivierung von Fremdschlüsseln in SQLite
PRAGMA foreign_keys = ON;

-- 1. Tabelle: USERS
CREATE TABLE IF NOT EXISTS USERS (
    User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL CHECK(length(Name) > 0),
    Shortcut TEXT,
    AD_user TEXT
);

-- 2. Tabelle: PRIMERS (Neu mit Primer_Name)
CREATE TABLE IF NOT EXISTS PRIMERS (
    Primer_Key INTEGER PRIMARY KEY AUTOINCREMENT,
    Primer_Number INTEGER NOT NULL UNIQUE,
    Primer_Name TEXT NOT NULL CHECK(length(Primer_Name) > 0),
    nt_Sequence TEXT NOT NULL, -- CHECK(nt_Sequence GLOB '*[ACGT]*' AND NOT nt_Sequence GLOB '*[^ACGT]*'),
    Creator INTEGER NOT NULL,
    Date_of_creation TEXT, -- ISO8601: YYYY-MM-DD
    Comments TEXT,
    Box INTEGER GENERATED ALWAYS AS (CAST((Primer_Number / 81) AS INT) + 1) STORED,
    Position INTEGER GENERATED ALWAYS AS ((Primer_Number % 81) + 1) STORED,
    FOREIGN KEY (Creator) REFERENCES USERS(User_ID)
);

-- 3. Tabelle: PLASMIDS (Neu mit Plasmid_Name)
CREATE TABLE IF NOT EXISTS PLASMIDS (
    Plasmid_Key INTEGER PRIMARY KEY AUTOINCREMENT,
    Plasmid_Number INTEGER NOT NULL UNIQUE,
    Plasmid_Name TEXT NOT NULL CHECK(length(Plasmid_Name) > 0),
    DNA_Sequence TEXT NOT NULL, -- CHECK(DNA_Sequence GLOB '*[ACGT]*' AND NOT DNA_Sequence GLOB '*[^ACGT]*'),
    Creator INTEGER NOT NULL,
    Date_of_creation TEXT,
    Comments TEXT,
    Box INTEGER GENERATED ALWAYS AS (CAST((Plasmid_Number / 81) AS INT) + 1) STORED,
    Position INTEGER GENERATED ALWAYS AS ((Plasmid_Number % 81) + 1) STORED,
    FOREIGN KEY (Creator) REFERENCES USERS(User_ID)
);

-- 4. Tabelle: ECOLI_STRAINS (Neu mit Ecoli_Strain_Name)
CREATE TABLE IF NOT EXISTS ECOLI_STRAINS (
    Ecoli_Strain_Key INTEGER PRIMARY KEY AUTOINCREMENT,
    Ecoli_Strain_Number INTEGER NOT NULL UNIQUE,
    Parent INTEGER,
    Ecoli_Strain_Name TEXT,
    Genotype TEXT,
    Creator INTEGER NOT NULL,
    Date_of_creation TEXT,
    Comments TEXT,
    Box INTEGER GENERATED ALWAYS AS (CAST((Ecoli_Strain_Number / 81) AS INT) + 1) STORED,
    Position INTEGER GENERATED ALWAYS AS ((Ecoli_Strain_Number % 81) + 1) STORED,
    FOREIGN KEY (Parent) REFERENCES ECOLI_STRAINS(Ecoli_Strain_Key),
    FOREIGN KEY (Creator) REFERENCES USERS(User_ID)
);

-- Junction Table für ECOLI_STRAINS <-> PLASMIDS (M:N)
CREATE TABLE IF NOT EXISTS STRAIN_PLASMIDS (
    Strain_Key INTEGER,
    Plasmid_Key INTEGER,
    PRIMARY KEY (Strain_Key, Plasmid_Key),
    FOREIGN KEY (Strain_Key) REFERENCES ECOLI_STRAINS(Ecoli_Strain_Key) ON DELETE CASCADE,
    FOREIGN KEY (Plasmid_Key) REFERENCES PLASMIDS(Plasmid_Key) ON DELETE CASCADE
);

-- 5. Tabelle: CELLBANKS
CREATE TABLE IF NOT EXISTS CELLBANKS (
    Cellbank_Key INTEGER PRIMARY KEY AUTOINCREMENT,
    Strain INTEGER NOT NULL,
    Creator INTEGER NOT NULL,
    Date_of_creation DATE,
    FOREIGN KEY (Strain) REFERENCES ECOLI_STRAINS(Ecoli_Strain_Key),
    FOREIGN KEY (Creator) REFERENCES USERS(User_ID)
);
