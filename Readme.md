# Molecular Biology Lab Database

A lightweight database for Microbial Molecular Biology labs based on SQLite and its browser-based user interface Python streamlit

## Concept
Molecular biology requires the clear knowledge of whats in the tube, in particular because oligonucleotides, plasmids and bacterial strains usually cannot be distiguished by eye.

This database is an infrastructure for collecting structured information about the oligonucleotides, plasmids, strains and cell bank collections of a lab, including the relations of the different components.

Generally, the workflow in strain engineering starts with oligonucleotides, with which DNA fragments can be generated (e. g. by PCR) which are then used to manipulate a plasmid. The newly generated plasmid is then used to generate a new strain by transforming a previously generated strain. Out of this new strain, a cell bank is generated that can serve as seed for reproducible experiments like fermentation development to optimize expression.

Oligonucleotide(s) -> Plasmid construct -> Strain

In addition, oligonucleotodes can directly serve as donor DNA for genome editing (e. g. Mund et al. 2023), in which case a direct link between oligonucleotide and strain is established.


## Use

The foundation of the database is the USERS table, as every entry is connected to the user.
This is considered critical to be able to contact the creator of the respective item and/or track or relate to a project the lab member has pursued. Not least importantly this feature is to track who did the actual work.

Therefore, a user has to be created before an entry can be made.

### Usage principles
Each oligo, plasmid or strain gets one entry and one unique number (ID).
For Oligos, the uniqueness is connected to the sequence.

### Freezer Boxes and vial positions
The items are usually stored in freezer boxes. The current implementation supports 9 x 9 position cryo-boxes and calculates the box and position of each tube based on the unique number.
