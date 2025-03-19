from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import json

app = Flask(__name__)
CORS(app)

# In-memory storage for development
scores = []

@app.route('/', methods=['GET'])
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
        # Sort by score descending
        sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
        return jsonify(sorted_scores)
    except Exception as e:
        print(f"Error getting scores: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/highscores', methods=['POST'])
def add_highscore():
    try:
        data = request.json
        if not data or 'name' not in data or 'score' not in data:
            return jsonify({'error': 'Missing required fields: name and score'}), 400

        new_score = {
            'id': len(scores) + 1,
            'name': data['name'],
            'score': int(data['score']),
            'date': datetime.utcnow().isoformat()
        }
        
        scores.append(new_score)
        return jsonify(new_score), 201
    except Exception as e:
        print(f"Error adding score: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }), 200