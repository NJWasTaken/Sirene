from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from functools import wraps
import dotenv

dotenv.load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')  
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')  
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'sirene')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # If this is an API route, return JSON 401 instead of redirecting
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Unauthorized', 'message': 'Please log in'}), 401
            # For normal routes, redirect to login
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Main browse page"""
    # Pass login state to template so homepage JS can conditionally load API data
    logged_in = 'user_id' in session
    return render_template('index.html', logged_in=logged_in)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE Username = %s", [username])
        user = cur.fetchone()
        cur.close()
        
        if user and check_password_hash(user['PasswordHash'], password):
            session['user_id'] = user['UserID']
            session['username'] = user['Username']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Hash the password
        password_hash = generate_password_hash(password)
        
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO users (Username, Email, PasswordHash) 
                VALUES (%s, %s, %s)
            """, (username, email, password_hash))
            mysql.connection.commit()
            cur.close()
            
            return redirect(url_for('login'))
        except Exception as e:
            return render_template('register.html', error="Username or email already exists")
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/media/<int:media_id>')
@login_required
def media_details(media_id):
    """Media details page"""
    cur = mysql.connection.cursor()
    
    # Get media details
    cur.execute("""
        SELECT m.*, 
               GROUP_CONCAT(DISTINCT g.GenreName) as genres
        FROM media m
        LEFT JOIN media_genre mg ON m.MediaID = mg.MediaID
        LEFT JOIN genre g ON mg.GenreID = g.GenreID
        WHERE m.MediaID = %s
        GROUP BY m.MediaID
    """, [media_id])
    media = cur.fetchone()
    
    # Get cast and crew
    cur.execute("""
        SELECT p.*, mpr.Role
        FROM media_person_role mpr
        JOIN person p ON mpr.PersonID = p.PersonID
        WHERE mpr.MediaID = %s
        ORDER BY mpr.Role
    """, [media_id])
    people = cur.fetchall()
    
    # Get reviews
    cur.execute("""
        SELECT r.*, u.Username
        FROM review r
        JOIN users u ON r.UserID = u.UserID
        WHERE r.MediaID = %s
        ORDER BY r.ReviewDate DESC
    """, [media_id])
    reviews = cur.fetchall()
    
    # Get platforms
    cur.execute("""
        SELECT p.PlatformName
        FROM media_platform mp
        JOIN platform p ON mp.PlatformID = p.PlatformID
        WHERE mp.MediaID = %s
    """, [media_id])
    platforms = cur.fetchall()
    
    # Get episodes if TV show
    episodes = []
    if media and media['MediaType'] in ['TV Show', 'Anime']:
        cur.execute("""
            SELECT * FROM episode
            WHERE MediaID = %s
            ORDER BY SeasonNumber, EpisodeNumber
        """, [media_id])
        episodes = cur.fetchall()
    
    # Get awards
    cur.execute("""
        SELECT a.AwardName, a.AwardCategory, aw.YearWon, p.Name as PersonName
        FROM awardwon aw
        JOIN award a ON aw.AwardID = a.AwardID
        LEFT JOIN person p ON aw.PersonID = p.PersonID
        WHERE aw.MediaID = %s
    """, [media_id])
    awards = cur.fetchall()
    
    cur.close()
    
    return render_template('movie_details.html', 
                         media=media, 
                         people=people, 
                         reviews=reviews,
                         platforms=platforms,
                         episodes=episodes,
                         awards=awards)

@app.route('/search')
@login_required
def search():
    """Search page"""
    query = request.args.get('q', '')
    media_type = request.args.get('type', '')
    genre = request.args.get('genre', '')
    
    cur = mysql.connection.cursor()
    
    # Build the query
    sql = """
        SELECT DISTINCT m.*, 
               GROUP_CONCAT(DISTINCT g.GenreName) as genres
        FROM media m
        LEFT JOIN media_genre mg ON m.MediaID = mg.MediaID
        LEFT JOIN genre g ON mg.GenreID = g.GenreID
        WHERE 1=1
    """
    params = []
    
    if query:
        sql += " AND (m.Title LIKE %s OR m.Synopsis LIKE %s)"
        params.extend([f"%{query}%", f"%{query}%"])
    
    if media_type:
        sql += " AND m.MediaType = %s"
        params.append(media_type)
    
    if genre:
        sql += " AND g.GenreName = %s"
        params.append(genre)
    
    sql += " GROUP BY m.MediaID ORDER BY m.ReleaseDate DESC"
    
    cur.execute(sql, params)
    results = cur.fetchall()
    
    # Get all genres for filter dropdown
    cur.execute("SELECT DISTINCT GenreName FROM genre ORDER BY GenreName")
    genres = cur.fetchall()
    
    cur.close()
    
    return render_template('search.html', 
                         results=results, 
                         query=query,
                         genres=genres,
                         selected_type=media_type,
                         selected_genre=genre)

