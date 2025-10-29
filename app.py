import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

app = Flask(__name__)

# Database configuration (read from environment with sensible defaults)
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'sirene')

# SQLAlchemy URI for MySQL using PyMySQL driver
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Movie(db.Model):
    """Simple Movie model mapped to the `movies` table in your `sirene` DB.

    Assumed columns: id (int primary key), title (str), year (int), genre (str), description (text).
    If your schema differs, adjust this model accordingly.
    """
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    year = db.Column(db.Integer)
    genre = db.Column(db.String(100))
    description = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'year': self.year,
            'genre': self.genre,
            'description': self.description,
        }


@app.route('/')
def index():
    return jsonify({'service': 'sirene', 'routes': ['/', '/movies', '/health']})


@app.route('/movies')
def get_movies():
    """Return first 100 movies as JSON. If the table is empty or missing, returns empty list or 500 with error."""
    try:
        movies = Movie.query.limit(100).all()
        return jsonify([m.to_dict() for m in movies])
    except Exception as e:
        return jsonify({'error': 'could not fetch movies', 'details': str(e)}), 500


@app.route('/health')
def health():
    """Simple DB health check."""
    try:
        # lightweight check
        db.session.execute(str('SELECT 1'))
        return jsonify({'db': 'ok'}), 200
    except Exception as e:
        return jsonify({'db': 'error', 'details': str(e)}), 500


if __name__ == '__main__':
    # If you run locally, set env vars or create a .env file. See README.md
    app.run(debug=True)