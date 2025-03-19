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

# Global variable to track MongoDB connection
mongodb_client = None
highscores_collection = None

def get_mongodb():
    global mongodb_client, highscores_collection
    if mongodb_client is None:
        try:
            MONGODB_URI = os.environ.get('MONGODB_URI')
            if not MONGODB_URI:
                raise ValueError("MONGODB_URI environment variable is not set")
            
            print(f"Connecting to MongoDB...", file=sys.stderr)
            mongodb_client = MongoClient(MONGODB_URI)
            db = mongodb_client.get_database('highscores_db')
            highscores_collection = db.get_collection('highscores')
            
            # Test connection
            mongodb_client.admin.command('ping')
            print("Successfully connected to MongoDB!", file=sys.stderr)
        except Exception as e:
            print(f"MongoDB connection error: {str(e)}", file=sys.stderr)
            raise e
    return highscores_collection

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
        collection = get_mongodb()
        scores = list(collection.find().sort('score', -1))
        for score in scores:
            score['_id'] = str(score['_id'])
            if 'date' in score:
                score['date'] = score['date'].isoformat()
        return jsonify(scores)
    except Exception as e:
        print(f"Error in get_highscores: {str(e)}", file=sys.stderr)
        return jsonify({"error": f"Failed to get highscores: {str(e)}"}), 500

@app.route('/api/highscores', methods=['POST'])
def add_highscore():
    try:
        collection = get_mongodb()
        data = request.json
        if not data or 'name' not in data or 'score' not in data:
            return jsonify({'error': 'Missing required fields: name and score'}), 400

        new_score = {
            'name': data['name'],
            'score': int(data['score']),
            'date': datetime.utcnow()
        }

        result = collection.insert_one(new_score)
        new_score['_id'] = str(result.inserted_id)
        new_score['date'] = new_score['date'].isoformat()

        return jsonify(new_score), 201
    except ValueError as e:
        return jsonify({"error": f"Invalid score value: {str(e)}"}), 400
    except Exception as e:
        print(f"Error in add_highscore: {str(e)}", file=sys.stderr)
        return jsonify({"error": f"Failed to add highscore: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        collection = get_mongodb()
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