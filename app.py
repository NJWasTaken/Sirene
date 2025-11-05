import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from functools import wraps
import dotenv
from math import ceil

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

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('user_role') != 'admin':
            return redirect(url_for('index'))
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
            session['user_role'] = user.get('UserRole', 'user')  # Default to 'user' if column missing
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

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard to manage content"""

    # Pagination
    PER_PAGE = 20
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * PER_PAGE
    
    # Filtering
    filter_type = request.args.get('type', '')
    media_types = ['Movie', 'TV Show', 'Anime', 'Video Game']
    
    base_query = "FROM media WHERE 1=1"
    params = []
    
    if filter_type:
        base_query += " AND MediaType = %s"
        params.append(filter_type)

    cur = mysql.connection.cursor()
    
    # Get total count for pagination
    cur.execute(f"SELECT COUNT(*) as count {base_query}", params)
    total_count = cur.fetchone()['count']
    total_pages = ceil(total_count / PER_PAGE)
    
    # Get media for the current page
    query = f"SELECT * {base_query} ORDER BY Title ASC LIMIT %s OFFSET %s"
    params.extend([PER_PAGE, offset])
    
    cur.execute(query, params)
    all_media = cur.fetchall()
    cur.close()
    
    return render_template('admin_dashboard.html', 
                         all_media=all_media,
                         page=page,
                         total_pages=total_pages,
                         filter_type=filter_type,
                         media_types=media_types)

@app.route('/admin/media/new', methods=['GET', 'POST'])
@admin_required
def admin_add_media():
    """Add a new media item"""
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        title = request.form['title']
        synopsis = request.form['synopsis']
        media_type = request.form['media_type']
        release_date = request.form['release_date'] or None
        duration = request.form['duration'] or None

        cur.execute("""
            INSERT INTO media (Title, Synopsis, MediaType, ReleaseDate, DurationMinutes)
            VALUES (%s, %s, %s, %s, %s)
        """, (title, synopsis, media_type, release_date, duration))
        mysql.connection.commit()
        
        # Get the new MediaID
        new_media_id = cur.lastrowid

        # Link platforms if any selected
        platform_ids = request.form.getlist('platform_ids')
        if platform_ids:
            insert_data = [(new_media_id, pid) for pid in platform_ids]
            cur.executemany("INSERT INTO media_platform (MediaID, PlatformID) VALUES (%s, %s)", insert_data)
            mysql.connection.commit()
        
        cur.close()
        
        # Redirect to the new edit page to add genres/cast
        return redirect(url_for('admin_edit_media', media_id=new_media_id))

    # GET request
    # Fetch all genres to display on the form
    cur.execute("SELECT * FROM genre ORDER BY GenreName")
    all_genres = cur.fetchall()
    # Fetch all platforms to display "Available On" options
    cur.execute("SELECT PlatformID, PlatformName FROM platform ORDER BY PlatformName")
    all_platforms = cur.fetchall()

    cur.close()

    return render_template('admin_edit_media.html', 
                         media=None, 
                         title="Add New Media",
                         all_genres=all_genres,
                         all_platforms=all_platforms,
                         linked_genre_ids=set(),
                         linked_platform_ids=set())

@app.route('/admin/media/<int:media_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_media(media_id):
    """Edit an existing media item"""
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        # 1. Update Media Details
        title = request.form['title']
        synopsis = request.form['synopsis']
        media_type = request.form['media_type']
        release_date = request.form['release_date'] or None
        duration = request.form['duration'] or None

        cur.execute("""
            UPDATE media
            SET Title = %s, Synopsis = %s, MediaType = %s, ReleaseDate = %s, DurationMinutes = %s
            WHERE MediaID = %s
        """, (title, synopsis, media_type, release_date, duration, media_id))
        
        # 2. Update Genres
        genre_ids = request.form.getlist('genre_ids')
        platform_ids = request.form.getlist('platform_ids')
        try:
            # Delete old genres first
            cur.execute("DELETE FROM media_genre WHERE MediaID = %s", [media_id])
            
            # Insert new genres if any were selected
            if genre_ids:
                insert_data = [(media_id, genre_id) for genre_id in genre_ids]
                cur.executemany("INSERT INTO media_genre (MediaID, GenreID) VALUES (%s, %s)", insert_data)
            
            # Delete old platform links
            cur.execute("DELETE FROM media_platform WHERE MediaID = %s", [media_id])
            # Insert new platform links
            if platform_ids:
                insert_plat = [(media_id, pid) for pid in platform_ids]
                cur.executemany("INSERT INTO media_platform (MediaID, PlatformID) VALUES (%s, %s)", insert_plat)
            
            mysql.connection.commit()
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error updating genres: {e}") 
        
        cur.close()
        return redirect(url_for('admin_edit_media', media_id=media_id))

    # GET request: fetch media, all genres, and linked genres
    cur.execute("SELECT * FROM media WHERE MediaID = %s", [media_id])
    media = cur.fetchone()
    
    cur.execute("SELECT * FROM genre ORDER BY GenreName")
    all_genres = cur.fetchall()
    
    cur.execute("SELECT GenreID FROM media_genre WHERE MediaID = %s", [media_id])
    linked_genres_raw = cur.fetchall()
    linked_genre_ids = {g['GenreID'] for g in linked_genres_raw} # Use a set
    
    # Fetch available platforms and linked platforms
    cur.execute("SELECT PlatformID, PlatformName FROM platform ORDER BY PlatformName")
    all_platforms = cur.fetchall()
    cur.execute("SELECT PlatformID FROM media_platform WHERE MediaID = %s", [media_id])
    linked_platforms_raw = cur.fetchall()
    linked_platform_ids = {p['PlatformID'] for p in linked_platforms_raw}

    cur.close()
    
    if not media:
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_edit_media.html', 
                         media=media, 
                         title="Edit Media",
                         all_genres=all_genres,
                         all_platforms=all_platforms,
                         linked_genre_ids=linked_genre_ids,
                         linked_platform_ids=linked_platform_ids)

@app.route('/admin/media/<int:media_id>/delete', methods=['POST'])
@admin_required
def admin_delete_media(media_id):
    """Delete a media item"""
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM media WHERE MediaID = %s", [media_id])
    mysql.connection.commit()
    cur.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/media/<int:media_id>/assets', methods=['GET', 'POST'])
@admin_required
def admin_manage_media_assets(media_id):
    """Manage images and videos for a media item"""
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        action_type = request.form.get('action_type')
        
        try:
            if action_type == 'add_image':
                cur.execute("""
                    INSERT INTO mediaimage (MediaID, ImageUrl, Caption, Type, SortOrder)
                    VALUES (%s, %s, %s, %s, %s)
                """, (media_id, 
                      request.form['image_url'], 
                      request.form.get('caption'), 
                      request.form['image_type'], 
                      request.form.get('sort_order', 0)))
            
            elif action_type == 'add_video':
                cur.execute("""
                    INSERT INTO mediavideo (MediaID, VideoUrl, Title, Type, SortOrder)
                    VALUES (%s, %s, %s, %s, %s)
                """, (media_id,
                      request.form['video_url'],
                      request.form['video_title'],
                      request.form['video_type'],
                      request.form.get('sort_order', 0)))
            
            mysql.connection.commit()
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error adding asset: {e}") # Add flash messaging here for production
            
        return redirect(url_for('admin_manage_media_assets', media_id=media_id))

    # GET request
    cur.execute("SELECT * FROM media WHERE MediaID = %s", [media_id])
    media = cur.fetchone()
    cur.execute("SELECT * FROM mediaimage WHERE MediaID = %s ORDER BY Type, SortOrder", [media_id])
    images = cur.fetchall()
    cur.execute("SELECT * FROM mediavideo WHERE MediaID = %s ORDER BY Type, SortOrder", [media_id])
    videos = cur.fetchall()
    cur.close()

    if not media:
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_manage_media_assets.html', media=media, images=images, videos=videos)

@app.route('/admin/media/<int:media_id>/cast', methods=['GET', 'POST'])
@admin_required
def admin_manage_media_cast(media_id):
    """Manage cast & crew for a specific media item"""
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        try:
            if action == 'add':
                person_id = request.form.get('person_id')
                role = request.form.get('role', 'Actor').strip()
                if person_id and role:
                    cur.execute("""
                        INSERT INTO media_person_role (MediaID, PersonID, Role)
                        VALUES (%s, %s, %s)
                    """, (media_id, person_id, role))

            elif action == 'delete':
                person_id = request.form.get('person_id')
                role = request.form.get('role')
                if person_id and role:
                    cur.execute("""
                        DELETE FROM media_person_role
                        WHERE MediaID = %s AND PersonID = %s AND Role = %s
                    """, (media_id, person_id, role))
                    
            mysql.connection.commit()
        except Exception as e:
            mysql.connection.rollback()
            print(f"Error managing cast: {e}")
        
        cur.close()
        return redirect(url_for('admin_manage_media_cast', media_id=media_id))

    # GET Request
    cur.execute("SELECT MediaID, Title FROM media WHERE MediaID = %s", [media_id])
    media = cur.fetchone()
    
    cur.execute("""
        SELECT p.PersonID, p.Name, mpr.Role
        FROM media_person_role mpr
        JOIN person p ON mpr.PersonID = p.PersonID
        WHERE mpr.MediaID = %s
        ORDER BY p.Name, mpr.Role
    """, [media_id])
    linked_cast = cur.fetchall()
    
    cur.execute("SELECT PersonID, Name FROM person ORDER BY Name")
    all_people = cur.fetchall()
    
    cur.close()
    
    if not media:
        return redirect(url_for('admin_dashboard'))
        
    return render_template('admin_manage_media_cast.html',
                         media=media,
                         linked_cast=linked_cast,
                         all_people=all_people)

@app.route('/admin/image/<int:image_id>/delete', methods=['POST'])
@admin_required
def admin_delete_image(image_id):
    """Delete an image asset"""
    cur = mysql.connection.cursor()
    # Get MediaID first to redirect back
    cur.execute("SELECT MediaID FROM mediaimage WHERE ImageID = %s", [image_id])
    result = cur.fetchone()
    if result:
        media_id = result['MediaID']
        cur.execute("DELETE FROM mediaimage WHERE ImageID = %s", [image_id])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('admin_manage_media_assets', media_id=media_id))
    
    cur.close()
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/video/<int:video_id>/delete', methods=['POST'])
@admin_required
def admin_delete_video(video_id):
    """Delete a video asset"""
    cur = mysql.connection.cursor()
    # Get MediaID first to redirect back
    cur.execute("SELECT MediaID FROM mediavideo WHERE VideoID = %s", [video_id])
    result = cur.fetchone()
    if result:
        media_id = result['MediaID']
        cur.execute("DELETE FROM mediavideo WHERE VideoID = %s", [video_id])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('admin_manage_media_assets', media_id=media_id))

    cur.close()
    return redirect(url_for('admin_dashboard'))

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

    # Get images
    cur.execute("""SELECT * FROM mediaimage 
                WHERE MediaID = %s 
                ORDER BY Type, SortOrder""", [media_id])
    images = cur.fetchall()
    
    # Get videos
    cur.execute("""SELECT * FROM mediavideo 
                WHERE MediaID = %s 
                ORDER BY Type, SortOrder""", [media_id])
    videos = cur.fetchall()
    
    cur.close()

    poster = next((img for img in images if img['Type'] == 'Poster'), None)
    backdrop = next((img for img in images if img['Type'] == 'Backdrop'), None)
    gallery = [img for img in images if img['Type'] == 'Gallery']
    
    return render_template('movie_details.html', 
                         media=media, 
                         people=people, 
                         reviews=reviews,
                         platforms=platforms,
                         episodes=episodes,
                         awards=awards,
                         poster=poster,
                         backdrop=backdrop,
                         gallery=gallery,
                         videos=videos)

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
        SELECT m.MediaID, m.Title, m.MediaType, m.Synopsis, m.ReleaseDate, m.DurationMinutes,
               GROUP_CONCAT(DISTINCT g.GenreName) as genres,
               (SELECT ImageUrl FROM mediaimage WHERE MediaID = m.MediaID AND Type = 'Poster' LIMIT 1) as poster_url
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
    
    sql += " GROUP BY m.MediaID, m.Title, m.MediaType, m.Synopsis, m.ReleaseDate, m.DurationMinutes ORDER BY m.ReleaseDate DESC"
    
    if params:
        cur.execute(sql, params)
    else:
        cur.execute(sql)
    
    results = cur.fetchall()
    print(f"Search Debug - Query: '{query}', Type: '{media_type}', Genre: '{genre}'")
    print(f"Search Debug - Results count: {len(results)}")
    if results and len(results) > 0:
        print(f"Search Debug - First result: {results[0]}")
    
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

@app.route('/browse')
@login_required
def browse():
    """Browse page with filters"""
    cur = mysql.connection.cursor()
    
    # Get all genres for filter
    cur.execute("SELECT DISTINCT GenreName FROM genre ORDER BY GenreName")
    genres = cur.fetchall()
    
    cur.close()
    
    return render_template('browse.html', genres=genres)

@app.route('/api/browse')
@login_required
def api_browse():
    """API endpoint for browse with filters"""
    media_type = request.args.get('type', '')
    genre = request.args.get('genre', '')
    sort_by = request.args.get('sort', 'recent')  # recent, rating, title
    
    cur = mysql.connection.cursor()
    
    # Build the query
    sql = """
        SELECT DISTINCT m.*, 
               AVG(r.Rating) as avg_rating,
               COUNT(r.ReviewID) as review_count,
               (SELECT ImageUrl FROM mediaimage WHERE MediaID = m.MediaID AND Type = 'Poster' LIMIT 1) as poster_url
        FROM media m
        LEFT JOIN review r ON m.MediaID = r.MediaID
        LEFT JOIN media_genre mg ON m.MediaID = mg.MediaID
        LEFT JOIN genre g ON mg.GenreID = g.GenreID
        WHERE 1=1
    """
    params = []
    
    if media_type:
        sql += " AND m.MediaType = %s"
        params.append(media_type)
    
    if genre:
        sql += " AND g.GenreName = %s"
        params.append(genre)
    
    sql += " GROUP BY m.MediaID"
    
    # Add sorting
    if sort_by == 'rating':
        sql += " ORDER BY avg_rating DESC, review_count DESC"
    elif sort_by == 'title':
        sql += " ORDER BY m.Title ASC"
    else:  # recent
        sql += " ORDER BY m.ReleaseDate DESC"
    
    sql += " LIMIT 50"
    
    cur.execute(sql, params)
    results = cur.fetchall()
    cur.close()
    
    return jsonify(results)

# API Routes for dynamic content
@app.route('/api/media/trending')
@login_required
def api_trending():
    """Get trending media (based on recent reviews)"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT m.*, COUNT(r.ReviewID) as review_count, AVG(r.Rating) as avg_rating,
               (SELECT ImageUrl FROM mediaimage WHERE MediaID = m.MediaID AND Type = 'Poster' LIMIT 1) as poster_url
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
        SELECT m.*, AVG(r.Rating) as avg_rating, COUNT(r.ReviewID) as review_count,
               (SELECT ImageUrl FROM mediaimage WHERE MediaID = m.MediaID AND Type = 'Poster' LIMIT 1) as poster_url
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
        SELECT m.*,
               (SELECT ImageUrl FROM mediaimage WHERE MediaID = m.MediaID AND Type = 'Poster' LIMIT 1) as poster_url
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
        SELECT m.*, AVG(r.Rating) as avg_rating,
               (SELECT ImageUrl FROM mediaimage WHERE MediaID = m.MediaID AND Type = 'Poster' LIMIT 1) as poster_url
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
    """API endpoint for search autocomplete"""
    query = request.args.get('q', '')
    
    if len(query) < 2:
        return jsonify([])
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT m.*, 
               GROUP_CONCAT(DISTINCT g.GenreName) as genres,
               AVG(r.Rating) as avg_rating,
               (SELECT ImageUrl FROM mediaimage WHERE MediaID = m.MediaID AND Type = 'Poster' LIMIT 1) as poster_url
        FROM media m
        LEFT JOIN media_genre mg ON m.MediaID = mg.MediaID
        LEFT JOIN genre g ON mg.GenreID = g.GenreID
        LEFT JOIN review r ON m.MediaID = r.MediaID
        WHERE m.Title LIKE %s OR m.Synopsis LIKE %s
        GROUP BY m.MediaID
        ORDER BY 
            CASE 
                WHEN m.Title LIKE %s THEN 1
                ELSE 2
            END,
            m.Title ASC
        LIMIT 10
    """, [f"%{query}%", f"%{query}%", f"{query}%"])
    results = cur.fetchall()
    cur.close()
    
    # Format results for frontend
    formatted_results = []
    for item in results:
        formatted_results.append({
            'id': item['MediaID'],
            'title': item['Title'],
            'media_type': item['MediaType'],
            'synopsis': item['Synopsis'][:150] + '...' if item['Synopsis'] and len(item['Synopsis']) > 150 else item['Synopsis'],
            'release_date': str(item['ReleaseDate']) if item['ReleaseDate'] else None,
            'genres': item['genres'],
            'avg_rating': float(item['avg_rating']) if item['avg_rating'] else 0,
            'poster_url': item['poster_url']
        })
    
    return jsonify(formatted_results)

@app.route('/api/media/featured')
@login_required
def api_featured():
    """Get 4 random featured media items with backdrop images"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT m.*, 
               (SELECT ImageUrl FROM mediaimage WHERE MediaID = m.MediaID AND Type = 'Backdrop' LIMIT 1) as backdrop_url,
               (SELECT ImageUrl FROM mediaimage WHERE MediaID = m.MediaID AND Type = 'Poster' LIMIT 1) as poster_url,
               AVG(r.Rating) as avg_rating
        FROM media m
        LEFT JOIN review r ON m.MediaID = r.MediaID
        WHERE EXISTS (SELECT 1 FROM mediaimage WHERE MediaID = m.MediaID AND Type = 'Backdrop')
        GROUP BY m.MediaID
        ORDER BY RAND()
        LIMIT 4
    """)
    results = cur.fetchall()
    cur.close()
    return jsonify(results)

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
        SELECT r.*, m.Title, m.MediaType,
               (SELECT ImageUrl FROM mediaimage WHERE MediaID = m.MediaID AND Type = 'Poster' LIMIT 1) as poster_url
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