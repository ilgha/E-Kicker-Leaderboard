import sqlite3

DATABASE = 'ekicker.db'

def reset_season():
    """Reset all player ELO ratings to 1000 for both attacker and defender."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get total number of players before reset
    cursor.execute("SELECT COUNT(*) FROM players")
    player_count = cursor.fetchone()[0]
    
    # Reset all ELOs to 1000
    cursor.execute("UPDATE players SET elo_attacker = 1000, elo_defender = 1000")
    conn.commit()
    
    print(f"✓ Season reset complete!")
    print(f"  - Reset {player_count} players")
    print(f"  - All attacker ELOs set to 1000")
    print(f"  - All defender ELOs set to 1000")
    
    conn.close()

if __name__ == "__main__":
    reset_season()
