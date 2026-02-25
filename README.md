# E-Kicker By BEP

## Run flask server
`python3 app.py`

## Web Content
Modify the file templates/index.html

### ELO Rating System

The ELO rating system dynamically adjusts player skill levels based on match results. In Fuzeball, each player has two separate ELO ratings based on their **role**: one as an **attacker** and one as a **defender**.

#### How It Works

1. **Separate ELO Ratings by Role**: Each player has an **attacker ELO** and a **defender ELO** to capture their skill level in both roles independently. This allows players to be ranked uniquely for each role, providing a more accurate representation of their performance.

2. **Team-Based Adjustments**: The ELO for each player is adjusted based on the performance of their team as a whole, not just on individual role matchups. This means that both the attacker and defender on a team will see changes in their respective ELOs depending on the team’s success or failure, which reflects the collaborative nature of 2v2 gameplay.

3. **Starting Ratings**: Players start with a default rating (e.g., 1000) for both the attacker and defender roles.

4. **Expected Score**: Before a match, each team’s expected score is calculated based on the **average ELO** of the attacker and defender on each team:
   \[
   \text{Expected Score for Team 1} = \frac{1}{1 + 10^{(\text{Team 2 ELO} - \text{Team 1 ELO}) / 400}}
   \]
   where **Team ELO** is the average of the attacker and defender ELOs.

5. **Match Result**: After each game:
   - A **win** gives the team an **actual score of 1**.
   - A **loss** gives the team an **actual score of 0**.
   - A **draw** gives both teams an **actual score of 0.5**.

6. **Rating Adjustment**: Each player’s ELO is updated based on the team’s result using:
New Rating = Current Rating + K × (Actual Score - Expected Score) where **K** controls the rate of change.

#### Example Calculation with Uneven Team ELOs

Suppose we have a match with **Team 1** (Player A as Attacker, Player B as Defender) and **Team 2** (Player C as Attacker, Player D as Defender), with the following ELOs:

- **Player A** (Attacker on Team 1): Attacker ELO = 1300
- **Player B** (Defender on Team 1): Defender ELO = 1250
- **Player C** (Attacker on Team 2): Attacker ELO = 1100
- **Player D** (Defender on Team 2): Defender ELO = 1050

**Team ELOs**:
- **Team 1 ELO**: (1300 + 1250) / 2 = 1275
- **Team 2 ELO**: (1100 + 1050) / 2 = 1075

Since Team 1 has a higher ELO, they are expected to win. We calculate each team’s **expected score** based on these ELOs:

- **Expected Score for Team 1**: 
\[
\frac{1}{1 + 10^{(1075 - 1275) / 400}} \approx 0.76
\]
- **Expected Score for Team 2**: 
\[
1 - \text{Expected Score for Team 1} = 0.24
\]

##### Scenario 1: Team 1 Wins (Expected Outcome)
- **Actual Score for Team 1** = 1
- **Actual Score for Team 2** = 0

Each player’s ELO adjustment will be calculated based on their **role-specific ELO** and the team’s actual and expected scores:

- **Player A’s new ELO** (Team 1 Attacker):
\[
\text{New ELO for A} = 1300 + K \times (1 - 0.76) \approx 1308
\]
- **Player B’s new ELO** (Team 1 Defender):
\[
\text{New ELO for B} = 1250 + K \times (1 - 0.76) \approx 1258
\]
- **Player C’s new ELO** (Team 2 Attacker):
\[
\text{New ELO for C} = 1100 + K \times (0 - 0.24) \approx 1092
\]
- **Player D’s new ELO** (Team 2 Defender):
\[
\text{New ELO for D} = 1050 + K \times (0 - 0.24) \approx 1042
\]

##### Scenario 2: Team 2 Wins (Upset)
- **Actual Score for Team 1** = 0
- **Actual Score for Team 2** = 1

In this case, Team 2 (the lower-rated team) wins, leading to a larger adjustment for both teams because the outcome was unexpected.

- **Player A’s new ELO** (Team 1 Attacker):
\[
\text{New ELO for A} = 1300 + K \times (0 - 0.76) \approx 1276.8
\]
- **Player B’s new ELO** (Team 1 Defender):
\[
\text{New ELO for B} = 1250 + K \times (0 - 0.76) \approx 1226.8
\]
- **Player C’s new ELO** (Team 2 Attacker):
\[
\text{New ELO for C} = 1100 + K \times (1 - 0.24) \approx 1124.8
\]
- **Player D’s new ELO** (Team 2 Defender):
\[
\text{New ELO for D} = 1050 + K \times (1 - 0.24) \approx 1074.8
\]

This system provides a team-based ranking that rewards upsets and tempers expected wins, creating a fairer and more dynamic ranking for 2v2 gameplay.
