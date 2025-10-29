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


# --- CORRECTED MODELS ---

# Define the association table for the many-to-many relationship
# This maps to the `media_genre` table in sirene.sql
media_genre_table = db.Table('media_genre',
    db.Column('MediaID', db.Integer, db.ForeignKey('media.MediaID'), primary_key=True),
    db.Column('GenreID', db.Integer, db.ForeignKey('genre.GenreID'), primary_key=True)
)

class Media(db.Model):
    """
    Maps to the `media` table in sirene.sql.
    This replaces the old 'Movie' model.
    """
    __tablename__ = 'media'
    
    # Map columns from sirene.sql
    id = db.Column('MediaID', db.Integer, primary_key=True)
    title = db.Column('Title', db.String(255))
    synopsis = db.Column('Synopsis', db.Text)
    media_type = db.Column('MediaType', db.Enum('Movie','TV Show','Anime','Video Game'))
    release_date = db.Column('ReleaseDate', db.Date)
    duration_minutes = db.Column('DurationMinutes', db.Integer)

    # Define the many-to-many relationship to Genre
    genres = db.relationship('Genre', secondary=media_genre_table, lazy='subquery',
        backref=db.backref('media', lazy=True))

    def to_dict(self):
        """Converts the Media object to a dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            # Use the 'Synopsis' column for the 'description' field
            'description': self.synopsis, 
            'year': self.release_date.year if self.release_date else None,
            'media_type': self.media_type,
            # Add the list of genres from the relationship
            'genres': [g.genre_name for g in self.genres] 
        }

class Genre(db.Model):
    """Maps to the `genre` table in sirene.sql."""
    __tablename__ = 'genre'
    id = db.Column('GenreID', db.Integer, primary_key=True)
    genre_name = db.Column('GenreName', db.String(100), unique=True)


# --- UPDATED ROUTES ---

@app.route('/')
def index():
    return jsonify({'service': 'sirene', 'routes': ['/', '/movies', '/health']})


@app.route('/movies')
def get_movies():
    """
    Return first 100 movies as JSON.
    This now correctly queries the 'media' table.
    """
    try:
        # Query the Media table, filter for 'Movie', limit to 100
        movies = Media.query.filter_by(media_type='Movie').limit(100).all()
        return jsonify([m.to_dict() for m in movies])
    except Exception as e:
        return jsonify({'error': 'could not fetch movies', 'details': str(e)}), 500


@app.route('/health')
def health():
    """Simple DB health check."""
    try:
        # lightweight check
        with db.engine.connect() as conn:
            conn.execute(db.text('SELECT 1'))
        return jsonify({'db': 'ok'}), 200
    except Exception as e:
        return jsonify({'db': 'error', 'details': str(e)}), 500


if __name__ == '__main__':
    # If you run locally, set env vars or create a .env file. See README.md
    app.run(debug=True, port=5000) # Running on port 5000