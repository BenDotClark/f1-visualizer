import requests
# This imports functions from the Flask framework to build a web app.

# Flask – creates the app itself.
# render_template – lets you load an HTML file from your templates/ folder.
# jsonify – converts Python data (like a dictionary) into JSON format, for use in APIs.
# request – gives you access to data that came with the user's request — like form inputs, headers, and URL parameters.
from flask import Flask, render_template, jsonify, request
from datetime import datetime


# This creates an instance of your Flask app and stores it in the variable app.

# __name__ tells Flask where to look for things like templates and static files
# This is the core app object you'll use to define routes and run the server
app = Flask(__name__)

# This defines a route — what should happen when someone visits a specific URL on my site.

# @app.route("/") means:
# When the user goes to the homepage (/), run the index() function.

# render_template("index.html") means:
# Look in the templates/ folder, find index.html, and send it to the browser.

# This is how my HTML frontend is served!
# -------------------------
# Home Page Route
# -------------------------
@app.route("/")
def index():
    # Render the main HTML page
    return render_template("index.html")

# This creates an API route that serves data instead of a web page.

# @app.route("/api/wins-by-driver") means:
# When the user (or JavaScript frontend) makes a request to /api/wins-by-driver, run wins().

# jsonify({...}) means:
# Convert this Python dictionary into JSON, which is readable by browsers and JavaScript.

# The frontend JavaScript (like Chart.js) will fetch this API and turn it into a chart!


# -------------------------
# API: Driver Wins (Default Chart)
# -------------------------
@app.route("/api/wins-by-driver")
def wins():
    # Get the selected season from the query string, default to 2023
    season = request.args.get("season", "2023")
    try:
        # Fetch driver standings from the hosted Jolpica Ergast-compatible API
        response = requests.get(f"http://api.jolpi.ca/ergast/f1/{season}/driverStandings.json")
        data = response.json()

        # Drill down to the list of driver standings for the season
        standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]

        wins_data = {}
        for driver in standings:
            # Extract the full driver name and win count
            name = f"{driver['Driver']['givenName']} {driver['Driver']['familyName']}"
            wins = int(driver['wins'])
            wins_data[name] = wins  # Store in dictionary

        return jsonify(wins_data)
    except Exception as e:
        # Return error message with HTTP 500 status
        return jsonify({"error": str(e)}), 500
    
