# Placement System Documentation

## Overview
The E-Kicker Leaderboard now implements a placement system for the new season:
- Players must play **5 games** before appearing on the public leaderboard
- ELO is tracked and updated from the **first game**
- Internal Flask app shows all players with their placement status
- Public GitHub leaderboard only displays players with 5+ completed games

## How It Works

### Database
- Added `games_played` column to track each player's game count
- Increments by 1 each time a player participates in a match (regardless of result)

### Flask App (Internal Use)
- Shows **ALL players** in the management interface
- Displays games played count (e.g., "3/5")
- Shows placement status badge:
  - **Placement** (orange) = Player has < 5 games
  - **Active** (green) = Player has 5+ games and appears on public leaderboard

### Public Leaderboard (GitHub Pages)
- Only displays players with `games_played >= 5`
- Run `python update_and_push_leaderboard.py` to update

## Usage

### Recording Matches
1. Players start at 1000 ELO (attacker and defender)
2. When a match is recorded, all 4 participating players:
   - Have their ELOs updated normally
   - Have their `games_played` counter incremented by 1

### Viewing Progress
- Internal Flask app shows real-time progress for all players
- Once a player reaches 5 games, they automatically appear on public leaderboard

### Resetting for New Season
- Run: `python reset_season.py` - Sets all ELOs to 1000 and games_played to 0

## Files Modified
- `app.py` - Updated to track games_played
- `templates/index.html` - Added games played display and placement status
- `update_and_push_leaderboard.py` - Filters to only include 5+ game players
- `add_placement_system.py` - Migration script to add the feature
