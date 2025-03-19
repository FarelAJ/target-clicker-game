from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB connection
MONGODB_URI = os.environ.get('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("No MONGODB_URI in environment variables")

client = MongoClient(MONGODB_URI)
db = client.get_database('highscores_db')
highscores_collection = db.get_collection('highscores')

@app.route('/api/highscores', methods=['GET'])
def get_highscores():
    # Get all scores and sort them by score (descending)
    scores = list(highscores_collection.find().sort('score', -1))
    
    # Convert ObjectId to string for JSON serialization
    for score in scores:
        score['_id'] = str(score['_id'])
        score['date'] = score['date'].isoformat() if 'date' in score else None
    
    return jsonify(scores)

@app.route('/api/highscores', methods=['POST'])
def add_highscore():
    data = request.json
    if not data or 'name' not in data or 'score' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Create new score document
    new_score = {
        'name': data['name'],
        'score': data['score'],
        'date': datetime.utcnow()
    }
    
    # Insert into MongoDB
    result = highscores_collection.insert_one(new_score)
    
    # Get all scores after adding new one
    scores = list(highscores_collection.find().sort('score', -1))
    
    # Convert ObjectId to string for JSON serialization
    for score in scores:
        score['_id'] = str(score['_id'])
        score['date'] = score['date'].isoformat() if 'date' in score else None
    
    return jsonify(scores), 201

if __name__ == '__main__':
    app.run(debug=True)