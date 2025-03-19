from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure database based on environment
if os.environ.get('DATABASE_URL'):
    # Use PostgreSQL in production
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
else:
    # Use SQLite in development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///highscores.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class HighScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'score': self.score,
            'date': self.date.isoformat()
        }

# Create tables
with app.app_context():
    db.create_all()

@app.route('/api/highscores', methods=['GET'])
def get_highscores():
    # Get all scores and sort them by score (descending)
    scores = HighScore.query.order_by(HighScore.score.desc()).all()
    return jsonify([score.to_dict() for score in scores])

@app.route('/api/highscores', methods=['POST'])
def add_highscore():
    data = request.json
    if not data or 'name' not in data or 'score' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Create new score
    new_score = HighScore(
        name=data['name'],
        score=data['score']
    )
    
    # Add and commit to database
    db.session.add(new_score)
    db.session.commit()
    
    # Return all scores after adding new one
    scores = HighScore.query.order_by(HighScore.score.desc()).all()
    return jsonify([score.to_dict() for score in scores]), 201

if __name__ == '__main__':
    app.run(debug=True)