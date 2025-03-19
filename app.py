from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import json
import sys
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
CORS(app)

# Error handling
@app.errorhandler(Exception)
def handle_error(error):
    print(f"Error: {str(error)}", file=sys.stderr)
    return jsonify({"error": str(error)}), 500

try:
    # MongoDB connection
    MONGODB_URI = os.environ.get('MONGODB_URI')
    if not MONGODB_URI:
        raise ValueError("No MONGODB_URI in environment variables")

    client = MongoClient(MONGODB_URI)
    db = client.get_database('highscores_db')
    highscores_collection = db.get_collection('highscores')

    # Test the connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB!", file=sys.stderr)

except Exception as e:
    print(f"MongoDB connection error: {str(e)}", file=sys.stderr)
    raise e

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"message": "API is working"}), 200

@app.route('/api/highscores', methods=['GET'])
def get_highscores():
    try:
        scores = list(highscores_collection.find().sort('score', -1))
        for score in scores:
            score['_id'] = str(score['_id'])
            if 'date' in score:
                score['date'] = score['date'].isoformat()
        return jsonify(scores)
    except Exception as e:
        print(f"Error in get_highscores: {str(e)}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500

@app.route('/api/highscores', methods=['POST'])
def add_highscore():
    try:
        data = request.json
        if not data or 'name' not in data or 'score' not in data:
            return jsonify({'error': 'Invalid data'}), 400

        new_score = {
            'name': data['name'],
            'score': int(data['score']),
            'date': datetime.utcnow()
        }

        result = highscores_collection.insert_one(new_score)
        new_score['_id'] = str(result.inserted_id)
        new_score['date'] = new_score['date'].isoformat()

        return jsonify(new_score), 201
    except Exception as e:
        print(f"Error in add_highscore: {str(e)}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # Test MongoDB connection
        client.admin.command('ping')
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500