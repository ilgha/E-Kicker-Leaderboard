import sqlite3
from jinja2 import Environment, FileSystemLoader
import shutil
import os
import subprocess
from datetime import datetime

DATABASE = 'ekicker.db'
TEMPLATE = 'leaderboard_template.html'
OUTPUT_HTML = 'index.html'
PROFILE_SRC = 'static/profile_pictures'
PROFILE_DST = 'static/profile_pictures'

def get_placement_stats():
    """Get statistics on player placement progress."""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM players")
        total_players = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM players WHERE games_played >= 5")
        qualified_players = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM players WHERE games_played > 0 AND games_played < 5")
        in_placement = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM players WHERE games_played = 0")
        no_games = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total': total_players,
            'qualified': qualified_players,
            'in_placement': in_placement,
            'no_games': no_games
        }
    except Exception as e:
        print(f"Error reading database: {e}")
        return None

def get_players():
    """Fetch all players from database with 5+ games, ordered by total ELO."""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, elo_attacker, elo_defender, profile_picture,
                   (elo_attacker + elo_defender) as total_elo,
                   games_played
            FROM players
            WHERE games_played >= 5
            ORDER BY total_elo DESC
        """)
        players = cursor.fetchall()
        conn.close()
        return players
    except Exception as e:
        print(f"Error reading database: {e}")
        return []

def generate_html(players, updated_time):
    """Generate HTML from template and player data."""
    try:
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template(TEMPLATE)
        html_output = template.render(players=players, last_updated=updated_time)

        # Write with UTF-8 encoding to handle emojis
        with open(OUTPUT_HTML, 'w', encoding='utf-8') as file:
            file.write(html_output)
        print(f"✓ Generated {OUTPUT_HTML}")
    except Exception as e:
        print(f"Error generating HTML: {e}")

def copy_profile_pictures(players):
    """Copy profile pictures to the GitHub Pages directory."""
    os.makedirs(PROFILE_DST, exist_ok=True)
    copied = 0
    for player in players:
        src = os.path.join(PROFILE_SRC, player[3])
        dst = os.path.join(PROFILE_DST, player[3])
        try:
            if os.path.exists(src):
                # Skip if source and destination are the same (already in place)
                if os.path.abspath(src) != os.path.abspath(dst):
                    shutil.copy(src, dst)
                    copied += 1
        except Exception as e:
            print(f"Warning: Could not copy {player[3]}: {e}")
    print(f"✓ Processed profile pictures (already in place)")

def git_push(updated_time):
    """Commit and push changes to GitHub."""
    try:
        # Check if git is available
        subprocess.run(['git', '--version'], check=True, capture_output=True)
        
        # Stage all changes
        result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Warning: git add failed: {result.stderr}")
            return False
        
        # Commit
        commit_msg = f"Auto-update leaderboard at {updated_time}"
        result = subprocess.run(['git', 'commit', '-m', commit_msg], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Warning: git commit failed: {result.stderr}")
            return False
        
        # Push
        result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Warning: git push failed: {result.stderr}")
            return False
        
        print(f"✓ Pushed to GitHub with message: {commit_msg}")
        return True
    except FileNotFoundError:
        print("Warning: Git is not installed or not in PATH")
        return False
    except Exception as e:
        print(f"Error during git operations: {e}")
        return False

if __name__ == "__main__":
    updated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("=" * 60)
    print(f"Updating leaderboard at: {updated_time}")
    print("=" * 60)

    # Show placement stats
    stats = get_placement_stats()
    if stats:
        print(f"\nPlacement System Status:")
        print(f"  Total players:     {stats['total']}")
        print(f"  Qualified (5+ games):  {stats['qualified']}")
        print(f"  In placement:          {stats['in_placement']} (need more games)")
        print(f"  Not started:           {stats['no_games']}")
        print()

    # Get players from database
    players = get_players()
    
    if not players:
        print("⚠️  No players with 5+ games found in database")
        print("   (Players need to complete 5 placement games first)")
        print()
        print("✓ Attempting to push changes anyway...")
        git_push(updated_time)
        print("=" * 60)
        print("Update complete! Public leaderboard ready when players reach 5 games.")
        print("=" * 60)
        exit(0)
    
    print(f"✓ Found {len(players)} qualified players (5+ games)")

    # Generate HTML
    generate_html(players, updated_time)
    
    # Copy profile pictures
    copy_profile_pictures(players)

    # Push to GitHub
    print()
    git_push(updated_time)
    
    print()
    print("=" * 60)
    print("Update complete!")
    print("=" * 60)

