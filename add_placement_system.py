import sqlite3

DATABASE = 'ekicker.db'

def add_games_played_column():
    """Add games_played column to players table for placement system."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(players)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'games_played' not in columns:
            # Add the column
            cursor.execute("ALTER TABLE players ADD COLUMN games_played INTEGER DEFAULT 0")
            conn.commit()
            print("✓ Added games_played column to players table")
        else:
            print("✓ games_played column already exists")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_games_played_column()
