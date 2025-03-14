import sqlite3
from jinja2 import Environment, FileSystemLoader
import shutil
import os

DATABASE = '../ekicker.db'
TEMPLATE = 'leaderboard_template.html'
OUTPUT_HTML = 'index.html'
PROFILE_SRC = '../static/profile_pictures'
PROFILE_DST = 'static/profile_pictures'

def get_players():
    conn = sqlite3.connect(DATABASE)
    players = conn.execute("""
        SELECT name, elo_attacker, elo_defender, profile_picture,
               (elo_attacker + elo_defender) as total_elo
        FROM players
        ORDER BY total_elo DESC
    """).fetchall()
    conn.close()
    return players

def generate_html(players):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(TEMPLATE)
    html_output = template.render(players=players)

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
    players = get_players()
    generate_html(players)
    copy_profile_pictures(players)
    print("Public leaderboard updated.")