# -------------------------
# API: Constructor Wins
# -------------------------
@app.route("/api/constructor-standings")
def constructor_standings():
    season = request.args.get("season", "2023")
    try:
        # Fetch constructor standings data
        response = requests.get(f"http://api.jolpi.ca/ergast/f1/{season}/constructorStandings.json")
        data = response.json()

        standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"]

        constructor_data = {}
        for team in standings:
            name = team["Constructor"]["name"]
            wins = int(team["wins"])
            constructor_data[name] = wins

        return jsonify(constructor_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------
# API: Pole Positions (per driver)
# -------------------------
@app.route("/api/pole-positions")
def pole_positions():
    season = request.args.get("season", "2023")
    try:
        # Fetch all qualifying results with a high limit to include all races
        response = requests.get(f"http://api.jolpi.ca/ergast/f1/{season}/qualifying.json?limit=1000")
        data = response.json()
        races = data["MRData"]["RaceTable"]["Races"]

        pole_counts = {}
        for race in races:
            if not race["QualifyingResults"]:
                continue  # Skip races with no qualifying results
            pole_driver = race["QualifyingResults"][0]["Driver"]  # Get the fastest qualifier
            name = f"{pole_driver['givenName']} {pole_driver['familyName']}"
            pole_counts[name] = pole_counts.get(name, 0) + 1  # Count the pole

        return jsonify(pole_counts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------
# API: Fastest Laps (per driver)
# -------------------------
@app.route("/api/fastest-laps")
def fastest_laps():
    season = request.args.get("season", "2023")
    try:
        # Fetch race results including fastest lap info
        response = requests.get(f"http://api.jolpi.ca/ergast/f1/{season}/results.json?limit=1000")
        data = response.json()
        races = data["MRData"]["RaceTable"]["Races"]

        lap_counts = {}
        for race in races:
            for result in race["Results"]:
                # Check if this driver got the fastest lap (rank 1)
                if result.get("FastestLap", {}).get("rank") == "1":
                    driver = result["Driver"]
                    name = f"{driver['givenName']} {driver['familyName']}"
                    lap_counts[name] = lap_counts.get(name, 0) + 1

        return jsonify(lap_counts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================
# API: Latest Race Results (for race table)
# =========================
@app.route("/api/latest-results")
def latest_results():
    try:
        # Get the latest race results from Jolpica API
        url = "http://api.jolpi.ca/ergast/f1/current/last/results.json"
        response = requests.get(url)
        data = response.json()

        # Drill into the first race results returned
        race = data['MRData']['RaceTable']['Races'][0]
        race_name = race["raceName"]
        results = race['Results']

        formatted_results = []
        for r in results:
            driver = r['Driver']
            constructor = r['Constructor']
            formatted_results.append({
                "position": r['position'],
                "driver": f"{driver['givenName']} {driver['familyName']}",
                "code": driver.get("code", driver['familyName'][:3].upper()),
                "constructor": constructor['name'],
                "time": r.get('Time', {}).get('time', r.get('status', 'N/A')),
            })

        return jsonify({
        "grandPrix": race_name,
        "results": formatted_results
    })
    
    except Exception as e:
        return jsonify({"error": "Could not load latest results", "details": str(e)}), 500
    
# ===========================
# API: Driver Spotlight 
# ===========================
@app.route("/api/driver-spotlight")
def driver_spotlight():
    """
    Fetch enriched driver data for the current season's standings,
    combining standings info with profile data (age, nationality).
    """
    season = request.args.get("season", str(datetime.now().year))

    try:
        ERGAST_BASE_URL = "https://api.jolpi.ca/ergast/f1"

        # Correct URL spelling
        standings_url = f"{ERGAST_BASE_URL}/{season}/driverStandings.json"
        standings_response = requests.get(standings_url)
        standings_data = standings_response.json()

        standings = standings_data["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"][:3]

        # Fix profile endpoint spelling and key path
        profiles_url = f"{ERGAST_BASE_URL}/drivers.json?limit=1000"
        profiles_response = requests.get(profiles_url)
        profiles_data = profiles_response.json()

        all_profiles = profiles_data["MRData"]["DriverTable"]["Drivers"]
        profile_lookup = {driver["driverId"]: driver for driver in all_profiles}

        enriched_data = []
        for entry in standings:
            driver = entry["Driver"]
            driver_id = driver["driverId"]

            # Try fast lookup
            profile = profile_lookup.get(driver_id)

            # Fallback fetch if not found
            if not profile:
                print(f"🔁 Fallback fetch for missing profile: {driver_id}")
                fallback_url = f"{ERGAST_BASE_URL}/drivers/{driver_id}.json"
                fallback_response = requests.get(fallback_url).json()
                drivers_list = fallback_response["MRData"]["DriverTable"]["Drivers"]
                profile = drivers_list[0] if drivers_list else {}

            nationality = profile.get("nationality", "N/A")
            dob = profile.get("dateOfBirth", None)
            age = calculate_age(dob) if dob else "?"

            print(f"✅ Loaded profile for {driver_id}: {nationality} | {dob}")

            enriched_data.append({
                "name": f"{driver['givenName']} {driver['familyName']}",
                "constructor": entry["Constructors"][0]["name"],
                "points": entry["points"],
                "nationality": nationality,
                "age": age,
                "driverID": driver_id
            })

        return jsonify(enriched_data)

    except Exception as e:
        return jsonify({"error": "Could not load driver spotlight", "details": str(e)}), 500
    
@app.route("/api/constructor-spotlight")
def constructor_spotlight():
    season = request.args.get("season", str(datetime.now().year))
    try:
        response = requests.get(f"https://api.jolpi.ca/ergast/f1/{season}/constructorStandings.json")
        data = response.json()

        standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"]

        top3 = standings[:3]
        spotlight_data = []

        for team in top3:
            constructor = team["Constructor"]
            name = constructor["name"]
            spotlight_data.append({
                "name": name,
                "points": team["points"],
                "wins": team["wins"],
                "logo": team_logo_file(name)
            })

        return jsonify(spotlight_data)

    except Exception as e:
        return jsonify({"error": "Could not load constructor spotlight", "details": str(e)}), 500


# -------------------------
# Utility: Calculate Age
# -------------------------
def calculate_age(dob_string):
    birth_date = datetime.strptime(dob_string, "%Y-%m-%d")
    today = datetime.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def team_logo_file(name):
    """
    Maps constructor names to their logo filenames.
    Match this to your static/img/teams/ folder.
    """
    logo_map = {
        "Red Bull": "red-bull-racing-logo.png",
        "McLaren": "mclaren-logo.png",
        "Ferrari": "ferrari-logo.png",
        "Mercedes": "mercedes-logo.png",
        "Aston Martin": "aston-martin-logo.png",
        "Williams": "williams-logo.png",
        "Haas F1 Team": "haas-logo.png",
        "Alpine F1 Team": "alpine-logo.png",
        "Sauber": "kick-sauber-logo.png",
        "RB F1 Team": "racing-bulls-logo.png"
    }
    return logo_map.get(name, "default.png")