import os
import base64
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# ------------------------------------------------------------
# Page setup
# ------------------------------------------------------------

st.set_page_config(
    page_title="Basketball Performance Readiness Dashboard",
    page_icon="",
    layout="wide",
)

st.markdown("""
<style>
.report-card {
    background-color: #111827;
    border: 1px solid #374151;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 12px;
    min-height: 120px;
}
.report-card-title {
    font-size: 16px;
    color: #9CA3AF;
    margin-bottom: 10px;
    font-weight: 600;
}
.report-card-value {
    font-size: 28px;
    font-weight: 700;
    color: #F9FAFB;
    line-height: 1.2;
    white-space: normal !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
}
</style>
""", unsafe_allow_html=True)

def report_card(title, value):
    st.markdown(
        f"""
        <div class="report-card">
            <div class="report-card-title">{title}</div>
            <div class="report-card-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
# ------------------------------------------------------------
# Styling - Orange / Charcoal Glassmorphism UI
# ------------------------------------------------------------

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --bg-main: #101010;
            --bg-panel: rgba(41, 41, 41, 0.72);
            --bg-panel-strong: rgba(41, 41, 41, 0.92);
            --orange: #F47A3A;
            --orange-soft: rgba(244, 122, 58, 0.18);
            --orange-border: rgba(244, 122, 58, 0.55);
            --text-main: #F7F7F7;
            --text-muted: #B8B8B8;
            --border-glass: rgba(255, 255, 255, 0.12);
            --shadow-glass: 0 18px 45px rgba(0, 0, 0, 0.38);
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(244, 122, 58, 0.20), transparent 32%),
                radial-gradient(circle at bottom right, rgba(244, 122, 58, 0.12), transparent 30%),
                linear-gradient(135deg, #101010 0%, #171717 45%, #292929 100%);
            color: var(--text-main);
        }

        section[data-testid="stSidebar"] {
            background: rgba(16, 16, 16, 0.82) !important;
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            border-right: 1px solid var(--border-glass);
        }

        section[data-testid="stSidebar"] > div {
            background: transparent !important;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p {
            color: var(--text-main) !important;
            font-weight: 600 !important;
        }

        .block-container {
            padding-top: 3rem;
            padding-bottom: 3rem;
            max-width: 1280px;
        }

        .main-title {
            font-size: 42px;
            font-weight: 800;
            letter-spacing: -1.2px;
            margin-bottom: 6px;
            color: var(--text-main);
            text-shadow: 0 3px 18px rgba(0, 0, 0, 0.45);
        }

        .main-title::after {
            content: "";
            display: block;
            width: 90px;
            height: 4px;
            margin-top: 14px;
            border-radius: 20px;
            background: linear-gradient(90deg, var(--orange), rgba(244, 122, 58, 0.15));
        }

        .subtitle {
            font-size: 17px;
            color: var(--text-muted);
            margin-bottom: 30px;
            font-weight: 500;
        }

        h1, h2, h3, h4 {
            color: var(--text-main) !important;
            letter-spacing: -0.4px;
        }

        p, span, label, div {
            color: inherit;
        }

        div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stMetric"]) {
            background: rgba(41, 41, 41, 0.62);
            border: 1px solid var(--border-glass);
            border-radius: 18px;
            padding: 14px 16px;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            box-shadow: var(--shadow-glass);
        }

        div[data-testid="stMetric"] {
            background: transparent;
        }

        div[data-testid="stMetricLabel"] {
            color: var(--text-muted) !important;
            font-weight: 600;
        }

        div[data-testid="stMetricValue"] {
            color: var(--text-main) !important;
            font-weight: 800;
            letter-spacing: -0.8px;
        }

        .score-card {
            padding: 24px;
            border-radius: 20px;
            background:
                linear-gradient(145deg, rgba(244, 122, 58, 0.24), rgba(41, 41, 41, 0.72));
            color: var(--text-main);
            text-align: center;
            margin-bottom: 16px;
            border: 1px solid var(--orange-border);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            box-shadow: var(--shadow-glass);
        }

        .score-number {
            font-size: 52px;
            font-weight: 800;
            margin-bottom: 5px;
            color: var(--orange);
            text-shadow: 0 0 18px rgba(244, 122, 58, 0.35);
        }

        .score-label {
            font-size: 17px;
            font-weight: 700;
            color: var(--text-main);
        }

        .green-box,
        .amber-box,
        .red-box,
        .info-box {
            padding: 18px 20px;
            border-radius: 18px;
            margin-bottom: 16px;
            background: rgba(41, 41, 41, 0.68);
            border: 1px solid var(--border-glass);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            box-shadow: var(--shadow-glass);
            color: var(--text-main);
        }

        .green-box {
            border-left: 6px solid #33D17A;
        }

        .amber-box {
            border-left: 6px solid var(--orange);
        }

        .red-box {
            border-left: 6px solid #FF4D4D;
        }

        .info-box {
            border-left: 6px solid var(--orange);
            background: linear-gradient(145deg, rgba(244, 122, 58, 0.16), rgba(41, 41, 41, 0.70));
        }

        .green-box b,
        .amber-box b,
        .red-box b,
        .info-box b {
            color: var(--orange);
        }

        .report-card {
            background:
                linear-gradient(145deg, rgba(41, 41, 41, 0.78), rgba(16, 16, 16, 0.72));
            border: 1px solid var(--border-glass);
            border-radius: 18px;
            padding: 18px 20px;
            margin-bottom: 14px;
            min-height: 120px;
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            box-shadow: var(--shadow-glass);
        }

        .report-card-title {
            font-size: 15px;
            color: var(--text-muted);
            margin-bottom: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.6px;
        }

        .report-card-value {
            font-size: 28px;
            font-weight: 800;
            color: var(--text-main);
            line-height: 1.2;
            white-space: normal !important;
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
        }

        div[data-testid="stDataFrame"] {
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid var(--border-glass);
            box-shadow: var(--shadow-glass);
        }

        div[data-testid="stTable"] {
            border-radius: 18px;
            overflow: hidden;
        }

        .stSelectbox > div > div,
        .stMultiSelect > div > div,
        .stTextInput > div > div,
        .stNumberInput > div > div {
            background: rgba(41, 41, 41, 0.72) !important;
            border: 1px solid var(--border-glass) !important;
            border-radius: 14px !important;
            color: var(--text-main) !important;
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
        }

        .stSelectbox div,
        .stSlider div,
        .stFileUploader div {
            color: var(--text-main);
        }

        div[data-baseweb="select"] > div {
            background: rgba(41, 41, 41, 0.72) !important;
            border: 1px solid var(--border-glass) !important;
            border-radius: 14px !important;
            color: var(--text-main) !important;
        }

        div[data-baseweb="select"] span {
            color: var(--text-main) !important;
        }

        .stSlider [data-baseweb="slider"] div {
            color: var(--orange) !important;
        }

        .stSlider [role="slider"] {
            background-color: var(--orange) !important;
            border: 2px solid #FFB083 !important;
        }

        .stSlider div[data-testid="stTickBar"] {
            background: rgba(255, 255, 255, 0.18) !important;
        }

        button[kind="primary"],
        button[kind="secondary"],
        .stButton button {
            background: linear-gradient(135deg, var(--orange), #D95F24) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.16) !important;
            border-radius: 14px !important;
            font-weight: 700 !important;
            box-shadow: 0 12px 28px rgba(244, 122, 58, 0.25);
        }

        button:hover,
        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 16px 36px rgba(244, 122, 58, 0.36);
        }

        .fixed-download {
            position: fixed;
            top: 72px;
            right: 28px;
            z-index: 999999;
            background: rgba(41, 41, 41, 0.78);
            color: var(--text-main) !important;
            padding: 11px 17px;
            border-radius: 14px;
            text-decoration: none;
            font-weight: 800;
            border: 1px solid var(--orange-border);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            box-shadow: var(--shadow-glass);
        }

        .fixed-download:hover {
            background: linear-gradient(135deg, var(--orange), #D95F24);
            color: white !important;
            text-decoration: none;
        }

        div[data-testid="stAlert"] {
            background: rgba(41, 41, 41, 0.74);
            color: var(--text-main);
            border-radius: 16px;
            border: 1px solid var(--orange-border);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
        }

        div[data-testid="stExpander"] {
            background: rgba(41, 41, 41, 0.62);
            border: 1px solid var(--border-glass);
            border-radius: 16px;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
        }

        iframe {
            border-radius: 18px !important;
        }

        .js-plotly-plot {
            border-radius: 18px;
            background: rgba(41, 41, 41, 0.42);
            border: 1px solid var(--border-glass);
            padding: 10px;
            box-shadow: var(--shadow-glass);
        }

        hr {
            border-color: rgba(244, 122, 58, 0.35);
        }
        /* Fix metric text clipping */
div[data-testid="stMetric"] {
    width: 100% !important;
    overflow: visible !important;
}

div[data-testid="stMetric"] > div {
    overflow: visible !important;
}

div[data-testid="stMetricLabel"] {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
    font-size: 15px !important;
    line-height: 1.25 !important;
}

div[data-testid="stMetricValue"] {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
    word-break: normal !important;
    overflow-wrap: break-word !important;
    line-height: 1.15 !important;
    font-size: clamp(24px, 2.2vw, 38px) !important;
    max-width: 100% !important;
}

div[data-testid="stMetricValue"] > div {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
    word-break: normal !important;
    overflow-wrap: break-word !important;
    line-height: 1.15 !important;
}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Data loading
# ------------------------------------------------------------

@st.cache_data
def load_default_data() -> pd.DataFrame:
    possible_paths = [
        "Data/clean_nba_player_gamelog_2018_2022.csv",
        "data/clean_nba_player_gamelog_2018_2022.csv",
        "clean_nba_player_gamelog_2018_2022.csv",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return pd.read_csv(path)

    st.error(
        "Default dataset not found. Make sure `clean_nba_player_gamelog_2018_2022.csv` "
        "is inside the Data folder."
    )

    return pd.DataFrame()


@st.cache_data
def load_team_name_lookup() -> dict:
    team_lookup = {}

    teams_paths = [
        "Data/raw/teams.csv",
        "data/raw/teams.csv",
        "teams.csv",
    ]

    for path in teams_paths:
        if os.path.exists(path):
            teams_df = pd.read_csv(path)

            if "ABBREVIATION" in teams_df.columns:
                teams_df = teams_df.dropna(subset=["ABBREVIATION"]).copy()
                teams_df["ABBREVIATION"] = teams_df["ABBREVIATION"].astype(str).str.strip()

                if "CITY" in teams_df.columns and "NICKNAME" in teams_df.columns:
                    teams_df["DisplayName"] = (
                        teams_df["CITY"].astype(str).str.strip()
                        + " "
                        + teams_df["NICKNAME"].astype(str).str.strip()
                    )
                elif "NICKNAME" in teams_df.columns:
                    teams_df["DisplayName"] = teams_df["NICKNAME"].astype(str).str.strip()
                elif "CITY" in teams_df.columns:
                    teams_df["DisplayName"] = teams_df["CITY"].astype(str).str.strip()
                else:
                    teams_df["DisplayName"] = teams_df["ABBREVIATION"]

                teams_df = teams_df.drop_duplicates(subset=["ABBREVIATION"], keep="last")

                for _, row in teams_df.iterrows():
                    code = row["ABBREVIATION"]
                    name = row["DisplayName"]

                    if pd.notna(code) and pd.notna(name):
                        team_lookup[code] = name

            break

    games_details_paths = [
        "Data/raw/games_details.csv",
        "data/raw/games_details.csv",
        "games_details.csv",
    ]

    for path in games_details_paths:
        if os.path.exists(path):
            try:
                details_df = pd.read_csv(
                    path,
                    usecols=["TEAM_ABBREVIATION", "TEAM_CITY"],
                    low_memory=False,
                )

                details_df = details_df.dropna(subset=["TEAM_ABBREVIATION"]).copy()
                details_df["TEAM_ABBREVIATION"] = (
                    details_df["TEAM_ABBREVIATION"].astype(str).str.strip()
                )

                if "TEAM_CITY" in details_df.columns:
                    details_df["TEAM_CITY"] = details_df["TEAM_CITY"].astype(str).str.strip()
                    details_df = details_df.drop_duplicates(
                        subset=["TEAM_ABBREVIATION"],
                        keep="last",
                    )

                    for _, row in details_df.iterrows():
                        code = row["TEAM_ABBREVIATION"]
                        city = row["TEAM_CITY"]

                        if code not in team_lookup and pd.notna(city):
                            team_lookup[code] = city

            except ValueError:
                pass

            break

    return team_lookup


def validate_data(df: pd.DataFrame) -> list:
    required_columns = [
        "Player",
        "Team",
        "Date",
        "Opponent",
        "Minutes",
        "Points",
        "Rebounds",
        "Assists",
        "FieldGoalPct",
        "ThreePointPct",
        "FreeThrowPct",
        "Turnovers",
        "PlusMinus",
        "Result",
    ]

    return [col for col in required_columns if col not in df.columns]


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    numeric_columns = [
        "Minutes",
        "Points",
        "Rebounds",
        "Assists",
        "FieldGoalPct",
        "ThreePointPct",
        "FreeThrowPct",
        "Turnovers",
        "PlusMinus",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if "Production" not in df.columns:
        df["Production"] = (
            df["Points"]
            + df["Rebounds"]
            + df["Assists"]
            + df["PlusMinus"]
        )

    if "GameParticipation" not in df.columns:
        df["GameParticipation"] = np.where(df["Minutes"] > 0, 1, 0)

    return df.sort_values("Date")


# ------------------------------------------------------------
# Scoring logic
# ------------------------------------------------------------

def clamp_score(value: float, lower: float = 0, upper: float = 100) -> float:
    if pd.isna(value) or np.isinf(value):
        return 0
    return round(max(lower, min(upper, value)), 1)


def safe_mean(series: pd.Series) -> float:
    if series is None:
        return 0.0
    value = pd.to_numeric(series, errors="coerce").mean()
    return 0.0 if pd.isna(value) else float(value)


def safe_div(numerator: float, denominator: float) -> float:
    if pd.isna(numerator) or pd.isna(denominator) or denominator == 0:
        return 0.0
    return float(numerator) / float(denominator)


def calculate_workload_score(workload_ratio: float) -> float:
    if pd.isna(workload_ratio) or np.isinf(workload_ratio):
        return 60

    if 0.85 <= workload_ratio <= 1.15:
        return 100
    elif 0.70 <= workload_ratio < 0.85:
        return 75
    elif 1.15 < workload_ratio <= 1.30:
        return 75
    elif workload_ratio < 0.70:
        return 60
    else:
        return 55


def calculate_scores(
    player_df: pd.DataFrame,
    recent_window: int,
    metric_focus: str = "All-round",
) -> dict:
    player_df = player_df.sort_values("Date").copy()

    weight_profiles = {
        "All-round": {
            "Recent Form": 0.30,
            "Efficiency": 0.25,
            "Consistency": 0.25,
            "Workload Balance": 0.20,
        },
        "Scoring": {
            "Recent Form": 0.40,
            "Efficiency": 0.30,
            "Consistency": 0.20,
            "Workload Balance": 0.10,
        },
        "Efficiency": {
            "Recent Form": 0.20,
            "Efficiency": 0.45,
            "Consistency": 0.20,
            "Workload Balance": 0.15,
        },
        "Consistency": {
            "Recent Form": 0.20,
            "Efficiency": 0.20,
            "Consistency": 0.45,
            "Workload Balance": 0.15,
        },
        "Workload": {
            "Recent Form": 0.20,
            "Efficiency": 0.20,
            "Consistency": 0.20,
            "Workload Balance": 0.40,
        },
    }

    weights = weight_profiles.get(metric_focus, weight_profiles["All-round"])

    if player_df.empty:
        return {
            "Readiness Score": 0,
            "Recent Form": 0,
            "Efficiency": 0,
            "Consistency": 0,
            "Workload Balance": 0,
            "Recent Avg Production": 0,
            "Season Avg Production": 0,
            "Recent Avg Minutes": 0,
            "Season Avg Minutes": 0,
            "Workload Ratio": 0,
            "Participation Context": "No data available",
            "Recent Games Used": 0,
            "Metric Focus": metric_focus,
            "Weight Profile": weights,
        }

    recent_window = min(recent_window, len(player_df))
    recent_df = player_df.tail(recent_window)

    season_avg_production = player_df["Production"].mean()
    recent_avg_production = recent_df["Production"].mean()

    if season_avg_production > 0:
        recent_form_score = (recent_avg_production / season_avg_production) * 100
    else:
        recent_form_score = 50

    recent_form_score = clamp_score(recent_form_score)

    season_avg_minutes = player_df["Minutes"].mean()
    recent_avg_minutes = recent_df["Minutes"].mean()

    if season_avg_minutes > 0:
        workload_ratio = recent_avg_minutes / season_avg_minutes
    else:
        workload_ratio = 1

    workload_score = calculate_workload_score(workload_ratio)

    turnover_control = 100 - (recent_df["Turnovers"].mean() * 12)
    turnover_control = clamp_score(turnover_control)

    efficiency_score = (
        0.40 * recent_df["FieldGoalPct"].mean()
        + 0.25 * recent_df["ThreePointPct"].mean()
        + 0.20 * recent_df["FreeThrowPct"].mean()
        + 0.15 * turnover_control
    )
    efficiency_score = clamp_score(efficiency_score)

    recent_production_mean = recent_df["Production"].mean()
    recent_production_std = recent_df["Production"].std(ddof=0)

    if recent_production_mean > 0:
        coefficient_of_variation = recent_production_std / recent_production_mean
        consistency_score = 100 - (coefficient_of_variation * 100)
    else:
        consistency_score = 50

    consistency_score = clamp_score(consistency_score)

    readiness_score = (
        weights["Recent Form"] * recent_form_score
        + weights["Efficiency"] * efficiency_score
        + weights["Consistency"] * consistency_score
        + weights["Workload Balance"] * workload_score
    )

    readiness_score = clamp_score(readiness_score)

    participation_context = (
        f"{len(recent_df)} recorded game(s) used from selected recent window. "
        "Participation is shown as context only and is not included in the readiness score."
    )

    return {
        "Readiness Score": readiness_score,
        "Recent Form": recent_form_score,
        "Efficiency": efficiency_score,
        "Consistency": consistency_score,
        "Workload Balance": workload_score,
        "Recent Avg Production": round(recent_avg_production, 1),
        "Season Avg Production": round(season_avg_production, 1),
        "Recent Avg Minutes": round(recent_avg_minutes, 1),
        "Season Avg Minutes": round(season_avg_minutes, 1),
        "Workload Ratio": round(workload_ratio, 2),
        "Participation Context": participation_context,
        "Recent Games Used": len(recent_df),
        "Metric Focus": metric_focus,
        "Weight Profile": weights,
    }


def readiness_label(score: float) -> str:
    if score >= 80:
        return "High Readiness"
    elif score >= 65:
        return "Monitor"
    elif score >= 50:
        return "Manage Minutes / Controlled Role"
    else:
        return "Review Before Selection"


def card_class(status: str) -> str:
    if status == "High Readiness":
        return "green-box"
    elif status in ["Monitor", "Manage Minutes"]:
        return "amber-box"
    elif status == "Manage Minutes / Controlled Role":
        return "amber-box"
    else:
        return "red-box"


def rotation_recommendation(score: float) -> str:
    if score >= 80:
        return "Start / normal high involvement"
    elif score >= 65:
        return "Use normally, but monitor key alerts"
    elif score >= 50:
        return "Manage minutes / controlled role"
    else:
        return "Review before major involvement"


def readiness_interpretation_text(mode_note: str) -> str:
    return (
        "Readiness Score interpretation: This score is relative to the selected player’s own "
        "performance baseline. It compares recent form, efficiency, consistency, and workload "
        "balance against how this player usually performs in the selected season. A high score "
        "means the player is currently performing well compared with their expected role. It "
        "does not mean the player is better than every other player. "
        + mode_note
    )


def mode_help_text(mode: str) -> str:
    return {
        "Team Overview": "What this mode helps with: comparing team selection options and current lineup fit.",
        "Player Profile": "What this mode helps with: reviewing one player's season profile and recent form.",
        "Pre-Game Readiness": "What this mode helps with: supporting selection and role planning before the next game.",
        "Live Game Monitor": "What this mode helps with: guiding tactical choices during the game using live context.",
        "Post-Game Report": "What this mode helps with: turning the latest game into a next-step action plan.",
    }.get(mode, "")


def workload_alert(scores: dict) -> tuple:
    ratio = scores["Workload Ratio"]

    if ratio > 1.30:
        return "Very High Workload", "Review minutes and consider managing next-game load."
    elif ratio > 1.15:
        return "Elevated Workload", "Monitor minutes and avoid unnecessary extended load."
    elif ratio < 0.70:
        return "Very Low Recent Involvement", "Review role, rhythm, and match fitness context."
    elif ratio < 0.85:
        return "Reduced Involvement", "Monitor whether reduced minutes reflect role or performance trend."
    else:
        return "Stable Workload", "Minutes are close to the player’s normal baseline."


def efficiency_alert(scores: dict) -> tuple:
    efficiency = scores["Efficiency"]

    if efficiency >= 75:
        return "Strong Efficiency", "Shooting and turnover profile are currently strong."
    elif efficiency >= 60:
        return "Efficiency Monitor", "Efficiency is acceptable but should be monitored."
    else:
        return "Efficiency Review", "Review shot selection, decision-making, and turnover profile."


def consistency_alert(scores: dict) -> tuple:
    consistency = scores["Consistency"]

    if consistency >= 75:
        return "Reliable Output", "Recent production is relatively stable."
    elif consistency >= 60:
        return "Moderate Variation", "Recent production shows some game-to-game variation."
    else:
        return "High Variation", "Recent output is inconsistent and should be reviewed."


def final_coach_action(status: str, scores: dict) -> str:
    workload_status, _ = workload_alert(scores)
    efficiency_status, _ = efficiency_alert(scores)
    consistency_status, _ = consistency_alert(scores)

    alerts = []

    if workload_status in ["Very High Workload", "Elevated Workload"]:
        alerts.append("monitor workload")
    elif workload_status in ["Very Low Recent Involvement", "Reduced Involvement"]:
        alerts.append("review recent involvement")

    if efficiency_status == "Efficiency Review":
        alerts.append("review efficiency")
    elif efficiency_status == "Efficiency Monitor":
        alerts.append("monitor efficiency")

    if consistency_status == "High Variation":
        alerts.append("review consistency")
    elif consistency_status == "Moderate Variation":
        alerts.append("monitor consistency")

    if status == "High Readiness":
        if alerts:
            return "Available for normal involvement, but " + ", ".join(alerts) + "."
        return "Available for normal or high involvement."
    elif status == "Monitor":
        if alerts:
            return "Available, but coaching staff should " + ", ".join(alerts) + "."
        return "Available, but continue monitoring recent performance indicators."
    elif status == "Manage Minutes":
        if alerts:
            return "Use with managed minutes and " + ", ".join(alerts) + "."
        return "Use with managed minutes and review current role."
    else:
        if alerts:
            return "Review before major involvement and " + ", ".join(alerts) + "."
        return "Review before major involvement."


def make_summary_csv(summary_dict: dict) -> bytes:
    return pd.DataFrame([summary_dict]).to_csv(index=False).encode("utf-8")


def fixed_download_link(data: bytes, file_name: str, label: str = "Download CSV") -> None:
    b64 = base64.b64encode(data).decode()

    href = f"""
    <a class="fixed-download" href="data:text/csv;base64,{b64}" download="{file_name}">
        {label}
    </a>
    """

    st.markdown(href, unsafe_allow_html=True)


# ------------------------------------------------------------
# Team and player summaries
# ------------------------------------------------------------

def get_team_summary(df: pd.DataFrame, team: str) -> dict:
    if team == "All":
        team_df = df.copy()
    else:
        team_df = df[df["Team"] == team].copy()

    if team_df.empty:
        return {}

    needed_columns = ["Date", "Team", "Opponent", "Result"]

    if "Team_Points" in team_df.columns and "Opponent_Points" in team_df.columns:
        needed_columns += ["Team_Points", "Opponent_Points"]
        games_df = team_df[needed_columns].drop_duplicates().sort_values("Date")

        games_played = len(games_df)
        wins = (games_df["Result"] == "W").sum()
        losses = (games_df["Result"] == "L").sum()
        win_pct = (wins / games_played) * 100 if games_played > 0 else 0

        avg_team_points = games_df["Team_Points"].mean()
        avg_opp_points = games_df["Opponent_Points"].mean()
        avg_margin = (games_df["Team_Points"] - games_df["Opponent_Points"]).mean()
    else:
        games_df = team_df[needed_columns].drop_duplicates().sort_values("Date")

        games_played = len(games_df)
        wins = (games_df["Result"] == "W").sum()
        losses = (games_df["Result"] == "L").sum()
        win_pct = (wins / games_played) * 100 if games_played > 0 else 0

        avg_team_points = np.nan
        avg_opp_points = np.nan
        avg_margin = np.nan

    return {
        "Games Played": games_played,
        "Wins": wins,
        "Losses": losses,
        "Win %": round(win_pct, 1),
        "Avg Team Points": round(avg_team_points, 1) if not pd.isna(avg_team_points) else "N/A",
        "Avg Opponent Points": round(avg_opp_points, 1) if not pd.isna(avg_opp_points) else "N/A",
        "Avg Margin": round(avg_margin, 1) if not pd.isna(avg_margin) else "N/A",
        "Games Data": games_df,
        "Team Data": team_df,
    }


def get_player_summary(df: pd.DataFrame, player: str) -> dict:
    player_df = df[df["Player"] == player].copy()

    if player_df.empty:
        return {}

    return {
        "Games": len(player_df),
        "Avg Minutes": round(player_df["Minutes"].mean(), 1),
        "PPG": round(player_df["Points"].mean(), 1),
        "RPG": round(player_df["Rebounds"].mean(), 1),
        "APG": round(player_df["Assists"].mean(), 1),
        "FG%": round(player_df["FieldGoalPct"].mean(), 1),
        "3P%": round(player_df["ThreePointPct"].mean(), 1),
        "FT%": round(player_df["FreeThrowPct"].mean(), 1),
        "Turnovers": round(player_df["Turnovers"].mean(), 1),
        "PlusMinus": round(player_df["PlusMinus"].mean(), 1),
        "Player Data": player_df.sort_values("Date"),
    }


def safe_series(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        return pd.Series(dtype=float)
    return pd.to_numeric(df[column], errors="coerce")


def percentile_score(series: pd.Series, value, inverse: bool = False) -> float:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty or pd.isna(value):
        return 50.0
    if clean.nunique() <= 1:
        return 50.0
    # Use count of values at or below the target for a stable 0-100 percentile-like score.
    pct = float((clean.le(value).mean()) * 100)
    if inverse:
        pct = 100 - pct
    return pct


def classify_player_role(player_row_or_df):
    if isinstance(player_row_or_df, pd.DataFrame):
        row = player_row_or_df.iloc[-1]
    else:
        row = player_row_or_df

    points_pm = float(row.get("Points Per Minute", 0) or 0)
    rebounds_pm = float(row.get("Rebounds Per Minute", 0) or 0)
    assists_pm = float(row.get("Assists Per Minute", 0) or 0)
    turnovers_pm = float(row.get("Turnovers Per Minute", 0) or 0)
    three_pct = float(row.get("ThreePointPct", 0) or 0)
    fg_pct = float(row.get("FieldGoalPct", 0) or 0)
    plus_minus = float(row.get("PlusMinus", 0) or 0)
    avg_minutes = float(row.get("Avg Minutes", 0) or 0)

    if rebounds_pm >= max(0.12, assists_pm * 0.9) and (three_pct <= 25 or three_pct == 0):
        return "Rebounder / Interior"
    if three_pct >= 33 and points_pm >= 0.25:
        return "Floor Spacer"
    if assists_pm >= max(0.12, rebounds_pm) and turnovers_pm <= 0.10:
        return "Playmaker"
    if points_pm >= 0.28 and fg_pct >= 45:
        return "Scorer"
    if plus_minus >= 0 and turnovers_pm <= 0.12 and avg_minutes >= 18:
        return "Stabiliser"
    return "Balanced Contributor"


def role_logic_summary() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Role": "Scorer",
                "Primary signals": "Points per minute, production per minute, FG%, 3PT% if relevant",
            },
            {
                "Role": "Playmaker",
                "Primary signals": "Assists per minute, turnover control, plus-minus, production",
            },
            {
                "Role": "Rebounder / Interior",
                "Primary signals": "Rebounds per minute, FG%, plus-minus, production",
            },
            {
                "Role": "Floor Spacer",
                "Primary signals": "3PT%, points per minute, FG%, plus-minus",
            },
            {
                "Role": "Stabiliser",
                "Primary signals": "Plus-minus, low turnovers, consistency, minutes",
            },
            {
                "Role": "Balanced Contributor",
                "Primary signals": "Production, plus-minus, minutes, multi-category stability",
            },
        ]
    )


def suggested_team_use(role: str) -> str:
    mapping = {
        "Scorer": "Use when the team needs shot creation or quick scoring.",
        "Playmaker": "Use when the team needs ball movement and controlled possessions.",
        "Rebounder / Interior": "Use when rebounding, interior presence, or efficient finishing is the priority.",
        "Floor Spacer": "Use to improve spacing and three-point threat.",
        "Stabiliser": "Use to protect structure, reduce mistakes, and stabilise impact.",
        "Balanced Contributor": "Use as a flexible option across multiple lineup needs.",
    }
    return mapping.get(role, "Use as a flexible lineup option.")


def calculate_team_selection_fit(team_df: pd.DataFrame, recent_window: int = 10) -> pd.DataFrame:
    if team_df.empty:
        return pd.DataFrame()

    team_df = team_df.copy()
    if "Production" not in team_df.columns:
        team_df["Production"] = (
            safe_series(team_df, "Points").fillna(0)
            + safe_series(team_df, "Rebounds").fillna(0)
            + safe_series(team_df, "Assists").fillna(0)
            + safe_series(team_df, "PlusMinus").fillna(0)
        )

    rows = []
    for player in sorted(team_df["Player"].dropna().unique()):
        player_data = team_df[team_df["Player"] == player].sort_values("Date").copy()
        if player_data.empty:
            continue

        recent_data = player_data.tail(min(recent_window, len(player_data)))
        minutes = safe_series(player_data, "Minutes").fillna(0)
        recent_minutes = safe_series(recent_data, "Minutes").fillna(0)
        production = safe_series(player_data, "Production").fillna(0)
        recent_production = safe_series(recent_data, "Production").fillna(0)
        points = safe_series(player_data, "Points").fillna(0)
        rebounds = safe_series(player_data, "Rebounds").fillna(0)
        assists = safe_series(player_data, "Assists").fillna(0)
        turnovers = safe_series(player_data, "Turnovers").fillna(0)
        plus_minus = safe_series(player_data, "PlusMinus").fillna(0)
        fg = safe_series(player_data, "FieldGoalPct")
        three = safe_series(player_data, "ThreePointPct")

        total_minutes = minutes.sum()
        total_recent_minutes = recent_minutes.sum()

        ppm = safe_div(points.sum(), total_minutes)
        rpm = safe_div(rebounds.sum(), total_minutes)
        apm = safe_div(assists.sum(), total_minutes)
        tovpm = safe_div(turnovers.sum(), total_minutes)
        prodpm = safe_div(production.sum(), total_minutes)
        recent_prodpm = safe_div(recent_production.sum(), total_recent_minutes)
        season_prodpm = prodpm
        recent_minutes_avg = safe_mean(recent_minutes)
        season_minutes_avg = safe_mean(minutes)

        role = classify_player_role(
            {
                "Points Per Minute": ppm,
                "Rebounds Per Minute": rpm,
                "Assists Per Minute": apm,
                "Turnovers Per Minute": tovpm,
                "ThreePointPct": safe_mean(three) if len(three.dropna()) > 0 else 0,
                "FieldGoalPct": safe_mean(fg) if len(fg.dropna()) > 0 else 0,
                "PlusMinus": safe_mean(plus_minus),
                "Avg Minutes": season_minutes_avg,
            }
        )

        if role == "Scorer":
            perf = (
                0.35 * percentile_score(team_df.groupby("Player")["Points"].mean(), points.mean())
                + 0.30 * percentile_score(team_df.groupby("Player")["Production"].mean(), production.mean())
                + 0.20 * percentile_score(team_df.groupby("Player")["FieldGoalPct"].mean(), safe_mean(fg))
                + 0.15 * percentile_score(team_df.groupby("Player")["ThreePointPct"].mean(), safe_mean(three))
            )
            main_strength = "Shot creation and scoring"
        elif role == "Playmaker":
            perf = (
                0.35 * percentile_score(team_df.groupby("Player")["Assists"].mean(), assists.mean())
                + 0.25 * percentile_score(team_df.groupby("Player")["Turnovers"].mean(), turnovers.mean(), inverse=True)
                + 0.20 * percentile_score(team_df.groupby("Player")["PlusMinus"].mean(), safe_mean(plus_minus))
                + 0.20 * percentile_score(team_df.groupby("Player")["Production"].mean(), production.mean())
            )
            main_strength = "Ball movement"
        elif role == "Rebounder / Interior":
            perf = (
                0.40 * percentile_score(team_df.groupby("Player")["Rebounds"].mean(), rebounds.mean())
                + 0.25 * percentile_score(team_df.groupby("Player")["FieldGoalPct"].mean(), safe_mean(fg))
                + 0.20 * percentile_score(team_df.groupby("Player")["PlusMinus"].mean(), safe_mean(plus_minus))
                + 0.15 * percentile_score(team_df.groupby("Player")["Production"].mean(), production.mean())
            )
            main_strength = "Rebounding and interior impact"
        elif role == "Floor Spacer":
            perf = (
                0.40 * percentile_score(team_df.groupby("Player")["ThreePointPct"].mean(), safe_mean(three))
                + 0.25 * percentile_score(team_df.groupby("Player")["Points"].mean(), points.mean())
                + 0.20 * percentile_score(team_df.groupby("Player")["FieldGoalPct"].mean(), safe_mean(fg))
                + 0.15 * percentile_score(team_df.groupby("Player")["PlusMinus"].mean(), safe_mean(plus_minus))
            )
            main_strength = "Spacing and shooting threat"
        elif role == "Stabiliser":
            perf = (
                0.35 * percentile_score(team_df.groupby("Player")["PlusMinus"].mean(), safe_mean(plus_minus))
                + 0.25 * percentile_score(team_df.groupby("Player")["Turnovers"].mean(), turnovers.mean(), inverse=True)
                + 0.20 * percentile_score(team_df.groupby("Player")["Production"].mean(), production.mean())
                + 0.20 * percentile_score(team_df.groupby("Player")["Minutes"].mean(), season_minutes_avg)
            )
            main_strength = "Structure and low-error impact"
        else:
            perf = (
                0.30 * percentile_score(team_df.groupby("Player")["Production"].mean(), production.mean())
                + 0.25 * percentile_score(team_df.groupby("Player")["PlusMinus"].mean(), safe_mean(plus_minus))
                + 0.25 * percentile_score(team_df.groupby("Player")["Minutes"].mean(), season_minutes_avg)
                + 0.20 * percentile_score(team_df.groupby("Player")["Rebounds"].mean(), rebounds.mean() + assists.mean())
            )
            main_strength = "Two-way flexibility"

        team_players = team_df.groupby("Player")
        avg_minutes_pct = percentile_score(team_players["Minutes"].mean(), season_minutes_avg)
        games_played = len(player_data)
        games_pct = percentile_score(team_players.size(), games_played)
        coach_usage = 0.60 * avg_minutes_pct + 0.40 * games_pct

        recent_prodpm_pct = percentile_score(team_players["Production"].mean(), recent_prodpm)
        season_prodpm_pct = percentile_score(team_players["Production"].mean(), season_prodpm)
        recent_form = clamp_score(0.5 * recent_prodpm_pct + 0.5 * season_prodpm_pct)

        if season_minutes_avg > 0:
            workload_ratio = recent_minutes_avg / season_minutes_avg
        else:
            workload_ratio = 1
        if 0.85 <= workload_ratio <= 1.15:
            workload_stability = 100
        elif 0.70 <= workload_ratio < 0.85 or 1.15 < workload_ratio <= 1.30:
            workload_stability = 75
        elif workload_ratio < 0.70:
            workload_stability = 60
        else:
            workload_stability = 55

        consistency_std = production.tail(min(recent_window, len(production))).std()
        if pd.isna(consistency_std):
            consistency_std = 0.0
        consistency_score = clamp_score(100 - (consistency_std * 1.5))

        role_adj = clamp_score(perf)
        fit_score = clamp_score(
            0.35 * role_adj
            + 0.20 * recent_form
            + 0.20 * coach_usage
            + 0.15 * workload_stability
            + 0.10 * consistency_score
        )

        rows.append(
            {
                "Player": player,
                "Role": role,
                "Team Selection Fit Score": round(fit_score, 1),
                "Avg Minutes": round(season_minutes_avg, 1),
                "Games Played": games_played,
                "Production Per Minute": round(prodpm, 3),
                "Main Strength": main_strength,
                "Coach Usage Score": round(coach_usage, 1),
                "Role-Adjusted Performance": round(role_adj, 1),
                "Suggested Team Use": suggested_team_use(role),
            }
        )

    if not rows:
        return pd.DataFrame()

    result = pd.DataFrame(rows)
    return result.sort_values("Team Selection Fit Score", ascending=False)


# ------------------------------------------------------------
# Live and post-game logic
# ------------------------------------------------------------

def live_game_decision(
    current_minutes: float,
    current_points: int,
    current_rebounds: int,
    current_assists: int,
    current_turnovers: int,
    current_plus_minus: int,
    coach_concern: int,
    baseline_minutes: float,
) -> dict:
    live_contribution = (
        current_points
        + current_rebounds
        + current_assists
        + current_plus_minus
        - current_turnovers
    )

    if baseline_minutes > 0:
        load_ratio = current_minutes / baseline_minutes
    else:
        load_ratio = 1

    alerts = []

    if load_ratio > 1.15:
        load_status = "Elevated live workload"
        alerts.append("Current minutes are above the player’s normal baseline.")
    elif load_ratio < 0.70:
        load_status = "Low live involvement"
        alerts.append("Current minutes are below the player’s normal involvement.")
    else:
        load_status = "Stable live workload"

    if current_turnovers >= 4:
        alerts.append("Turnovers are high and decision-making should be reviewed.")

    if current_plus_minus <= -10:
        alerts.append("Negative plus-minus suggests current lineup or matchup concern.")

    if coach_concern >= 8:
        alerts.append("Coach concern level is high.")

    if len(alerts) == 0:
        action = "Continue normal involvement."
    elif coach_concern >= 8 or current_plus_minus <= -10:
        action = "Review current role and consider rotation adjustment."
    elif load_ratio > 1.15:
        action = "Monitor minutes and consider short rest."
    else:
        action = "Continue involvement but monitor alerts."

    return {
        "Live Contribution": live_contribution,
        "Load Status": load_status,
        "Alerts": alerts,
        "Action": action,
        "Load Ratio": round(load_ratio, 2),
    }


def post_game_impact(
    pg_minutes: float,
    pg_points: int,
    pg_rebounds: int,
    pg_assists: int,
    pg_turnovers: int,
    pg_plus_minus: int,
    baseline: dict,
) -> dict:
    pg_production = pg_points + pg_rebounds + pg_assists + pg_plus_minus

    baseline_production = (
        baseline["Points"]
        + baseline["Rebounds"]
        + baseline["Assists"]
        + baseline["Plus-Minus"]
    )

    if pg_production > baseline_production * 1.15:
        impact = "Positive Impact"
    elif pg_production < baseline_production * 0.85:
        impact = "Below Baseline Impact"
    else:
        impact = "Near Baseline Impact"

    if pg_minutes > baseline["Minutes"] * 1.15:
        workload = "Elevated workload"
    elif pg_minutes < baseline["Minutes"] * 0.85:
        workload = "Reduced workload"
    else:
        workload = "Normal workload"

    if pg_turnovers > baseline["Turnovers"] * 1.25:
        efficiency_note = "Turnover concern"
    else:
        efficiency_note = "Turnovers within expected range"

    if impact == "Positive Impact" and workload == "Normal workload":
        recommendation = "Maintain role or involvement level."
    elif workload == "Elevated workload":
        recommendation = "Consider recovery-focused follow-up or monitor next-game minutes."
    elif efficiency_note == "Turnover concern":
        recommendation = "Review decision-making and ball security."
    elif impact == "Below Baseline Impact":
        recommendation = "Review role, matchup, or recent form trend."
    else:
        recommendation = "Continue monitoring next performance."

    return {
        "Game Production": pg_production,
        "Game Impact": impact,
        "Workload": workload,
        "Efficiency Flag": efficiency_note,
        "Recommendation": recommendation,
    }


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

st.markdown(
    '<div class="main-title">Basketball Performance Readiness Dashboard</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">Coach-facing performance readiness, workload, efficiency, and decision-support tool.</div>',
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Sidebar and setup
# ------------------------------------------------------------

st.sidebar.header("Controls")

tool_mode = st.sidebar.selectbox(
    "Tool mode",
    [
        "Choose tool mode",
        "Team Overview",
        "Player Profile",
        "Pre-Game Readiness",
        "Live Game Monitor",
        "Post-Game Report",
        "Upload Custom CSV / Data Check",
        "Documentation / Interpretation",
    ],
)

if tool_mode == "Choose tool mode":
    st.info("Choose a tool mode from the sidebar to begin.")
    st.stop()


# ------------------------------------------------------------
# Upload custom CSV mode
# ------------------------------------------------------------

if tool_mode == "Upload Custom CSV / Data Check":
    st.subheader("Upload Custom CSV / Data Check")
    st.write(
        "Use this mode to test whether a custom CSV file matches the dashboard format. "
        "The main dashboard modes use the cleaned NBA dataset by default."
    )

    uploaded_file = st.file_uploader("Upload custom CSV", type=["csv"])

    if uploaded_file is None:
        st.info("Upload a CSV file to validate its structure.")
        st.stop()

    data = pd.read_csv(uploaded_file)

    if data.empty:
        st.error("The uploaded CSV is empty.")
        st.stop()

    missing_columns = validate_data(data)

    if missing_columns:
        st.error("The uploaded dataset is missing the following required columns:")
        st.write(missing_columns)
        st.stop()

    data = prepare_data(data)

    st.success("CSV structure is valid.")

    st.write("### Uploaded Data Preview")
    st.dataframe(data.head(20), use_container_width=True)

    st.write("### Dataset Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", len(data))
    col2.metric("Players", data["Player"].nunique())
    col3.metric("Teams", data["Team"].nunique())

    fixed_download_link(
        data=data.head(100).to_csv(index=False).encode("utf-8"),
        file_name="uploaded_data_preview.csv",
        label="Download Preview",
    )

    st.stop()


# ------------------------------------------------------------
# Documentation mode
# ------------------------------------------------------------

if tool_mode == "Documentation / Interpretation":
    st.subheader("Tool Documentation / Interpretation")

    st.write("### Tool Purpose")
    st.write(
        "The Basketball Performance Readiness Dashboard is a coach-facing sports analytics tool designed to support player selection, rotation planning, workload review, and post-game performance interpretation."
    )

    st.write("### Readiness Score Methodology")
    st.info(
        "The Readiness Score is a player-relative performance-readiness index. It compares a player’s recent output against that player’s own season baseline. It is designed to support coach-facing decisions around selection, role planning, workload support, and post-game review. It is not an absolute ranking of player quality and it is not an injury or medical prediction model."
    )

    st.write("### Variables Used")
    variables_df = pd.DataFrame(
        [
            {
                "Component": "Recent Form",
                "Variables Used": "Points, Rebounds, Assists, PlusMinus, Production",
                "Purpose": "Measures whether recent output is above or below the player’s normal baseline.",
            },
            {
                "Component": "Efficiency",
                "Variables Used": "FieldGoalPct, ThreePointPct, FreeThrowPct, Turnovers",
                "Purpose": "Measures shooting quality and possession control.",
            },
            {
                "Component": "Consistency",
                "Variables Used": "Production over recent games",
                "Purpose": "Measures stability of recent output.",
            },
            {
                "Component": "Workload Balance",
                "Variables Used": "Minutes",
                "Purpose": "Measures whether recent minutes are stable compared with the player’s normal role.",
            },
        ]
    )
    st.dataframe(variables_df, use_container_width=True)

    with st.expander("Readiness Score formulas", expanded=True):
        st.write("### Production Calculation")
        st.write(
            "If the dataset does not already include Production, the app creates it as a simple box-score style indicator."
        )
        st.code("Production = Points + Rebounds + Assists + PlusMinus")
        st.write(
            "If Production is missing in the imported data, the app uses that formula before building the readiness components."
        )

        st.write("### Recent Form Formula")
        st.code(
            "Recent Form Score = Recent Average Production / Season Average Production × 100"
        )
        st.write(
            "Recent Average Production is the average Production over the selected recent-game window. Season Average Production is the average Production over the selected season. A score of 100 means the player is matching their normal production baseline. Above 100 means recent production is above baseline, but the final score is capped at 100. Below 100 means recent production is below baseline."
        )

        st.write("### Efficiency Formula")
        st.code(
            "Efficiency Score = 40% FieldGoalPct + 25% ThreePointPct + 20% FreeThrowPct + 15% Turnover Control"
        )
        st.code("Turnover Control = 100 - Average Turnovers × 12")
        st.write(
            "Higher shooting percentages improve the score. More turnovers reduce the turnover control component. If a percentage column is missing, the app handles it safely and uses the available metrics."
        )

        st.write("### Consistency Formula")
        st.code("Coefficient of Variation = Standard Deviation of Recent Production / Average Recent Production")
        st.code("Consistency Score = 100 - Coefficient of Variation × 100")
        st.write(
            "Stable production across recent games creates a higher score. Highly variable production creates a lower score. Consistency does not mean games played; it means stability of output in the selected recent window."
        )

        st.write("### Workload Balance Formula")
        st.code("Workload Ratio = Recent Average Minutes / Season Average Minutes")
        workload_table = pd.DataFrame(
            [
                {"Workload Ratio Range": "0.85-1.15", "Workload Balance Score": 100, "Interpretation": "Stable workload"},
                {"Workload Ratio Range": "0.70-0.84", "Workload Balance Score": 75, "Interpretation": "Reduced involvement"},
                {"Workload Ratio Range": "1.16-1.30", "Workload Balance Score": 75, "Interpretation": "Elevated workload"},
                {"Workload Ratio Range": "Below 0.70", "Workload Balance Score": 60, "Interpretation": "Very low involvement"},
                {"Workload Ratio Range": "Above 1.30", "Workload Balance Score": 55, "Interpretation": "Very high workload"},
            ]
        )
        st.dataframe(workload_table, use_container_width=True)
        st.write(
            "The workload score does not simply reward more minutes. It rewards a stable workload compared with the player’s own usual role."
        )

        st.write("### Final Readiness Score")
        st.code(
            "Readiness Score = Recent Form Weight × Recent Form Score + Efficiency Weight × Efficiency Score + Consistency Weight × Consistency Score + Workload Weight × Workload Balance Score"
        )
        st.write(
            "The final score combines the component scores using the selected Metric Focus."
        )
        st.write("### Validation Examples")
        validation_df = pd.DataFrame(
            [
                {
                    "Example": "Specialist rebounder",
                    "Expected interpretation": "A player with strong rebounds, minutes, and interior efficiency can score well even if 3PT% is low or zero, because the role logic does not over-weight spacing for that role.",
                },
                {
                    "Example": "High-minute starter with poor recent form",
                    "Expected interpretation": "A starter can score lower if recent production, consistency, or workload stability falls below the season baseline, even if the season averages remain strong.",
                },
            ]
        )
        st.dataframe(validation_df, use_container_width=True)

    st.write("### Metric Focus Weight Profiles")
    focus_df = pd.DataFrame(
        [
            {
                "Metric Focus": "All-round",
                "Recent Form": "30%",
                "Efficiency": "25%",
                "Consistency": "25%",
                "Workload Balance": "20%",
            },
            {
                "Metric Focus": "Scoring",
                "Recent Form": "40%",
                "Efficiency": "30%",
                "Consistency": "20%",
                "Workload Balance": "10%",
            },
            {
                "Metric Focus": "Efficiency",
                "Recent Form": "20%",
                "Efficiency": "45%",
                "Consistency": "20%",
                "Workload Balance": "15%",
            },
            {
                "Metric Focus": "Consistency",
                "Recent Form": "20%",
                "Efficiency": "20%",
                "Consistency": "45%",
                "Workload Balance": "15%",
            },
            {
                "Metric Focus": "Workload",
                "Recent Form": "20%",
                "Efficiency": "20%",
                "Consistency": "20%",
                "Workload Balance": "40%",
            },
        ]
    )
    st.dataframe(focus_df, use_container_width=True)

    st.write("### Readiness Thresholds")
    threshold_df = pd.DataFrame(
        [
            {
                "Score Range": "80-100",
                "Threshold": "High Readiness",
                "Interpretation": "Above or close to the player’s strongest recent role level.",
            },
            {
                "Score Range": "65-79",
                "Threshold": "Monitor",
                "Interpretation": "One or more components need attention.",
            },
            {
                "Score Range": "50-64",
                "Threshold": "Manage Minutes / Controlled Role",
                "Interpretation": "Role or workload should be managed.",
            },
            {
                "Score Range": "Below 50",
                "Threshold": "Review Before Selection",
                "Interpretation": "Recent indicators are below expected baseline.",
            },
        ]
    )
    st.dataframe(threshold_df, use_container_width=True)
    st.info(
        "These thresholds are interpreted relative to the player’s own baseline. A high score means the player is performing strongly compared with their expected role. It does not mean the player is the best player on the team."
    )

    st.write("### Important Interpretation Note")
    st.warning(
        "A low-minute or specialist player can receive a strong readiness score if they are performing well compared with their normal role. Equally, a high-minute starter can receive a lower score if recent form, efficiency, consistency, or workload balance drops below their usual baseline. The score supports coach judgement rather than replacing it."
    )

    st.write("### How the score supports coaching decisions")
    st.write(
        "Use the score to support selection and role planning before the next game, to contextualise live tactical decisions, and to guide post-game follow-up on training, film review, and role adjustment."
    )

    st.write("### Important Limitation")
    st.warning(
        "This tool is not a medical or injury prediction model. It uses basketball game-log indicators to support performance-readiness decisions."
    )

    st.stop()


# ------------------------------------------------------------
# Default dataset setup for dashboard modes
# ------------------------------------------------------------

data = load_default_data()

if data is None or data.empty:
    st.error("No default data loaded. Check that the cleaned CSV is inside the Data folder.")
    st.stop()

missing_columns = validate_data(data)

if missing_columns:
    st.error("The dataset is missing the following required columns:")
    st.write(missing_columns)
    st.stop()

data = prepare_data(data)
team_name_lookup = load_team_name_lookup()


# ------------------------------------------------------------
# Required sidebar selections
# ------------------------------------------------------------

if "Season" in data.columns:
    season_values = sorted(data["Season"].dropna().unique().tolist())
    season_options = ["Choose season"] + season_values
    selected_season = st.sidebar.selectbox("Season", season_options)

    if selected_season == "Choose season":
        st.info("Choose a season from the sidebar to continue.")
        st.stop()

    data = data[data["Season"] == selected_season].copy()
else:
    selected_season = "All"

team_codes = sorted(data["Team"].dropna().unique().tolist())

team_display_map = {}

for team in team_codes:
    team_name = team_name_lookup.get(team, team)
    display_name = f"{team_name} ({team})"
    team_display_map[display_name] = team

team_display_options = ["Choose team"] + sorted(team_display_map.keys())

selected_team_display = st.sidebar.selectbox("Team", team_display_options)

if selected_team_display == "Choose team":
    st.info("Choose a team from the sidebar to continue.")
    st.stop()

selected_team = team_display_map[selected_team_display]
team_filtered_data = data[data["Team"] == selected_team].copy()

selected_player = None
player_df = pd.DataFrame()
scores = None
status = None
rotation_action = None
workload_status = None
workload_action = None
efficiency_status = None
efficiency_action = None
consistency_status = None
consistency_action = None
coach_action = None
metric_focus = "All-round"


# ------------------------------------------------------------
# Main-page settings
# ------------------------------------------------------------

if tool_mode == "Team Overview":
    st.write("### Team Overview Settings")

    recent_window = st.slider(
        "Recent games used for player readiness ranking",
        min_value=3,
        max_value=15,
        value=5,
        step=1,
    )

else:
    player_options = sorted(team_filtered_data["Player"].dropna().unique().tolist())

    if len(player_options) == 0:
        st.warning("No players available for the selected filters.")
        st.stop()

    player_options = ["Choose player"] + player_options
    selected_player = st.sidebar.selectbox("Player", player_options)

    if selected_player == "Choose player":
        st.info("Choose a player from the sidebar to continue.")
        st.stop()

    st.write("### Analysis Settings")

    col_setting_1, col_setting_2 = st.columns(2)

    with col_setting_1:
        recent_window = st.slider(
            "Recent games",
            min_value=3,
            max_value=15,
            value=5,
            step=1,
        )

    with col_setting_2:
        metric_focus = st.selectbox(
            "Metric focus",
            ["All-round", "Scoring", "Efficiency", "Consistency", "Workload"],
        )

    player_df = team_filtered_data[team_filtered_data["Player"] == selected_player].copy()

    if player_df.empty:
        st.warning("No data available for selected player.")
        st.stop()

    scores = calculate_scores(player_df, recent_window, metric_focus)
    status = readiness_label(scores["Readiness Score"])
    rotation_action = rotation_recommendation(scores["Readiness Score"])
    workload_status, workload_action = workload_alert(scores)
    efficiency_status, efficiency_action = efficiency_alert(scores)
    consistency_status, consistency_action = consistency_alert(scores)
    coach_action = final_coach_action(status, scores)


# ------------------------------------------------------------
# Mode: Team Overview
# ------------------------------------------------------------

if tool_mode == "Team Overview":
    st.subheader("Team Overview Mode")
    st.write(
        "This mode provides a team-level performance summary, recent game context, "
        "and player readiness ranking."
    )

    team_summary = get_team_summary(data, selected_team)

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

        if "Team_Points" in recent_games.columns and "Opponent_Points" in recent_games.columns:
            recent_games["Margin"] = (
                recent_games["Team_Points"] - recent_games["Opponent_Points"]
            )

            st.dataframe(
                recent_games[
                    ["Date", "Opponent", "Result", "Team_Points", "Opponent_Points", "Margin"]
                ],
                use_container_width=True,
            )

            fig_recent_games = px.bar(
                recent_games,
                x="Date",
                y="Margin",
                color="Result",
                title="Recent Game Margins",
            )
            st.plotly_chart(fig_recent_games, use_container_width=True)
        else:
            st.dataframe(recent_games, use_container_width=True)

        st.write("### Team Selection Fit Ranking")
        st.info(
            "Team Selection Fit is different from the individual Readiness Score. Individual readiness compares a player against their own baseline. Team Selection Fit compares players within the team context and adjusts for role, average minutes, games played, and role-specific strengths. This avoids unfairly penalising specialists, such as rebounders or interior players, for metrics that are less central to their role."
        )
        st.caption(
            "Team Selection Fit is a team-context ranking that compares players inside the selected team and adjusts for role, usage, workload stability, and consistency."
        )

        team_fit_table = calculate_team_selection_fit(team_summary["Team Data"], recent_window)

        if team_fit_table.empty:
            st.warning("Not enough player data to calculate team selection fit ranking.")
        else:
            st.caption(mode_help_text("Team Overview"))
            st.info(
                "Team Selection Fit is a team-context view. It compares players within the selected team, adjusts for role, and highlights who is currently the strongest fit for selection."
            )
            with st.expander("How the role logic works", expanded=False):
                st.caption("The app classifies each player into a role, then emphasizes the metrics that matter most for that role.")
                st.dataframe(role_logic_summary(), use_container_width=True)

            display_table = team_fit_table.copy()
            display_table.insert(0, "Rank", range(1, len(display_table) + 1))
            st.dataframe(
                display_table[
                    [
                        "Rank",
                        "Player",
                        "Role",
                        "Team Selection Fit Score",
                        "Avg Minutes",
                        "Games Played",
                        "Production Per Minute",
                        "Main Strength",
                        "Coach Usage Score",
                        "Role-Adjusted Performance",
                        "Suggested Team Use",
                    ]
                ],
                use_container_width=True,
            )

            top_players = display_table.head(5)

            fig_players = px.bar(
                top_players,
                x="Player",
                y="Team Selection Fit Score",
                text="Team Selection Fit Score",
                title="Top 5 Team Selection Fit Scores",
                hover_data={
                    "Role": True,
                    "Avg Minutes": ":.1f",
                    "Games Played": True,
                    "Main Strength": True,
                },
            )
            st.plotly_chart(fig_players, use_container_width=True)

            top_player = display_table.iloc[0]
            team_insight = (
                f"Top fit: {top_player['Player']} ({top_player['Role']}) with a score of {top_player['Team Selection Fit Score']}. "
                f"This is the clearest current selection option in the team context."
            )

            st.markdown(
                f"""
                <div class="info-box">
                    <b>Main Coach Takeaway:</b><br>
                    {team_insight}
                </div>
                """,
                unsafe_allow_html=True,
            )

            fixed_download_link(
                data=display_table.to_csv(index=False).encode("utf-8"),
                file_name=f"{selected_team}_team_selection_fit_table.csv",
                label="Download Team Selection Fit CSV",
            )


# ------------------------------------------------------------
# Mode: Player Profile
# ------------------------------------------------------------

elif tool_mode == "Player Profile":
    st.subheader("Player Profile Mode")
    st.caption(mode_help_text("Player Profile"))

    player_summary = get_player_summary(team_filtered_data, selected_player)

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
                <b>Rotation Recommendation:</b> {rotation_action}<br>
                <b>Final Coach Action:</b> {coach_action}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.info(
            f"Current metric focus: {metric_focus}. This changes the readiness score weighting for the selected player."
        )

        st.write("### Coach Decision Layer")

        decision_df = pd.DataFrame(
            [
                {
                    "Area": "Workload",
                    "Signal": workload_status,
                    "Coach Action": workload_action,
                },
                {
                    "Area": "Efficiency",
                    "Signal": efficiency_status,
                    "Coach Action": efficiency_action,
                },
                {
                    "Area": "Consistency",
                    "Signal": consistency_status,
                    "Coach Action": consistency_action,
                },
                {
                    "Area": "Participation Context",
                    "Signal": f"{scores['Recent Games Used']} recent recorded games",
                    "Coach Action": "Participation is context only, not included in readiness score.",
                },
            ]
        )

        st.dataframe(decision_df, use_container_width=True)

        player_profile_df = player_summary["Player Data"].tail(recent_window).copy()

        st.write("### Recent Performance Trend")

        fig_profile = px.line(
            player_profile_df,
            x="Date",
            y=["Points", "Rebounds", "Assists", "PlusMinus"],
            markers=True,
            title=f"{selected_player}: Recent Performance Trend",
        )
        st.plotly_chart(fig_profile, use_container_width=True)

        st.write("### Recent Game Log")
        st.dataframe(player_profile_df, use_container_width=True)

        player_summary_download = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Mode": tool_mode,
            "Metric Focus": metric_focus,
            "Player": selected_player,
            "Team": selected_team,
            "Season": selected_season,
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
            "Rotation Recommendation": rotation_action,
            "Final Coach Action": coach_action,
        }

        fixed_download_link(
            data=make_summary_csv(player_summary_download),
            file_name=f"{selected_player.replace(' ', '_')}_player_profile_summary.csv",
            label="Download Profile CSV",
        )


# ------------------------------------------------------------
# Mode: Pre-Game Readiness
# ------------------------------------------------------------

elif tool_mode == "Pre-Game Readiness":
    st.subheader("Pre-Game Readiness Mode")
    st.caption(mode_help_text("Pre-Game Readiness"))

    col1, col2, col3 = st.columns([1.2, 1, 1])

    with col1:
        st.markdown(
            f"""
            <div class="score-card">
                <div class="score-number">{scores['Readiness Score']}</div>
                <div class="score-label">Readiness Score / 100</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.metric("Readiness Category", status)
        st.metric("Recent Games Used", scores["Recent Games Used"])

    with col3:
        st.metric("Recent Avg Production", scores["Recent Avg Production"])
        st.metric("Season Avg Production", scores["Season Avg Production"])

    st.markdown(
        f"""
        <div class="info-box">
            <b>Readiness Score interpretation:</b> {readiness_interpretation_text("Use this to support selection and role planning before the next game.")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="{card_class(status)}">
            <b>Rotation Recommendation:</b> {rotation_action}<br>
            <b>Final Coach Action:</b> {coach_action}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("### Readiness Component Breakdown")

    st.info(
        f"Current metric focus: {metric_focus}. "
        "The readiness score weighting changes based on the selected focus. "
        "Team readiness rankings use the All-round profile for fair comparison."
    )

    weights = scores["Weight Profile"]

    component_df = pd.DataFrame(
        {
            "Component": [
                "Recent Form",
                "Efficiency",
                "Consistency",
                "Workload Balance",
            ],
            "Score": [
                scores["Recent Form"],
                scores["Efficiency"],
                scores["Consistency"],
                scores["Workload Balance"],
            ],
            "Weight": [
                f"{int(weights['Recent Form'] * 100)}%",
                f"{int(weights['Efficiency'] * 100)}%",
                f"{int(weights['Consistency'] * 100)}%",
                f"{int(weights['Workload Balance'] * 100)}%",
            ],
        }
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.dataframe(component_df, use_container_width=True)

    with col2:
        fig_components = px.bar(
            component_df,
            x="Component",
            y="Score",
            text="Score",
            title="Readiness Component Scores",
        )
        st.plotly_chart(fig_components, use_container_width=True)

    st.write("### Coach Decision Layer")

    coach_df = pd.DataFrame(
        [
            {
                "Area": "Workload",
                "Signal": workload_status,
                "Coach Action": workload_action,
            },
            {
                "Area": "Efficiency",
                "Signal": efficiency_status,
                "Coach Action": efficiency_action,
            },
            {
                "Area": "Consistency",
                "Signal": consistency_status,
                "Coach Action": consistency_action,
            },
            {
                "Area": "Participation Context",
                "Signal": scores["Participation Context"],
                "Coach Action": "Use as context only. Not weighted in readiness score.",
            },
        ]
    )

    st.dataframe(coach_df, use_container_width=True)

    st.write("### Recent Performance Context")

    recent_df = player_df.sort_values("Date").tail(recent_window)

    fig_recent = px.line(
        recent_df,
        x="Date",
        y=["Production", "Minutes"],
        markers=True,
        title=f"{selected_player}: Recent Production and Minutes",
    )
    st.plotly_chart(fig_recent, use_container_width=True)

    summary = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Mode": tool_mode,
        "Metric Focus": metric_focus,
        "Player": selected_player,
        "Team": selected_team,
        "Season": selected_season,
        "Readiness Score": scores["Readiness Score"],
        "Status": status,
        "Recent Form": scores["Recent Form"],
        "Efficiency": scores["Efficiency"],
        "Consistency": scores["Consistency"],
        "Workload Balance": scores["Workload Balance"],
        "Recent Avg Production": scores["Recent Avg Production"],
        "Season Avg Production": scores["Season Avg Production"],
        "Recent Avg Minutes": scores["Recent Avg Minutes"],
        "Season Avg Minutes": scores["Season Avg Minutes"],
        "Workload Ratio": scores["Workload Ratio"],
        "Rotation Recommendation": rotation_action,
        "Final Coach Action": coach_action,
    }

    fixed_download_link(
        data=make_summary_csv(summary),
        file_name=f"{selected_player.replace(' ', '_')}_pre_game_readiness.csv",
        label="Download Readiness CSV",
    )


# ------------------------------------------------------------
# Mode: Live Game Monitor
# ------------------------------------------------------------

# ------------------------------------------------------------
# Mode: Live Game Monitor
# ------------------------------------------------------------

elif tool_mode == "Live Game Monitor":
    st.subheader("Live Game Monitor Mode")
    st.caption(mode_help_text("Live Game Monitor"))

    st.write("### Enter Current Live Game Indicators")

    input_col1, input_col2, input_col3 = st.columns(3)

    with input_col1:
        current_minutes = st.slider(
            "Current minutes",
            min_value=0,
            max_value=80,
            value=0,
            step=1,
            help="Range allows regulation and rare overtime scenarios.",
        )
        current_points = st.slider(
            "Current points",
            min_value=0,
            max_value=110,
            value=0,
            step=1,
            help="Range based on NBA single-game scoring record plus buffer.",
        )

    with input_col2:
        current_rebounds = st.slider(
            "Current rebounds",
            min_value=0,
            max_value=65,
            value=0,
            step=1,
            help="Range based on NBA single-game rebounding record plus buffer.",
        )
        current_assists = st.slider(
            "Current assists",
            min_value=0,
            max_value=40,
            value=0,
            step=1,
            help="Range based on NBA single-game assist record plus buffer.",
        )

    with input_col3:
        current_turnovers = st.slider(
            "Current turnovers",
            min_value=0,
            max_value=25,
            value=0,
            step=1,
            help="Range allows unusually high turnover games without being unrealistic.",
        )
        current_plus_minus = st.slider(
            "Current plus-minus",
            min_value=-70,
            max_value=70,
            value=0,
            step=1,
            help="Range covers historical positive and negative plus-minus extremes plus buffer.",
        )

    coach_concern = st.slider("Coach concern level", 1, 10, 5)

    live_result = live_game_decision(
        current_minutes=current_minutes,
        current_points=current_points,
        current_rebounds=current_rebounds,
        current_assists=current_assists,
        current_turnovers=current_turnovers,
        current_plus_minus=current_plus_minus,
        coach_concern=coach_concern,
        baseline_minutes=scores["Season Avg Minutes"],
    )

    st.write("### Main Tactical Response")

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:
        report_card("Live Contribution", live_result["Live Contribution"])

    with summary_col2:
        report_card("Load Status", live_result["Load Status"])

    with summary_col3:
        report_card("Load Ratio", live_result["Load Ratio"])

    alert_col1, alert_col2 = st.columns(2)

    with alert_col1:
        if live_result["Alerts"]:
            alert_text = "<br>".join(live_result["Alerts"])
            st.markdown(
                f"""
                <div class="amber-box">
                    <b>Live Alerts:</b><br>
                    {alert_text}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="green-box">
                    <b>Live Alerts:</b><br>
                    No major live-game concern detected.
                </div>
                """,
                unsafe_allow_html=True,
            )

    with alert_col2:
        st.markdown(
            f"""
            <div class="info-box">
                <b>Live Coach Action:</b><br>
                {live_result["Action"]}
            </div>
            """,
            unsafe_allow_html=True,
        )

    summary = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Mode": tool_mode,
        "Metric Focus": metric_focus,
        "Player": selected_player,
        "Team": selected_team,
        "Season": selected_season,
        "Current Minutes": current_minutes,
        "Current Points": current_points,
        "Current Rebounds": current_rebounds,
        "Current Assists": current_assists,
        "Current Turnovers": current_turnovers,
        "Current PlusMinus": current_plus_minus,
        "Coach Concern": coach_concern,
        "Live Contribution": live_result["Live Contribution"],
        "Load Status": live_result["Load Status"],
        "Load Ratio": live_result["Load Ratio"],
        "Action": live_result["Action"],
    }

    fixed_download_link(
        data=make_summary_csv(summary),
        file_name=f"{selected_player.replace(' ', '_')}_live_monitoring.csv",
        label="Download Live CSV",
    )


# ------------------------------------------------------------
# Mode: Post-Game Report
# ------------------------------------------------------------

if tool_mode == "Post-Game Report":
    st.subheader("Post-Game Report Mode")
    st.caption(mode_help_text("Post-Game Report"))

    def post_game_card(title: str, value: str) -> None:
        st.markdown(
            f"""
            <div style="
                background-color:#111827;
                border:1px solid #374151;
                border-radius:12px;
                padding:16px 18px;
                margin-bottom:12px;
                min-height:110px;">
                <div style="
                    font-size:15px;
                    color:#9CA3AF;
                    margin-bottom:8px;
                    font-weight:600;">
                    {title}
                </div>
                <div style="
                    font-size:24px;
                    font-weight:700;
                    color:#F9FAFB;
                    line-height:1.25;
                    white-space:normal;
                    overflow-wrap:break-word;">
                    {value}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    player_baseline = player_df.copy()

    baseline = {
        "Points": player_baseline["Points"].mean(),
        "Rebounds": player_baseline["Rebounds"].mean(),
        "Assists": player_baseline["Assists"].mean(),
        "Turnovers": player_baseline["Turnovers"].mean(),
        "Plus-Minus": player_baseline["PlusMinus"].mean(),
        "Minutes": player_baseline["Minutes"].mean(),
    }

    st.write("### Enter Latest Game Performance")

    col1, col2, col3 = st.columns(3)

    with col1:
        pg_minutes = st.slider("Post-game minutes", 0.0, 60.0, 25.0, 0.5)
        pg_points = st.slider("Post-game points", 0, 80, 15)

    with col2:
        pg_rebounds = st.slider("Post-game rebounds", 0, 30, 5)
        pg_assists = st.slider("Post-game assists", 0, 25, 4)

    with col3:
        pg_turnovers = st.slider("Post-game turnovers", 0, 12, 2)
        pg_plus_minus = st.slider("Post-game plus-minus", -40, 40, 0)

    latest = {
        "Points": pg_points,
        "Rebounds": pg_rebounds,
        "Assists": pg_assists,
        "Turnovers": pg_turnovers,
        "Plus-Minus": pg_plus_minus,
        "Minutes": pg_minutes,
    }

    post_result = post_game_impact(
        pg_minutes=pg_minutes,
        pg_points=pg_points,
        pg_rebounds=pg_rebounds,
        pg_assists=pg_assists,
        pg_turnovers=pg_turnovers,
        pg_plus_minus=pg_plus_minus,
        baseline=baseline,
    )

    st.write("### Main Coach Recommendation")

    summary_col1, summary_col2 = st.columns(2)

    with summary_col1:
        post_game_card("Game Impact", post_result["Game Impact"])

    with summary_col2:
        post_game_card("Coach Action", post_result["Recommendation"])

    st.markdown(
        f"""
        <div class="info-box">
            <b>Coach Action:</b><br>
            {post_result["Recommendation"]}
        </div>
        """,
        unsafe_allow_html=True,
    )

    comparison_df = pd.DataFrame(
        {
            "Metric": list(latest.keys()),
            "Latest Game": list(latest.values()),
            "Player Average": [baseline[m] for m in latest.keys()],
        }
    )

    comparison_df["Difference"] = (
        comparison_df["Latest Game"] - comparison_df["Player Average"]
    ).round(1)

    comparison_df["Player Average"] = comparison_df["Player Average"].round(1)

    st.write("### Latest Game vs Player Average")
    st.caption(
        "The chart compares the latest entered game with the selected player's normal historical baseline."
    )

    fig_compare = px.bar(
        comparison_df,
        x="Metric",
        y=["Latest Game", "Player Average"],
        barmode="group",
        title="Latest Game Compared With Player Average",
    )

    fig_compare.update_layout(
        xaxis_title="Performance Metric",
        yaxis_title="Value",
        legend_title="Comparison",
    )

    st.plotly_chart(fig_compare, use_container_width=True)

    st.write("### Baseline Comparison Table")
    st.dataframe(comparison_df, use_container_width=True)

    decision_rows = []

    if pg_minutes > baseline["Minutes"] * 1.15:
        decision_rows.append(
            {
                "Area": "Workload",
                "Signal": "Minutes above player average",
                "Coach Action": "Monitor next-game minutes or consider recovery-focused follow-up.",
            }
        )
    elif pg_minutes < baseline["Minutes"] * 0.85:
        decision_rows.append(
            {
                "Area": "Workload",
                "Signal": "Minutes below player average",
                "Coach Action": "Review role, involvement level, or tactical usage.",
            }
        )
    else:
        decision_rows.append(
            {
                "Area": "Workload",
                "Signal": "Minutes within normal range",
                "Coach Action": "Normal workload management.",
            }
        )

    if pg_turnovers > baseline["Turnovers"] * 1.25:
        decision_rows.append(
            {
                "Area": "Efficiency",
                "Signal": "Turnovers above player average",
                "Coach Action": "Review ball security, shot decisions, and possession quality.",
            }
        )
    else:
        decision_rows.append(
            {
                "Area": "Efficiency",
                "Signal": "Turnovers within expected range",
                "Coach Action": "No major turnover concern.",
            }
        )

    baseline_production = (
        baseline["Points"]
        + baseline["Rebounds"]
        + baseline["Assists"]
        + baseline["Plus-Minus"]
    )

    if post_result["Game Production"] > baseline_production * 1.15:
        decision_rows.append(
            {
                "Area": "Performance Impact",
                "Signal": "Production clearly above player average",
                "Coach Action": "Maintain or increase involvement if matchup context supports it.",
            }
        )
    elif post_result["Game Production"] < baseline_production * 0.85:
        decision_rows.append(
            {
                "Area": "Performance Impact",
                "Signal": "Production below player average",
                "Coach Action": "Review role, matchup, recent form, and support structure.",
            }
        )
    else:
        decision_rows.append(
            {
                "Area": "Performance Impact",
                "Signal": "Production near player average",
                "Coach Action": "Maintain current role and monitor next-game trend.",
            }
        )

    if pg_plus_minus < baseline["Plus-Minus"] - 5:
        decision_rows.append(
            {
                "Area": "Lineup Impact",
                "Signal": "Plus-minus below normal baseline",
                "Coach Action": "Review lineup combinations and matchup exposure.",
            }
        )
    elif pg_plus_minus > baseline["Plus-Minus"] + 5:
        decision_rows.append(
            {
                "Area": "Lineup Impact",
                "Signal": "Plus-minus above normal baseline",
                "Coach Action": "Consider whether current lineup combinations are effective.",
            }
        )
    else:
        decision_rows.append(
            {
                "Area": "Lineup Impact",
                "Signal": "Plus-minus close to normal baseline",
                "Coach Action": "No major lineup impact concern from this game.",
            }
        )

    coach_decision_df = pd.DataFrame(decision_rows)

    st.write("### Coach-Ready Decision Summary")
    st.dataframe(coach_decision_df, use_container_width=True)

    summary = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Mode": tool_mode,
        "Metric Focus": metric_focus,
        "Player": selected_player,
        "Team": selected_team,
        "Season": selected_season,
        "Minutes": pg_minutes,
        "Player Avg Minutes": round(baseline["Minutes"], 1),
        "Points": pg_points,
        "Player Avg Points": round(baseline["Points"], 1),
        "Rebounds": pg_rebounds,
        "Player Avg Rebounds": round(baseline["Rebounds"], 1),
        "Assists": pg_assists,
        "Player Avg Assists": round(baseline["Assists"], 1),
        "Turnovers": pg_turnovers,
        "Player Avg Turnovers": round(baseline["Turnovers"], 1),
        "PlusMinus": pg_plus_minus,
        "Player Avg PlusMinus": round(baseline["Plus-Minus"], 1),
        "Game Production": post_result["Game Production"],
        "Game Impact": post_result["Game Impact"],
        "Workload": post_result["Workload"],
        "Efficiency Flag": post_result["Efficiency Flag"],
        "Recommendation": post_result["Recommendation"],
    }

    fixed_download_link(
        data=make_summary_csv(summary),
        file_name=f"{selected_player.replace(' ', '_')}_post_game_report.csv",
        label="Download Report CSV",
    )
