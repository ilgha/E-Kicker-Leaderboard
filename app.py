from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import sqlite3
import os
from PIL import Image

app = Flask(__name__)
DATABASE = 'ekicker.db'
K = 32  # ELO adjustment factor
OBS_DIRECTORY = 'obs_data'  # Directory to store text files for OBS

# PLACEMENT SYSTEM: Players must play 5 games before appearing on public leaderboard
# - ELO is updated from the first game
# - Flask app shows all players with placement status
# - Public GitHub leaderboard only shows players with 5+ games

# Initialize a dictionary to store current players' data for the website display
current_players_display = {}

# Initialize a dictionary to store current players' data for the website display with default values
current_players_display = {
    'team1_attacker': ('Unknown', 'N/A'),
    'team1_defender': ('Unknown', 'N/A'),
    'team2_attacker': ('Unknown', 'N/A'),
    'team2_defender': ('Unknown', 'N/A'),
}

UPLOAD_FOLDER = 'static/profile_pictures'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize scores
current_score = {'team1': 0, 'team2': 0}

# Ensure the profile pictures folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Ensure OBS directory exists
if not os.path.exists(OBS_DIRECTORY):
    os.makedirs(OBS_DIRECTORY)

def connect_db():
    conn = sqlite3.connect(DATABASE)
    return conn

def calculate_expected_score(team_elo, opponent_team_elo):
    """Calculate the expected score for a team based on ELOs."""
    return 1 / (1 + 10 ** ((opponent_team_elo - team_elo) / 400))

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(input_path, output_path, width, height):
    """Resize an image to the specified dimensions."""
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            # Resize the image
            resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
            resized_img.save(output_path, 'PNG', quality=95)
    except Exception as e:
        print(f"Error resizing image from {input_path} to {output_path}: {str(e)}")
        raise

@app.route('/')
def index():
    conn = connect_db()
    cursor = conn.cursor()
    # Select players ordered by the sum of elo_attacker and elo_defender in descending order
    # Column order: id, name, total_elo, elo_attacker, elo_defender, profile_picture, games_played
    cursor.execute("SELECT id, name, (elo_attacker + elo_defender), elo_attacker, elo_defender, profile_picture, games_played FROM players ORDER BY (elo_attacker + elo_defender) DESC")
    players = cursor.fetchall()
    conn.close()
    return render_template('index.html', players=players, current_players=current_players_display, current_score=current_score)

@app.route('/add_player', methods=['POST'])
def add_player():
    name = request.form['name']
    file = request.files['profile_picture']

    if not file or file.filename == '':
        return 'Profile picture is required', 400

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{name}.png")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO players (name, elo_attacker, elo_defender, profile_picture) VALUES (?, 1000, 1000, ?)",
            (name, filename)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('index'))
    return 'Invalid file format', 400


@app.route('/record_match', methods=['POST'])
def record_match():
    """Record match result using the current selected players."""
    # Check if current players have been set
    if not all(isinstance(v, tuple) and len(v) == 4 for v in current_players_display.values()):
        return 'Please set current players first', 400
    
    try:
        # Retrieve team and result data from current players
        team1_attacker_id = current_players_display['team1_attacker'][3]  # ID is now at index 3
        team1_defender_id = current_players_display['team1_defender'][3]
        team2_attacker_id = current_players_display['team2_attacker'][3]
        team2_defender_id = current_players_display['team2_defender'][3]
        result = float(request.form['result'])  # 1 if Team RED wins, 0 if Team BLUE wins, 0.5 for draw

        conn = connect_db()
        cursor = conn.cursor()

        # Retrieve the ELOs for each player in their respective roles
        cursor.execute("SELECT elo_attacker FROM players WHERE id = ?", (team1_attacker_id,))
        team1_attacker_elo = cursor.fetchone()[0]
        cursor.execute("SELECT elo_defender FROM players WHERE id = ?", (team1_defender_id,))
        team1_defender_elo = cursor.fetchone()[0]
        cursor.execute("SELECT elo_attacker FROM players WHERE id = ?", (team2_attacker_id,))
        team2_attacker_elo = cursor.fetchone()[0]
        cursor.execute("SELECT elo_defender FROM players WHERE id = ?", (team2_defender_id,))
        team2_defender_elo = cursor.fetchone()[0]

        # Calculate each team's average ELO
        team1_elo = (team1_attacker_elo + team1_defender_elo) / 2
        team2_elo = (team2_attacker_elo + team2_defender_elo) / 2

        # Calculate expected score for each team based on the team average ELOs
        team1_expected_score = calculate_expected_score(team1_elo, team2_elo)
        team2_expected_score = calculate_expected_score(team2_elo, team1_elo)

        # Adjust ELOs for each player in their respective roles
        if result == 1:  # Team RED wins
            team1_score, team2_score = 1, 0
        elif result == 0:  # Team BLUE wins
            team1_score, team2_score = 0, 1
        else:  # Draw
            team1_score, team2_score = 0.5, 0.5

        # Update ELO for each player based on team outcome
        team1_attacker_new_elo = round(team1_attacker_elo + K * (team1_score - team1_expected_score))
        team1_defender_new_elo = round(team1_defender_elo + K * (team1_score - team1_expected_score))
        team2_attacker_new_elo = round(team2_attacker_elo + K * (team2_score - team2_expected_score))
        team2_defender_new_elo = round(team2_defender_elo + K * (team2_score - team2_expected_score))

        # Update database with new ELOs and increment games_played
        cursor.execute("UPDATE players SET elo_attacker = ?, games_played = games_played + 1 WHERE id = ?", (team1_attacker_new_elo, team1_attacker_id))
        cursor.execute("UPDATE players SET elo_defender = ?, games_played = games_played + 1 WHERE id = ?", (team1_defender_new_elo, team1_defender_id))
        cursor.execute("UPDATE players SET elo_attacker = ?, games_played = games_played + 1 WHERE id = ?", (team2_attacker_new_elo, team2_attacker_id))
        cursor.execute("UPDATE players SET elo_defender = ?, games_played = games_played + 1 WHERE id = ?", (team2_defender_new_elo, team2_defender_id))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))
    except Exception as e:
        return f'Error recording match: {str(e)}', 500


