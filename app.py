import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime


st.set_page_config(
    page_title="Basketball Performance Readiness Dashboard",
    page_icon="",
    layout="wide"
)


REQUIRED_COLUMNS = [
    "Player", "Team", "Date", "Opponent", "Minutes", "Points", "Rebounds",
    "Assists", "FieldGoalPct", "ThreePointPct", "FreeThrowPct",
    "Turnovers", "PlusMinus", "Result"
]


# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    .main-title {
        font-size: 44px;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .subtitle {
        font-size: 16px;
        color: #6c757d;
        margin-bottom: 25px;
    }
    .score-card {
        padding: 22px;
        border-radius: 14px;
        background-color: #111827;
        border: 1px solid #374151;
        margin-bottom: 12px;
    }
    .score-label {
        font-size: 14px;
        color: #9ca3af;
        margin-bottom: 6px;
    }
    .score-value {
        font-size: 34px;
        font-weight: 800;
        color: white;
    }
    .green-card {
        padding: 18px;
        border-radius: 12px;
        background-color: #dcfce7;
        color: #14532d;
        border-left: 8px solid #22c55e;
        margin-bottom: 12px;
    }
    .amber-card {
        padding: 18px;
        border-radius: 12px;
        background-color: #fef3c7;
        color: #78350f;
        border-left: 8px solid #f59e0b;
        margin-bottom: 12px;
    }
    .red-card {
        padding: 18px;
        border-radius: 12px;
        background-color: #fee2e2;
        color: #7f1d1d;
        border-left: 8px solid #ef4444;
        margin-bottom: 12px;
    }
    .info-box {
        padding: 16px;
        border-radius: 12px;
        background-color: #eff6ff;
        color: #1e3a8a;
        border-left: 6px solid #3b82f6;
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Data functions
# -----------------------------
def load_sample_data() -> pd.DataFrame:
    return pd.read_csv("Data/clean_nba_player_gamelog_2018_2022.csv")


def validate_data(df: pd.DataFrame) -> list:
    return [col for col in REQUIRED_COLUMNS if col not in df.columns]


def clamp_score(value: float) -> float:
    if pd.isna(value) or np.isinf(value):
        return 0.0
    return max(0.0, min(100.0, float(value)))


def add_production_column(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Production"] = (
        df["Points"]
        + df["Rebounds"]
        + df["Assists"]
        + df["PlusMinus"]
    )
    return df


# -----------------------------
# Analytics functions
# -----------------------------
def calculate_scores(player_df: pd.DataFrame, recent_window: int) -> dict:
    player_df = player_df.sort_values("Date").copy()
    player_df = add_production_column(player_df)

    recent_df = player_df.tail(recent_window)

    season_production_avg = player_df["Production"].mean()
    recent_production_avg = recent_df["Production"].mean()

    if season_production_avg > 0:
        recent_form_score = (recent_production_avg / season_production_avg) * 100
    else:
        recent_form_score = 0

    season_minutes_avg = player_df["Minutes"].mean()
    recent_minutes_avg = recent_df["Minutes"].mean()

    if season_minutes_avg > 0:
        workload_ratio = recent_minutes_avg / season_minutes_avg
    else:
        workload_ratio = 1

    if 0.85 <= workload_ratio <= 1.15:
        workload_score = 100
    elif 1.15 < workload_ratio <= 1.30:
        workload_score = 75
    elif workload_ratio > 1.30:
        workload_score = 55
    elif 0.70 <= workload_ratio < 0.85:
        workload_score = 75
    else:
        workload_score = 60

    fg_score = recent_df["FieldGoalPct"].mean()
    three_score = recent_df["ThreePointPct"].mean()
    ft_score = recent_df["FreeThrowPct"].mean()

    avg_turnovers = recent_df["Turnovers"].mean()
    turnover_control = clamp_score(100 - (avg_turnovers * 12))

    efficiency_score = (
        0.40 * fg_score
        + 0.25 * three_score
        + 0.20 * ft_score
        + 0.15 * turnover_control
    )

    production_mean = recent_df["Production"].mean()
    production_std = recent_df["Production"].std()

    if production_mean > 0 and not pd.isna(production_std):
        cv = production_std / production_mean
        consistency_score = 100 - (cv * 100)
    else:
        consistency_score = 100

    participation_score = (
        (recent_df["Minutes"] > 0).sum() / len(recent_df)
    ) * 100 if len(recent_df) > 0 else 0

    recent_form_score = clamp_score(recent_form_score)
    workload_score = clamp_score(workload_score)
    efficiency_score = clamp_score(efficiency_score)
    consistency_score = clamp_score(consistency_score)
    participation_score = clamp_score(participation_score)

    readiness_score = (
        0.30 * recent_form_score
        + 0.25 * workload_score
        + 0.20 * efficiency_score
        + 0.15 * consistency_score
        + 0.10 * participation_score
    )

    readiness_score = clamp_score(readiness_score)

    return {
        "Readiness Score": round(readiness_score, 1),
        "Recent Form Score": round(recent_form_score, 1),
        "Workload Balance Score": round(workload_score, 1),
        "Efficiency Score": round(efficiency_score, 1),
        "Consistency Score": round(consistency_score, 1),
        "Game Participation Score": round(participation_score, 1),
        "Recent Production Avg": round(recent_production_avg, 1),
        "Season Production Avg": round(season_production_avg, 1),
        "Recent Minutes Avg": round(recent_minutes_avg, 1),
        "Season Minutes Avg": round(season_minutes_avg, 1),
    }


def readiness_label(score: float) -> str:
    if score >= 80:
        return "High Readiness"
    if score >= 60:
        return "Monitor"
    return "Performance Risk"


def card_class(status: str) -> str:
    if status == "High Readiness":
        return "green-card"
    if status == "Monitor":
        return "amber-card"
    return "red-card"


def build_alerts(scores: dict) -> list:
    alerts = []

    if scores["Workload Balance Score"] < 70:
        alerts.append("Workload imbalance detected. Review minutes and rotation plan.")

    if scores["Efficiency Score"] < 65:
        alerts.append("Efficiency profile is below target. Review shot selection and turnover control.")

    if scores["Consistency Score"] < 65:
        alerts.append("Performance variability is high. Monitor game-to-game stability.")

    if scores["Recent Form Score"] < 70:
        alerts.append("Recent production is below season baseline.")

    if not alerts:
        alerts.append("No major performance-readiness alerts detected.")

    return alerts


def build_pre_game_action(scores: dict) -> str:
    status = readiness_label(scores["Readiness Score"])

    if status == "High Readiness":
        return "Available for normal or high involvement based on current performance indicators."
    if status == "Monitor":
        return "Available for involvement, but staff should monitor workload or performance stability."
    return "Reduced performance readiness. Consider managed involvement or targeted review before selection."


def live_game_decision(minutes, points, rebounds, assists, turnovers, plus_minus, concern_level):
    contribution = points + rebounds + assists + plus_minus

    alerts = []
    status = "Normal"
    action = "Continue normal involvement."

    if minutes >= 32:
        alerts.append("High live workload based on current minutes.")
        status = "Monitor"
        action = "Monitor next rotation and consider minute management."

    if turnovers >= 5:
        alerts.append("Turnover count is high relative to live contribution.")
        status = "Monitor"
        action = "Review decision-making and ball security before next rotation."

    if plus_minus <= -8:
        alerts.append("Current plus-minus is strongly negative.")
        status = "Monitor"
        action = "Review matchup or rotation impact."

    if concern_level >= 4:
        alerts.append("Coach concern level is high.")
        status = "Manage"
        action = "Consider reducing load or reassessing role in next rotation."

    if contribution < 10 and minutes > 18:
        alerts.append("Low contribution relative to minutes played.")
        status = "Monitor"
        action = "Monitor performance impact and consider role adjustment."

    if not alerts:
        alerts.append("Live indicators are within normal range.")

    return status, action, alerts, contribution


def post_game_impact(points, rebounds, assists, turnovers, plus_minus, minutes):
    production = points + rebounds + assists + plus_minus

    if production >= 45 and plus_minus >= 5:
        impact = "Positive"
    elif production >= 25:
        impact = "Neutral"
    else:
        impact = "Negative"

    if minutes >= 36:
        workload = "Elevated"
    elif minutes >= 25:
        workload = "Normal"
    else:
        workload = "Low"

    if turnovers <= 3:
        efficiency_note = "Strong"
    elif turnovers <= 5:
        efficiency_note = "Monitor"
    else:
        efficiency_note = "Review"

    if impact == "Positive" and workload != "Elevated":
        recommendation = "Normal training and involvement can continue."
    elif workload == "Elevated":
        recommendation = "Consider recovery-focused follow-up and monitor next-session load."
    elif efficiency_note == "Review":
        recommendation = "Review turnover profile and decision-making."
    else:
        recommendation = "Monitor next game response and recent form trend."

    return impact, workload, efficiency_note, recommendation, production

def get_team_summary(df: pd.DataFrame, team: str) -> dict:
    """Create team-level summary statistics from cleaned player-game data."""
    if team == "All":
        team_df = df.copy()
    else:
        team_df = df[df["Team"] == team].copy()

    if team_df.empty:
        return {}

    # One row per team game
    games_df = (
        team_df[
            ["Date", "Team", "Opponent", "Result", "Team_Points", "Opponent_Points"]
        ]
        .drop_duplicates()
        .sort_values("Date")
    )

    games_played = len(games_df)
    wins = (games_df["Result"] == "W").sum()
    losses = (games_df["Result"] == "L").sum()
    win_pct = (wins / games_played) * 100 if games_played > 0 else 0

    avg_team_points = games_df["Team_Points"].mean()
    avg_opp_points = games_df["Opponent_Points"].mean()
    avg_margin = (games_df["Team_Points"] - games_df["Opponent_Points"]).mean()

    return {
        "Games Played": games_played,
        "Wins": wins,
        "Losses": losses,
        "Win %": round(win_pct, 1),
        "Avg Team Points": round(avg_team_points, 1),
        "Avg Opponent Points": round(avg_opp_points, 1),
        "Avg Margin": round(avg_margin, 1),
        "Games Data": games_df,
        "Team Data": team_df
    }


def get_player_summary(df: pd.DataFrame, player: str) -> dict:
    """Create player-level summary statistics."""
    player_df = df[df["Player"] == player].copy()

    if player_df.empty:
        return {}

    games = len(player_df)
    avg_minutes = player_df["Minutes"].mean()
    ppg = player_df["Points"].mean()
    rpg = player_df["Rebounds"].mean()
    apg = player_df["Assists"].mean()
    fg = player_df["FieldGoalPct"].mean()
    three = player_df["ThreePointPct"].mean()
    ft = player_df["FreeThrowPct"].mean()
    turnovers = player_df["Turnovers"].mean()
    plus_minus = player_df["PlusMinus"].mean()

    return {
        "Games": games,
        "Avg Minutes": round(avg_minutes, 1),
        "PPG": round(ppg, 1),
        "RPG": round(rpg, 1),
        "APG": round(apg, 1),
        "FG%": round(fg, 1),
        "3P%": round(three, 1),
        "FT%": round(ft, 1),
        "Turnovers": round(turnovers, 1),
        "PlusMinus": round(plus_minus, 1),
        "Player Data": player_df.sort_values("Date")
    }


def calculate_team_player_table(team_df: pd.DataFrame, recent_window: int) -> pd.DataFrame:
    """Generate player averages and readiness scores for a selected team."""
    rows = []

    for player in sorted(team_df["Player"].dropna().unique()):
        player_data = team_df[team_df["Player"] == player].copy()

        if len(player_data) < 3:
            continue

        window = min(recent_window, len(player_data))
        scores = calculate_scores(player_data, window)

        rows.append({
            "Player": player,
            "Games": len(player_data),
            "Avg Minutes": round(player_data["Minutes"].mean(), 1),
            "PPG": round(player_data["Points"].mean(), 1),
            "RPG": round(player_data["Rebounds"].mean(), 1),
            "APG": round(player_data["Assists"].mean(), 1),
            "FG%": round(player_data["FieldGoalPct"].mean(), 1),
            "3P%": round(player_data["ThreePointPct"].mean(), 1),
            "Turnovers": round(player_data["Turnovers"].mean(), 1),
            "PlusMinus": round(player_data["PlusMinus"].mean(), 1),
            "Readiness Score": scores["Readiness Score"],
            "Status": readiness_label(scores["Readiness Score"])
        })

    return pd.DataFrame(rows).sort_values("Readiness Score", ascending=False)

def make_summary_csv(summary_dict: dict) -> bytes:
    summary_df = pd.DataFrame([summary_dict])
    return summary_df.to_csv(index=False).encode("utf-8")


# -----------------------------
# Header
# -----------------------------
st.markdown(
    '<div class="main-title"> Basketball Performance Readiness Dashboard</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Localhost sports analytics tool for coach-facing performance-readiness and workload-support decisions.</div>',
    unsafe_allow_html=True
)


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("User Inputs")

tool_mode = st.sidebar.radio(
    "Select tool mode",
    [
        "Team Overview",
        "Player Profile",
        "Pre-Game Readiness",
        "Live Game Monitor",
        "Post-Game Report"
    ]
)

uploaded_file = st.sidebar.file_uploader(
    "Upload basketball game-log CSV",
    type=["csv"]
)

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
else:
    data = load_sample_data()

missing_columns = validate_data(data)

if missing_columns:
    st.error(
        "Dataset missing required columns: "
        + ", ".join(missing_columns)
    )
    st.stop()

data["Date"] = pd.to_datetime(data["Date"])
data = data.sort_values("Date")

team_options = ["All"] + sorted(data["Team"].dropna().unique().tolist())
selected_team = st.sidebar.selectbox("Select team", team_options)

if selected_team != "All":
    filtered_data = data[data["Team"] == selected_team].copy()
else:
    filtered_data = data.copy()

player_options = sorted(filtered_data["Player"].dropna().unique().tolist())
selected_player = st.sidebar.selectbox("Select player", player_options)

recent_window = st.sidebar.selectbox(
    "Recent-game window",
    options=[3, 5, 10],
    index=1
)

metric_focus = st.sidebar.selectbox(
    "Metric focus",
    options=["All-round", "Scoring", "Workload", "Efficiency"],
    index=0
)

player_df = filtered_data[filtered_data["Player"] == selected_player].copy()

if len(player_df) < recent_window:
    recent_window = len(player_df)

scores = calculate_scores(player_df, recent_window)
status = readiness_label(scores["Readiness Score"])
alerts = build_alerts(scores)
pre_game_action = build_pre_game_action(scores)


# -----------------------------
# Mode 1: Team Overview
# -----------------------------
if tool_mode == "Team Overview":
    st.subheader("Team Overview Mode")
    st.write(
        "This mode provides a team-level performance summary, recent game context, and player readiness ranking."
    )

    if selected_team == "All":
        st.warning("Select a specific team from the sidebar to view the Team Overview.")
    else:
        team_summary = get_team_summary(filtered_data, selected_team)

        if not team_summary:
            st.error("No team data available for the selected filters.")
        else:
            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Games Played", team_summary["Games Played"])
            col2.metric("Win %", f"{team_summary['Win %']}%")
            col3.metric("Avg Points", team_summary["Avg Team Points"])
            col4.metric("Avg Margin", team_summary["Avg Margin"])

            st.write("### Recent Games")

            recent_games = team_summary["Games Data"].tail(10).copy()
            recent_games["Margin"] = (
                recent_games["Team_Points"] - recent_games["Opponent_Points"]
            )

            st.dataframe(
                recent_games[
                    ["Date", "Opponent", "Result", "Team_Points", "Opponent_Points", "Margin"]
                ],
                use_container_width=True
            )

            fig_recent_games = px.bar(
                recent_games,
                x="Date",
                y="Margin",
                color="Result",
                title="Recent Game Margins"
            )
            st.plotly_chart(fig_recent_games, use_container_width=True)

            st.write("### Team Player Readiness Ranking")

            player_table = calculate_team_player_table(
                team_summary["Team Data"],
                recent_window
            )

            st.dataframe(player_table, use_container_width=True)

            top_players = player_table.head(5)

            fig_players = px.bar(
                top_players,
                x="Player",
                y="Readiness Score",
                text="Readiness Score",
                title="Top 5 Player Readiness Scores"
            )
            st.plotly_chart(fig_players, use_container_width=True)

            monitor_count = (player_table["Status"] != "High Readiness").sum()

            if monitor_count == 0:
                team_insight = (
                    "Team readiness profile is strong. No major player-level readiness concerns detected."
                )
            else:
                team_insight = (
                    f"{monitor_count} player(s) are currently flagged as Monitor or Performance Risk. "
                    "Coaching staff should review workload, efficiency, and consistency indicators."
                )

            st.markdown(
                f"""
                <div class="info-box">
                    <b>Team Insight:</b><br>
                    {team_insight}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.download_button(
                "Download team readiness table",
                data=player_table.to_csv(index=False).encode("utf-8"),
                file_name=f"{selected_team}_team_readiness_table.csv",
                mime="text/csv"
            )


# -----------------------------
# Mode 2: Player Profile
# -----------------------------
elif tool_mode == "Player Profile":
    st.subheader("Player Profile Mode")
    st.write(
        "This mode provides a dedicated player dashboard with season averages, recent form, workload, efficiency, and readiness context."
    )

    player_summary = get_player_summary(filtered_data, selected_player)

    if not player_summary:
        st.error("No player data available.")
    else:
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Games", player_summary["Games"])
        col2.metric("Avg Minutes", player_summary["Avg Minutes"])
        col3.metric("PPG", player_summary["PPG"])
        col4.metric("Readiness", f"{scores['Readiness Score']}/100")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("RPG", player_summary["RPG"])
        col2.metric("APG", player_summary["APG"])
        col3.metric("FG%", f"{player_summary['FG%']}%")
        col4.metric("3P%", f"{player_summary['3P%']}%")

        st.markdown(
            f"""
            <div class="{card_class(status)}">
                <b>Player Readiness Status:</b> {status}<br>
                <b>Coach Action:</b> {pre_game_action}
            </div>
            """,
            unsafe_allow_html=True
        )

        player_profile_df = player_summary["Player Data"].tail(recent_window).copy()

        st.write("### Recent Performance Trend")

        fig_profile = px.line(
            player_profile_df,
            x="Date",
            y=["Points", "Rebounds", "Assists", "PlusMinus"],
            markers=True,
            title=f"{selected_player}: Recent Performance Trend"
        )
        st.plotly_chart(fig_profile, use_container_width=True)

        st.write("### Workload Trend")

        fig_minutes = px.bar(
            player_profile_df,
            x="Date",
            y="Minutes",
            title=f"{selected_player}: Recent Minutes"
        )
        st.plotly_chart(fig_minutes, use_container_width=True)

        st.write("### Shooting Efficiency")

        fig_efficiency = px.line(
            player_profile_df,
            x="Date",
            y=["FieldGoalPct", "ThreePointPct", "FreeThrowPct"],
            markers=True,
            title=f"{selected_player}: Shooting Efficiency"
        )
        st.plotly_chart(fig_efficiency, use_container_width=True)

        st.write("### Recent Game Log")

        st.dataframe(player_profile_df, use_container_width=True)

        player_summary_download = {
            "Player": selected_player,
            "Team": selected_team,
            "Games": player_summary["Games"],
            "Avg Minutes": player_summary["Avg Minutes"],
            "PPG": player_summary["PPG"],
            "RPG": player_summary["RPG"],
            "APG": player_summary["APG"],
            "FG%": player_summary["FG%"],
            "3P%": player_summary["3P%"],
            "FT%": player_summary["FT%"],
            "Readiness Score": scores["Readiness Score"],
            "Status": status,
            "Coach Action": pre_game_action
        }

        st.download_button(
            "Download player profile summary",
            data=make_summary_csv(player_summary_download),
            file_name=f"{selected_player.replace(' ', '_')}_player_profile_summary.csv",
            mime="text/csv"
        )


# -----------------------------
# Mode 3: Pre-Game Readiness
# -----------------------------
elif tool_mode == "Pre-Game Readiness":
    st.subheader("Pre-Game Readiness Mode")
    st.write(
        "This mode supports selection and workload planning before a game using recent performance indicators."
    )

    game_context = st.selectbox(
        "Game context",
        ["Normal game", "High-importance game", "Back-to-back game"]
    )

    coach_confidence = st.slider(
        "Coach confidence rating",
        min_value=1,
        max_value=5,
        value=3,
        help="Optional coaching judgement input. This does not represent medical status."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="score-card">
                <div class="score-label">Readiness Score</div>
                <div class="score-value">{scores["Readiness Score"]}/100</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="score-card">
                <div class="score-label">Status</div>
                <div class="score-value">{status}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="score-card">
                <div class="score-label">Recent Window</div>
                <div class="score-value">Last {recent_window}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        f"""
        <div class="{card_class(status)}">
            <b>Recommended Coach Action:</b><br>
            {pre_game_action}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="info-box">
            <b>Key Alerts:</b>
        </div>
        """,
        unsafe_allow_html=True
    )
    for alert in alerts:
        st.write(f"• {alert}")

    component_df = pd.DataFrame({
        "Component": [
            "Recent Form",
            "Workload Balance",
            "Efficiency",
            "Consistency",
            "Game Participation"
        ],
        "Score": [
            scores["Recent Form Score"],
            scores["Workload Balance Score"],
            scores["Efficiency Score"],
            scores["Consistency Score"],
            scores["Game Participation Score"]
        ]
    })

    fig_components = px.bar(
        component_df,
        x="Component",
        y="Score",
        text="Score",
        title="Readiness Component Breakdown",
        range_y=[0, 100]
    )
    st.plotly_chart(fig_components, use_container_width=True)

    context_df = pd.DataFrame({
        "Metric": ["Production Avg", "Minutes Avg"],
        "Recent": [
            scores["Recent Production Avg"],
            scores["Recent Minutes Avg"]
        ],
        "Season": [
            scores["Season Production Avg"],
            scores["Season Minutes Avg"]
        ],
    })

    fig_context = px.bar(
        context_df,
        x="Metric",
        y=["Recent", "Season"],
        barmode="group",
        title="Recent vs Season Context"
    )
    st.plotly_chart(fig_context, use_container_width=True)

    summary = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Mode": tool_mode,
        "Player": selected_player,
        "Team": selected_team,
        "Game Context": game_context,
        "Coach Confidence": coach_confidence,
        "Readiness Score": scores["Readiness Score"],
        "Status": status,
        "Recommended Action": pre_game_action,
        "Alerts": " | ".join(alerts)
    }

    st.download_button(
        "Download readiness summary",
        data=make_summary_csv(summary),
        file_name=f"{selected_player.replace(' ', '_')}_pre_game_readiness_summary.csv",
        mime="text/csv"
    )


# -----------------------------
# Mode 2: Live Game Monitor
# -----------------------------
elif tool_mode == "Live Game Monitor":
    st.subheader("Live Game Monitor Mode")
    st.write(
        "This mode allows quick manual updates during a game. It is designed for rapid coach-facing decisions, not spreadsheet upload during live play."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        live_minutes = st.slider("Current minutes", 0, 48, 24)
        live_points = st.slider("Current points", 0, 60, 18)

    with col2:
        live_rebounds = st.slider("Current rebounds", 0, 25, 6)
        live_assists = st.slider("Current assists", 0, 20, 5)

    with col3:
        live_turnovers = st.slider("Current turnovers", 0, 12, 3)
        live_plus_minus = st.slider("Current plus-minus", -30, 30, 0)

    concern_level = st.slider(
        "Coach concern level",
        min_value=1,
        max_value=5,
        value=2
    )

    live_status, live_action, live_alerts, live_contribution = live_game_decision(
        live_minutes,
        live_points,
        live_rebounds,
        live_assists,
        live_turnovers,
        live_plus_minus,
        concern_level
    )

    if live_status == "Normal":
        live_class = "green-card"
    elif live_status == "Monitor":
        live_class = "amber-card"
    else:
        live_class = "red-card"

    col1, col2, col3 = st.columns(3)

    col1.metric("Live Contribution", live_contribution)
    col2.metric("Live Load Status", live_status)
    col3.metric("Coach Concern", f"{concern_level}/5")

    st.markdown(
        f"""
        <div class="{live_class}">
            <b>Live Coach Action:</b><br>
            {live_action}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("### Live Alerts")
    for alert in live_alerts:
        st.write(f"• {alert}")

    live_df = pd.DataFrame({
        "Metric": ["Points", "Rebounds", "Assists", "Turnovers", "Plus-Minus"],
        "Value": [live_points, live_rebounds, live_assists, live_turnovers, live_plus_minus]
    })

    fig_live = px.bar(
        live_df,
        x="Metric",
        y="Value",
        title="Current Live Game Indicators"
    )
    st.plotly_chart(fig_live, use_container_width=True)

    summary = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Mode": tool_mode,
        "Player": selected_player,
        "Current Minutes": live_minutes,
        "Points": live_points,
        "Rebounds": live_rebounds,
        "Assists": live_assists,
        "Turnovers": live_turnovers,
        "PlusMinus": live_plus_minus,
        "Coach Concern": concern_level,
        "Live Status": live_status,
        "Live Action": live_action,
        "Alerts": " | ".join(live_alerts)
    }

    st.download_button(
        "Download live monitoring summary",
        data=make_summary_csv(summary),
        file_name=f"{selected_player.replace(' ', '_')}_live_monitor_summary.csv",
        mime="text/csv"
    )


# -----------------------------
# Mode 3: Post-Game Report
# -----------------------------
elif tool_mode == "Post-Game Report":
    st.subheader("Post-Game Report Mode")
    st.write(
        "This mode generates a post-game performance summary for review, reporting, and follow-up planning."
    )

    st.write("### Enter latest game statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        pg_minutes = st.number_input("Minutes", min_value=0, max_value=60, value=34)
        pg_points = st.number_input("Points", min_value=0, max_value=80, value=25)

    with col2:
        pg_rebounds = st.number_input("Rebounds", min_value=0, max_value=40, value=7)
        pg_assists = st.number_input("Assists", min_value=0, max_value=30, value=5)

    with col3:
        pg_turnovers = st.number_input("Turnovers", min_value=0, max_value=20, value=3)
        pg_plus_minus = st.number_input("Plus-minus", min_value=-60, max_value=60, value=4)

    impact, workload, efficiency_note, pg_recommendation, pg_production = post_game_impact(
        pg_points,
        pg_rebounds,
        pg_assists,
        pg_turnovers,
        pg_plus_minus,
        pg_minutes
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Game Production", pg_production)
    col2.metric("Game Impact", impact)
    col3.metric("Workload", workload)
    col4.metric("Efficiency Flag", efficiency_note)

    if impact == "Positive":
        pg_class = "green-card"
    elif impact == "Neutral":
        pg_class = "amber-card"
    else:
        pg_class = "red-card"

    st.markdown(
        f"""
        <div class="{pg_class}">
            <b>Post-Game Recommendation:</b><br>
            {pg_recommendation}
        </div>
        """,
        unsafe_allow_html=True
    )

    post_df = pd.DataFrame({
        "Metric": ["Points", "Rebounds", "Assists", "Turnovers", "Plus-Minus", "Minutes"],
        "Value": [pg_points, pg_rebounds, pg_assists, pg_turnovers, pg_plus_minus, pg_minutes]
    })

    fig_post = px.bar(
        post_df,
        x="Metric",
        y="Value",
        title="Post-Game Performance Summary"
    )
    st.plotly_chart(fig_post, use_container_width=True)

    summary = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Mode": tool_mode,
        "Player": selected_player,
        "Minutes": pg_minutes,
        "Points": pg_points,
        "Rebounds": pg_rebounds,
        "Assists": pg_assists,
        "Turnovers": pg_turnovers,
        "PlusMinus": pg_plus_minus,
        "Game Production": pg_production,
        "Game Impact": impact,
        "Workload": workload,
        "Efficiency Flag": efficiency_note,
        "Recommendation": pg_recommendation
    }

    st.download_button(
        "Download post-game report",
        data=make_summary_csv(summary),
        file_name=f"{selected_player.replace(' ', '_')}_post_game_report.csv",
        mime="text/csv"
    )


# -----------------------------
# Documentation section
# -----------------------------
st.divider()
with st.expander("Tool Documentation and Interpretation"):
    st.write(
        """
        ### Purpose
        This dashboard is a local sports analytics tool designed to support basketball coaches,
        analysts, and performance staff with player readiness and workload-support decisions.

        ### Tool Modes
        **Pre-Game Readiness:** Uses recent game-log data to assess readiness before selection.  
        **Live Game Monitor:** Uses quick manual live inputs to support in-game rotation decisions.  
        **Post-Game Report:** Summarises post-game performance and produces a downloadable report.

        ### Required Data Columns
        Player, Team, Date, Opponent, Minutes, Points, Rebounds, Assists, FieldGoalPct,
        ThreePointPct, FreeThrowPct, Turnovers, PlusMinus, Result.

        ### Performance Readiness Score
        The readiness score is calculated as:

        - 30% Recent Form
        - 25% Workload Balance
        - 20% Efficiency
        - 15% Consistency
        - 10% Game Participation

        ### Score Interpretation
        - 80–100: High Readiness
        - 60–79: Monitor
        - Below 60: Performance Risk

        ### Important Limitation
        This is not a medical or injury prediction tool. It is a performance-readiness
        support tool based on basketball game-log indicators and configurable user inputs.
        """
    )