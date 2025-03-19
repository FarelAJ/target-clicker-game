from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import json
import sys

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
        print(f"GET /api/highscores - Returning scores: {scores}", file=sys.stderr)
        return jsonify(scores)
    except Exception as e:
        print(f"Error getting scores: {str(e)}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500

@app.route('/api/highscores', methods=['POST'])
def add_highscore():
    try:
        print("POST /api/highscores - Request received", file=sys.stderr)
        data = request.get_json()
        print(f"Request data: {data}", file=sys.stderr)

        if not data:
            print("Error: No data received", file=sys.stderr)
            return jsonify({'error': 'No data received'}), 400

        if 'name' not in data or 'score' not in data:
            print("Error: Missing required fields", file=sys.stderr)
            return jsonify({'error': 'Missing required fields: name and score'}), 400

        try:
            score = int(data['score'])
            print(f"Parsed score: {score}", file=sys.stderr)
        except (ValueError, TypeError) as e:
            print(f"Error parsing score: {str(e)}", file=sys.stderr)
            return jsonify({'error': f'Invalid score format: {str(e)}'}), 400

        if score < 0:
            print("Error: Negative score", file=sys.stderr)
            return jsonify({'error': 'Score cannot be negative'}), 400

        new_score = {
            'id': len(SCORES) + 1,
            'name': str(data['name']),
            'score': score,
            'date': datetime.utcnow().isoformat()
        }
        
        print(f"Created new score object: {new_score}", file=sys.stderr)
        SCORES.append(new_score)
        
        # Return all scores after adding new one
        all_scores = get_scores()
        print(f"Returning updated scores: {all_scores}", file=sys.stderr)
        return jsonify(all_scores), 201

    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        return jsonify({
            "status": "healthy",
            "scores_count": len(SCORES),
            "scores": SCORES,  # Include current scores in health check
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        print(f"Health check error: {str(e)}", file=sys.stderr)
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500