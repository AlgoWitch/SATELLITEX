from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import subprocess
import json

# Get absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')
UPLOADS_DIR = os.path.join(BASE_DIR, '..', 'uploads')
OUTPUTS_DIR = os.path.join(BASE_DIR, '..', 'outputs')

# Create directories
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

# Configure CORS
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
CORS(app, origins=[FRONTEND_URL, "http://localhost:3000", "http://localhost:5000", "*"])

# Serve frontend files
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/analysis.html')
def serve_analysis():
    return send_from_directory(app.static_folder, 'analysis.html')

@app.route('/outputs/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUTS_DIR, filename)

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route("/analyze", methods=["POST"])
def analyze():

    before = request.files["before"]
    after = request.files["after"]

    city = request.form.get("city", "custom")

    before_path = os.path.join(UPLOADS_DIR, f"before_{city}.tif")
    after_path = os.path.join(UPLOADS_DIR, f"after_{city}.tif")

    before.save(before_path)
    after.save(after_path)

    # Run prediction script
    subprocess.run(["python", "predict.py", city])

    result_path = os.path.join(OUTPUTS_DIR, f"{city}_results.json")

    with open(result_path) as f:
        data = json.load(f)

    return jsonify(data)

if __name__ == "__main__":
    port = int(os.getenv('PORT', 10000))
    app.run(host="0.0.0.0", port=port, debug=False)