@app.route('/remove_player', methods=['POST'])
def remove_player():
    player_id = request.form['player_id']
    
    # Connect to the database and delete the player
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/set_current_players', methods=['POST'])
def set_current_players():
    """Set current players and save their names, ELOs, and profile pictures for OBS display."""
    team1_attacker_id = request.form['team1_attacker']
    team1_defender_id = request.form['team1_defender']
    team2_attacker_id = request.form['team2_attacker']
    team2_defender_id = request.form['team2_defender']

    conn = connect_db()
    cursor = conn.cursor()

    # Fetch and store each player's name, ELO, and profile picture along with the player ID
    current_players_display.clear()  # Clear previous selection
    current_players_display.update({
        'team1_attacker': cursor.execute(
            "SELECT name, elo_attacker, profile_picture, id FROM players WHERE id = ?",
            (team1_attacker_id,)
        ).fetchone(),
        'team1_defender': cursor.execute(
            "SELECT name, elo_defender, profile_picture, id FROM players WHERE id = ?",
            (team1_defender_id,)
        ).fetchone(),
        'team2_attacker': cursor.execute(
            "SELECT name, elo_attacker, profile_picture, id FROM players WHERE id = ?",
            (team2_attacker_id,)
        ).fetchone(),
        'team2_defender': cursor.execute(
            "SELECT name, elo_defender, profile_picture, id FROM players WHERE id = ?",
            (team2_defender_id,)
        ).fetchone(),
    })

    # Save each player's name, ELO, and profile picture path to the OBS folder
    for role, (name, elo, profile_picture, player_id) in current_players_display.items():
        # Save name
        with open(os.path.join(OBS_DIRECTORY, f"{role}_name.txt"), "w") as name_file:
            name_file.write(name)

        # Save ELO
        with open(os.path.join(OBS_DIRECTORY, f"{role}_elo.txt"), "w") as elo_file:
            elo_file.write(str(elo))

        # Save profile picture
        src_picture_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_picture)
        dest_picture_path = os.path.join(OBS_DIRECTORY, f"{role}_profile.png")
        try:
            if os.path.exists(src_picture_path):
                resize_image(src_picture_path, dest_picture_path, 130, 130)
            else:
                # Use a default image if the profile picture is missing
                default_picture_path = os.path.join(app.config['UPLOAD_FOLDER'], 'default.png')
                if os.path.exists(default_picture_path):
                    resize_image(default_picture_path, dest_picture_path, 130, 130)
                else:
                    print(f"Warning: Default image not found at {default_picture_path}")
        except Exception as e:
            print(f"Error copying profile picture for {role}: {str(e)}")

    conn.close()
    return redirect(url_for('index'))

@app.route('/reset_current_players', methods=['POST'])
def reset_current_players():
    """Reset current players to default values."""
    current_players_display.clear()
    current_players_display.update({
        'team1_attacker': ('Unknown', 'N/A'),
        'team1_defender': ('Unknown', 'N/A'),
        'team2_attacker': ('Unknown', 'N/A'),
        'team2_defender': ('Unknown', 'N/A'),
    })
    return redirect(url_for('index'))

@app.route('/edit_player/<int:player_id>', methods=['POST'])
def edit_player(player_id):
    new_name = request.form['new_name']
    file = request.files.get('profile_picture')

    conn = connect_db()
    cursor = conn.cursor()

    # Update the player name
    cursor.execute("SELECT profile_picture FROM players WHERE id = ?", (player_id,))
    old_picture = cursor.fetchone()[0]

    # Rename or replace the profile picture
    if file and allowed_file(file.filename):
        new_filename = secure_filename(f"{new_name}.png")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(file_path)

        # Delete the old file if a new picture is uploaded
        old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], old_picture)
        if os.path.exists(old_file_path) and old_picture != 'default.png':
            os.remove(old_file_path)

        cursor.execute(
            "UPDATE players SET name = ?, profile_picture = ? WHERE id = ?",
            (new_name, new_filename, player_id)
        )
    else:
        # Just update the name if no picture is uploaded
        cursor.execute("UPDATE players SET name = ? WHERE id = ?", (new_name, player_id))

    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/set_score', methods=['POST'])
def set_score():
    """Set the current score for both teams and save to OBS."""
    team1_score = request.form['team1_score']
    team2_score = request.form['team2_score']

    # Update the current_score dictionary
    current_score['team1'] = int(team1_score)
    current_score['team2'] = int(team2_score)

    # Save scores to text files for OBS
    with open(os.path.join(OBS_DIRECTORY, "team1_score.txt"), "w") as team1_file:
        team1_file.write(str(team1_score))
    with open(os.path.join(OBS_DIRECTORY, "team2_score.txt"), "w") as team2_file:
        team2_file.write(str(team2_score))

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
