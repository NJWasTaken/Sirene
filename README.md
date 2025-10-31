# Sirene - Entertainment Database Web Application

A Flask-based web application for browsing and reviewing movies, TV shows, anime, and video games. This project is designed as a DBMS mini project with a Netflix-style interface.

## Features

- **User Authentication**: Register, login, and manage user profiles
- **Browse Content**: Explore movies, TV shows, anime, and video games
- **Search & Filter**: Advanced search with filters by type and genre
- **Reviews & Ratings**: Write and read reviews for content
- **Detailed Information**: View cast, crew, episodes, awards, and platforms
- **Responsive Design**: Dark theme with red accent colors, optimized for all devices
- **Dynamic Content**: RESTful API endpoints for dynamic content loading

## Tech Stack

- **Backend**: Python Flask
- **Database**: MySQL
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Authentication**: Werkzeug for password hashing

## Prerequisites

- Python 3.8+
- MySQL 8.0+
- pip (Python package manager)

## Installation

### 1. Clone the Repository

```bash
cd sirene-flask-app
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up MySQL Database

1. Start your MySQL server
2. Create the database and import the schema:

```bash
mysql -u root -p

# In MySQL prompt:
CREATE DATABASE sirene;
USE sirene;
SOURCE sirene.sql;
EXIT;
```

### 5. Configure Environment

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` file with your MySQL credentials:
```
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
```

### 6. Update Flask Configuration

Edit `app.py` and update the MySQL configuration:

```python
app.config['MYSQL_USER'] = 'your_mysql_username'
app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
```

## Running the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Project Structure

```
sirene-flask-app/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment configuration
├── sirene.sql            # MySQL database schema
│
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   ├── media_details.html # Media details page
│   ├── search.html      # Search page
│   └── profile.html     # User profile page
│
├── static/              # Static files
│   ├── css/
│   │   └── main.css    # Custom styles
│   └── js/
│       └── app.js      # JavaScript functionality
│
└── README.md           # Project documentation
```

## Database Schema

The application uses the following main tables:

- **users**: User accounts
- **media**: Movies, TV shows, anime, and video games
- **review**: User reviews and ratings
- **person**: Actors, directors, and crew
- **genre**: Content genres
- **episode**: TV show episodes
- **award**: Awards information
- **platform**: Streaming/gaming platforms
- **production_company**: Production companies

## API Endpoints

### Public Routes
- `GET /` - Home page
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /register` - Registration page
- `POST /register` - Process registration

### Protected Routes (Login Required)
- `GET /profile` - User profile
- `GET /media/<id>` - Media details
- `GET /search` - Search page
- `GET /logout` - Logout user

### API Routes
- `GET /api/media/trending` - Get trending content
- `GET /api/media/top-rated` - Get top-rated content
- `GET /api/media/recent` - Get recent releases
- `GET /api/media/<type>` - Get content by type
- `GET /api/search?q=<query>` - Search content
- `POST /api/review` - Add a review

## Default Users

The database includes these default users for testing:

1. Username: `moviefanatic`, Email: `fanatic@email.com`
2. Username: `serieswatcher`, Email: `watcher@email.com`
3. Username: `animeguru`, Email: `guru@email.com`

Note: You'll need to register new users or update the password hashes in the database to login with these accounts.

## Features in Detail

### User Authentication
- Secure password hashing using Werkzeug
- Session-based authentication
- Protected routes with login_required decorator

### Content Browsing
- Carousel-style content display
- Dynamic loading of trending, top-rated, and recent content
- Categorized browsing by media type

### Search & Discovery
- Real-time search with debouncing
- Advanced filters by media type and genre
- Grid layout for search results

### Reviews System
- 10-point rating scale
- Text comments
- User review history in profile
- Average ratings calculation

### Responsive Design
- Mobile-first approach
- Custom Tailwind CSS configuration
- Dark theme with brand colors
- Smooth animations and transitions

## Development

### Adding New Features

1. **New Routes**: Add routes in `app.py`
2. **New Templates**: Create HTML files in `templates/`
3. **Database Changes**: Update schema and run migrations
4. **Styles**: Edit `static/css/main.css` or use Tailwind classes
5. **JavaScript**: Add functionality in `static/js/app.js`

### Database Modifications

To modify the database schema:

1. Export current data if needed
2. Modify the schema in MySQL
3. Update corresponding models in `app.py`
4. Test thoroughly

## Troubleshooting

### Common Issues

1. **MySQL Connection Error**
   - Verify MySQL is running
   - Check credentials in `app.py`
   - Ensure database exists

2. **Module Not Found**
   - Activate virtual environment
   - Run `pip install -r requirements.txt`

3. **Port Already in Use**
   - Change port in `app.py`: `app.run(port=5001)`

4. **Static Files Not Loading**
   - Clear browser cache
   - Check file paths in templates

## Security Considerations

- Change the `SECRET_KEY` in production
- Use environment variables for sensitive data
- Implement HTTPS in production
- Add CSRF protection for forms
- Implement rate limiting for API endpoints
- Sanitize user inputs

## Future Enhancements

- [ ] Add image upload for media posters
- [ ] Implement watchlist feature
- [ ] Add recommendation system
- [ ] Social features (follow users, share reviews)
- [ ] Advanced analytics dashboard
- [ ] Email notifications
- [ ] OAuth integration
- [ ] Mobile app API
- [ ] Caching with Redis
- [ ] Full-text search with Elasticsearch

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## License

This project is created for educational purposes as a DBMS mini project.

## Acknowledgments

- Flask documentation
- Tailwind CSS
- MySQL documentation
- Netflix UI for design inspiration

## Contact

For questions or support, please contact the project maintainer.

---

**Note**: This is an educational project. The placeholder images and sample data are for demonstration purposes only.