# This imports functions from the Flask framework to build a web app.

# Flask – creates the app itself.
# render_template – lets you load an HTML file from your templates/ folder.
# jsonify – converts Python data (like a dictionary) into JSON format, for use in APIs.
from flask import Flask, render_template, jsonify


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
@app.route("/")
def index():
    return render_template("index.html")


# This creates an API route that serves data instead of a web page.

# @app.route("/api/wins-by-driver") means:
# When the user (or JavaScript frontend) makes a request to /api/wins-by-driver, run wins().

# jsonify({...}) means:
# Convert this Python dictionary into JSON, which is readable by browsers and JavaScript.

# The frontend JavaScript (like Chart.js) will fetch this API and turn it into a chart!
@app.route("/api/wins-by-driver")
def wins():
    return jsonify({
        "Max Verstappen": 19,
        "Sergio Pérez": 2,
        "Carlos Sainz": 1
    })
