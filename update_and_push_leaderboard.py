import sqlite3
from jinja2 import Environment, FileSystemLoader
import shutil
import os
from datetime import datetime

DATABASE = '../ekicker.db'
TEMPLATE = 'leaderboard_template.html'
OUTPUT_HTML = 'index.html'
PROFILE_SRC = '../static/profile_pictures'
PROFILE_DST = 'static/profile_pictures'

def get_players():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, elo_attacker, elo_defender, profile_picture,
               (elo_attacker + elo_defender) as total_elo
        FROM players
        ORDER BY total_elo DESC
    """)
    players = cursor.fetchall()
    conn.close()
    return players

def generate_html(players, updated_time):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(TEMPLATE)
    html_output = template.render(players=players, last_updated=updated_time)

    with open(OUTPUT_HTML, 'w') as file:
        file.write(html_output)

def copy_profile_pictures(players):
    os.makedirs(PROFILE_DST, exist_ok=True)
    for player in players:
        src = os.path.join(PROFILE_SRC, player[3])
        dst = os.path.join(PROFILE_DST, player[3])
        if os.path.exists(src):
            shutil.copy(src, dst)

if __name__ == "__main__":
    from datetime import datetime
    updated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("Generating leaderboard at:", updated_time)

    players = get_players()
    generate_html(players, updated_time)  # <-- Fix: Added updated_time here
    copy_profile_pictures(players)

    # Auto git commit & push
    os.system('git add .')
    os.system(f'git commit -m "Auto-update leaderboard at {updated_time}"')
    os.system('git push origin main')
