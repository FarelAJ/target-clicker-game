from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import json
import sys
import redis
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

# Vercel KV (Redis) connection
def get_redis():
    try:
        REDIS_URL = os.environ.get('REDIS_URL', os.environ.get('KV_URL'))
        if not REDIS_URL:
            raise ValueError("No Redis URL found in environment variables")
        
        print(f"Connecting to Redis...", file=sys.stderr)
        url = urlparse(REDIS_URL)
        
        r = redis.Redis(
            host=url.hostname,
            port=url.port,
            username=url.username,
            password=url.password,
            ssl=True,
            ssl_cert_reqs=None
        )
        
        # Test connection
        r.ping()
        print("Successfully connected to Redis!", file=sys.stderr)
        return r
    except Exception as e:
        print(f"Redis connection error: {str(e)}", file=sys.stderr)
        raise e

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

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Route not found"}), 404

@app.errorhandler(Exception)
def handle_error(error):
    print(f"Error: {str(error)}", file=sys.stderr)
    return jsonify({"error": str(error)}), 500

@app.route('/api/highscores', methods=['GET'])
def get_highscores():
    try:
        r = get_redis()
        # Get all scores from Redis
        scores = []
        for key in r.scan_iter("score:*"):
            score_data = r.get(key)
            if score_data:
                score = json.loads(score_data)
                scores.append(score)
        
        # Sort by score descending
        scores.sort(key=lambda x: x['score'], reverse=True)
        return jsonify(scores)
    except Exception as e:
        print(f"Error in get_highscores: {str(e)}", file=sys.stderr)
        return jsonify({"error": f"Failed to get highscores: {str(e)}"}), 500

@app.route('/api/highscores', methods=['POST'])
def add_highscore():
    try:
        r = get_redis()
        data = request.json
        if not data or 'name' not in data or 'score' not in data:
            return jsonify({'error': 'Missing required fields: name and score'}), 400

        score_id = r.incr('score_counter')
        new_score = {
            'id': score_id,
            'name': data['name'],
            'score': int(data['score']),
            'date': datetime.utcnow().isoformat()
        }

        # Store in Redis
        r.set(f"score:{score_id}", json.dumps(new_score))
        return jsonify(new_score), 201
    except ValueError as e:
        return jsonify({"error": f"Invalid score value: {str(e)}"}), 400
    except Exception as e:
        print(f"Error in add_highscore: {str(e)}", file=sys.stderr)
        return jsonify({"error": f"Failed to add highscore: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        r = get_redis()
        r.ping()
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