# Basketball Performance Readiness Dashboard

Local Streamlit sports analytics dashboard for the MIS41420 Sports & Performance Analytics Group Assessment.

## What this app does

The app helps coaches and analysts review basketball player performance, readiness, team selection fit, live tactical scenarios, and post-game action plans using NBA game-log data.

## What you need before starting

If you are starting from a fresh computer, install these first:

1. **Python 3.10 or newer**
   - Download from: https://www.python.org/downloads/
   - During installation on Windows, tick **Add Python to PATH**.

2. **Visual Studio Code**
   - Download from: https://code.visualstudio.com/

3. **Git** is optional, but helpful if you want to manage the project from the command line.

## Folder structure

After extracting the zip file, open the folder named:

`basketball_readiness_dashboard`

Inside that folder you should see files such as:

- `app.py`
- `README.md`
- `requirements.txt`
- `Data/clean_nba_player_gamelog_2018_2022.csv`

## One-time setup on a new computer

Open the project folder in VS Code, then open the terminal in VS Code and run the following commands one by one.

### 1. Check Python

```powershell
python --version
```

If that does not work, try:

```powershell
py --version
```

If neither command works, Python is not installed correctly or not added to PATH.

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

If `python` does not work but `py` does, use:

```powershell
py -m venv .venv
```

### 3. Activate the virtual environment

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again:

```powershell
.venv\Scripts\Activate.ps1
```

You should see `(.venv)` appear at the start of your terminal line.

### 4. Install the required packages

```powershell
pip install -r requirements.txt
```

If `pip` does not work, try:

```powershell
python -m pip install -r requirements.txt
```

## Run the app

After the packages finish installing, start the dashboard with:

```powershell
python -m streamlit run app.py
```

If `python` does not work, use:

```powershell
py -m streamlit run app.py
```

The app should open in your browser automatically.

## First-run checklist

If the app does not start, check these points:

- You are inside the `basketball_readiness_dashboard` folder in the terminal.
- The virtual environment is activated.
- `requirements.txt` has been installed successfully.
- The `Data` folder still contains `clean_nba_player_gamelog_2018_2022.csv`.
- You are running `python -m streamlit run app.py` from the project root.

## Common commands

### Re-open the app later

```powershell
.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

### Re-install packages if needed

```powershell
pip install -r requirements.txt
```

## Notes

- This is a local app and does not need a deployed server.
- The dashboard is designed to run from the project folder using the cleaned NBA player game-log data included in `Data/`.
