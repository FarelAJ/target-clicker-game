from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import json

app = Flask(__name__)
CORS(app)

# Global variable to store scores (will reset on cold starts, but fine for testing)
SCORES = []

def get_scores():
    """Get sorted scores"""
    return sorted(SCORES, key=lambda x: x['score'], reverse=True)

@app.route('/api', methods=['GET'])
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
        scores = get_scores()
        print(f"Returning scores: {scores}")  # Debug log
        return jsonify(scores)
    except Exception as e:
        print(f"Error getting scores: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/highscores', methods=['POST'])
def add_highscore():
    try:
        data = request.get_json()
        print(f"Received data: {data}")  # Debug log

        if not data or 'name' not in data or 'score' not in data:
            return jsonify({'error': 'Missing required fields: name and score'}), 400

        try:
            score = int(data['score'])
        except ValueError:
            return jsonify({'error': 'Score must be a number'}), 400

        if score < 0:
            return jsonify({'error': 'Score cannot be negative'}), 400

        new_score = {
            'id': len(SCORES) + 1,
            'name': str(data['name']),
            'score': score,
            'date': datetime.utcnow().isoformat()
        }
        
        SCORES.append(new_score)
        print(f"Added new score: {new_score}")  # Debug log
        
        # Return all scores after adding new one
        all_scores = get_scores()
        print(f"Returning all scores: {all_scores}")  # Debug log
        return jsonify(all_scores), 201

    except Exception as e:
        print(f"Error adding score: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "scores_count": len(SCORES),
        "timestamp": datetime.utcnow().isoformat()
    }), 200