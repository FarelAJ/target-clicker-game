from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
CORS(app)

# MongoDB connection
MONGODB_URI = "mongodb+srv://vercel-admin-user:7Wd0Qr5vxELGGELq@cluster0.mongodb.net/highscores?retryWrites=true&w=majority"
client = MongoClient(MONGODB_URI)
db = client.get_database('highscores')
scores_collection = db.get_collection('scores')

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
        # Get all scores and sort by score descending
        scores = list(scores_collection.find().sort('score', -1))
        
        # Convert ObjectId to string for JSON serialization
        for score in scores:
            score['_id'] = str(score['_id'])
        
        return jsonify(scores)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/highscores', methods=['POST'])
def add_highscore():
    try:
        data = request.json
        if not data or 'name' not in data or 'score' not in data:
            return jsonify({'error': 'Missing required fields: name and score'}), 400

        # Create new score document
        new_score = {
            'name': data['name'],
            'score': int(data['score']),
            'date': datetime.utcnow()
        }
        
        # Insert into MongoDB
        result = scores_collection.insert_one(new_score)
        
        # Return the new score with string ID
        new_score['_id'] = str(result.inserted_id)
        new_score['date'] = new_score['date'].isoformat()
        
        return jsonify(new_score), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # Ping MongoDB
        client.admin.command('ping')
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