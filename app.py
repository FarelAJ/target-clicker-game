from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import json
import requests

app = Flask(__name__)
CORS(app)

# Vercel KV REST API configuration
KV_REST_API_URL = "https://api.vercel.com/v1/kv"
KV_REST_API_TOKEN = "your-vercel-kv-token"

def kv_request(method, path, data=None):
    """Make request to Vercel KV REST API"""
    url = f"{KV_REST_API_URL}{path}"
    headers = {
        "Authorization": f"Bearer {KV_REST_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data)
    elif method == "PUT":
        response = requests.put(url, headers=headers, json=data)
    
    response.raise_for_status()
    return response.json()

@app.route('/')
def home():
    return jsonify({
        "message": "Target Clicker Game API",
        "endpoints": {
            "GET /api/highscores": "Get all highscores",
            "POST /api/highscores": "Add new highscore",
            "GET /api/health": "Check API health"
        }
    })

@app.route('/api/highscores', methods=['GET'])
def get_highscores():
    try:
        # Get scores from KV store
        response = kv_request("GET", "/scores")
        scores = response.get("scores", [])
        
        # Sort by score descending
        scores.sort(key=lambda x: x['score'], reverse=True)
        return jsonify(scores)
    except Exception as e:
        print(f"Error getting scores: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/highscores', methods=['POST'])
def add_highscore():
    try:
        data = request.json
        if not data or 'name' not in data or 'score' not in data:
            return jsonify({'error': 'Missing required fields: name and score'}), 400

        # Get current scores
        try:
            response = kv_request("GET", "/scores")
            scores = response.get("scores", [])
        except:
            scores = []

        new_score = {
            'id': len(scores) + 1,
            'name': data['name'],
            'score': int(data['score']),
            'date': datetime.utcnow().isoformat()
        }
        
        scores.append(new_score)
        
        # Update scores in KV store
        kv_request("PUT", "/scores", {"scores": scores})
        
        return jsonify(new_score), 201
    except Exception as e:
        print(f"Error adding score: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # Test KV store connection
        kv_request("GET", "/health")
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

if __name__ == '__main__':
    app.run(debug=True)