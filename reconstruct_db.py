import sqlite3
import os

DATABASE = 'ekicker.db'

# Player data extracted from index.html
players_data = [
    ("Crooked", 1153, 970, "Crooked.png"),
    ("drKicker", 1017, 1072, "drKicker.png"),
    ("ChillGuy", 1000, 1069, "ChillGuy.png"),
    ("Benji", 1016, 1016, "Benji.png"),
    ("Mirage", 1026, 1000, "Mirage.png"),
    ("Rafale", 1041, 982, "Rafale.png"),
    ("Quentin", 1016, 1000, "Quentin.png"),
    ("DAntoine", 984, 1032, "DAntoine.png"),
    ("VQPh8nix", 1016, 1000, "VQPh8nix.png"),
    ("benjilanglo", 1002, 1000, "benjilanglo.png"),
    ("Princess", 1000, 1001, "Princess.png"),
    ("RedBull", 1001, 1000, "RedBull.png"),
    ("coco myrtille", 1000, 1000, "coco_myrtille.png"),
    ("Dionysaure", 1000, 1000, "Dionysaure.png"),
    ("LeTajik", 1000, 1000, "LeTajik.png"),
    ("FootFungus", 1015, 985, "FootFungus.png"),
    ("Spaced _out", 1000, 1000, "Spaced__out.png"),
    ("QH", 1000, 1000, "QH.png"),
    ("Bio gogol", 1000, 1000, "Bio_gogol.png"),
    ("Lem", 1000, 1000, "Lem.png"),
    ("BateauSinge", 1000, 1000, "BateauSinge.png"),
    ("Samuel", 1000, 1000, "Samuel.png"),
    ("Pierroqueh", 1000, 1000, "Pierroqueh.png"),
    ("Baristote", 1000, 1000, "Baristote.png"),
    ("The Reaper", 1000, 1000, "The_Reaper.png"),
    ("Le reboul", 1000, 1000, "Le_reboul.png"),
    ("Romain", 1000, 1000, "Romain.png"),
    ("Passoire", 977, 1015, "Passoire.png"),
    ("RattacheMan", 971, 1015, "RattacheMan.png"),
    ("Sylvainqueur", 972, 1012, "Sylvainqueur.png"),
    ("Marie", 984, 1000, "Marie.png"),
    ("Zumzal", 1000, 984, "Zumzal.png"),
    ("Bus", 973, 1000, "Bus.png"),
    ("Fils", 1000, 973, "Fils.png"),
    ("CaptainObvious", 1000, 967, "CaptainObvious.png"),
    ("Chesh", 950, 1000, "Chesh.png"),
    ("El Raton", 886, 907, "El_Raton.png"),
    ("?", 0, 0, "default.png"),
]

def create_database():
    """Create the database and tables."""
    # Remove old database if it exists
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
        print(f"Removed old {DATABASE}")
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create players table
    cursor.execute("""
        CREATE TABLE players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            elo_attacker INTEGER NOT NULL DEFAULT 1000,
            elo_defender INTEGER NOT NULL DEFAULT 1000,
            profile_picture TEXT NOT NULL
        )
    """)
    
    # Insert all players
    cursor.executemany("""
        INSERT INTO players (name, elo_attacker, elo_defender, profile_picture)
        VALUES (?, ?, ?, ?)
    """, players_data)
    
    conn.commit()
    conn.close()
    print(f"✓ Database {DATABASE} created successfully with {len(players_data)} players")

if __name__ == "__main__":
    create_database()