# API Routes for dynamic content
@app.route('/api/media/trending')
@login_required
def api_trending():
    """Get trending media (based on recent reviews)"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT m.*, COUNT(r.ReviewID) as review_count, AVG(r.Rating) as avg_rating
        FROM media m
        LEFT JOIN review r ON m.MediaID = r.MediaID
        WHERE r.ReviewDate >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        GROUP BY m.MediaID
        ORDER BY review_count DESC, avg_rating DESC
        LIMIT 10
    """)
    results = cur.fetchall()
    cur.close()
    return jsonify(results)

@app.route('/api/media/top-rated')
@login_required
def api_top_rated():
    """Get top-rated media"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT m.*, AVG(r.Rating) as avg_rating, COUNT(r.ReviewID) as review_count
        FROM media m
        LEFT JOIN review r ON m.MediaID = r.MediaID
        GROUP BY m.MediaID
        HAVING review_count > 0
        ORDER BY avg_rating DESC
        LIMIT 10
    """)
    results = cur.fetchall()
    cur.close()
    return jsonify(results)

@app.route('/api/media/recent')
@login_required
def api_recent():
    """Get recently released media"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT m.*
        FROM media m
        WHERE m.ReleaseDate <= CURDATE()
        ORDER BY m.ReleaseDate DESC
        LIMIT 10
    """)
    results = cur.fetchall()
    cur.close()
    return jsonify(results)

@app.route('/api/media/<media_type>')
@login_required
def api_media_by_type(media_type):
    """Get media by type"""
    cur = mysql.connection.cursor()
    
    # Map URL parameter to database enum values
    type_map = {
        'movies': 'Movie',
        'tv': 'TV Show',
        'anime': 'Anime',
        'games': 'Video Game'
    }
    
    db_type = type_map.get(media_type)
    if not db_type:
        return jsonify([])
    
    cur.execute("""
        SELECT m.*, AVG(r.Rating) as avg_rating
        FROM media m
        LEFT JOIN review r ON m.MediaID = r.MediaID
        WHERE m.MediaType = %s
        GROUP BY m.MediaID
        ORDER BY m.ReleaseDate DESC
        LIMIT 10
    """, [db_type])
    results = cur.fetchall()
    cur.close()
    return jsonify(results)

@app.route('/api/search')
@login_required
def api_search():
    """API endpoint for search"""
    query = request.args.get('q', '')
    
    if len(query) < 2:
        return jsonify([])
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT m.*, 
               GROUP_CONCAT(DISTINCT g.GenreName) as genres,
               AVG(r.Rating) as avg_rating
        FROM media m
        LEFT JOIN media_genre mg ON m.MediaID = mg.MediaID
        LEFT JOIN genre g ON mg.GenreID = g.GenreID
        LEFT JOIN review r ON m.MediaID = r.MediaID
        WHERE m.Title LIKE %s OR m.Synopsis LIKE %s
        GROUP BY m.MediaID
        ORDER BY m.ReleaseDate DESC
        LIMIT 20
    """, [f"%{query}%", f"%{query}%"])
    results = cur.fetchall()
    cur.close()
    
    # Format results for frontend
    formatted_results = []
    for item in results:
        formatted_results.append({
            'id': item['MediaID'],
            'title': item['Title'],
            'media_type': item['MediaType'].lower().replace(' ', ''),
            'synopsis': item['Synopsis'],
            'release_date': str(item['ReleaseDate']) if item['ReleaseDate'] else None,
            'genres': item['genres'],
            'avg_rating': float(item['avg_rating']) if item['avg_rating'] else 0
        })
    
    return jsonify(formatted_results)

@app.route('/api/review', methods=['POST'])
@login_required
def api_add_review():
    """Add a review"""
    data = request.json
    media_id = data.get('media_id')
    rating = data.get('rating')
    comment = data.get('comment')
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO review (UserID, MediaID, Rating, Comment)
            VALUES (%s, %s, %s, %s)
        """, (session['user_id'], media_id, rating, comment))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    cur = mysql.connection.cursor()
    
    # Get user details
    cur.execute("SELECT * FROM users WHERE UserID = %s", [session['user_id']])
    user = cur.fetchone()
    
    # Get user's reviews
    cur.execute("""
        SELECT r.*, m.Title
        FROM review r
        JOIN media m ON r.MediaID = m.MediaID
        WHERE r.UserID = %s
        ORDER BY r.ReviewDate DESC
    """, [session['user_id']])
    reviews = cur.fetchall()
    
    cur.close()
    
    return render_template('profile.html', user=user, reviews=reviews)

if __name__ == '__main__':
    app.run(debug=True, port=5000)