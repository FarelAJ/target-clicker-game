from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import json
import sys
import requests
import base64

app = Flask(__name__)
CORS(app)

def get_upstash_client():
    """Get Upstash REST client configuration"""
    url = os.environ.get('UPSTASH_REDIS_REST_URL')
    token = os.environ.get('UPSTASH_REDIS_REST_TOKEN')
    
    if not url or not token:
        raise ValueError("Missing Upstash configuration. Please set UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN")
    
    return {
        'url': url.rstrip('/'),
        'token': token
    }

def upstash_request(command, *args):
    """Make request to Upstash REST API"""
    try:
        config = get_upstash_client()
        
        # Encode command and arguments
        encoded_args = [base64.b64encode(str(arg).encode()).decode() for arg in args]
        encoded_command = base64.b64encode(command.encode()).decode()
        
        # Prepare request
        headers = {
            'Authorization': f'Bearer {config["token"]}'
        }
        body = {
            'cmd': [encoded_command, *encoded_args]
        }
        
        # Make request
        response = requests.post(f"{config['url']}", headers=headers, json=body)
        response.raise_for_status()
        
        return response.json()['result']
    except requests.exceptions.RequestException as e:
        print(f"Upstash request error: {str(e)}", file=sys.stderr)
        raise

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
        # Get all score keys
        keys = upstash_request('KEYS', 'score:*')
        scores = []
        
        # Get scores for each key
        for key in keys:
            score_data = upstash_request('GET', key)
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
        data = request.json
        if not data or 'name' not in data or 'score' not in data:
            return jsonify({'error': 'Missing required fields: name and score'}), 400

        # Get next score ID
        score_id = upstash_request('INCR', 'score_counter')
        
        new_score = {
            'id': score_id,
            'name': data['name'],
            'score': int(data['score']),
            'date': datetime.utcnow().isoformat()
        }

        # Store score
        upstash_request('SET', f'score:{score_id}', json.dumps(new_score))
        return jsonify(new_score), 201
    except ValueError as e:
        return jsonify({"error": f"Invalid score value: {str(e)}"}), 400
    except Exception as e:
        print(f"Error in add_highscore: {str(e)}", file=sys.stderr)
        return jsonify({"error": f"Failed to add highscore: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # Test Upstash connection with PING
        result = upstash_request('PING')
        if result != 'PONG':
            raise ValueError("Invalid response from Upstash")
            
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