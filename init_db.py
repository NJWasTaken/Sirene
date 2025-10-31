#!/usr/bin/env python
"""
Database initialization script for Sirene application.
This script sets up the database and optionally adds test data.
"""

import mysql.connector
from mysql.connector import Error
import sys
import os
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def create_connection(host, user, password, database=None):
    """Create a database connection."""
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def execute_sql_file(connection, filepath):
    """Execute SQL statements from a file."""
    cursor = connection.cursor()
    
    try:
        with open(filepath, 'r') as file:
            sql_commands = file.read()
            
        # Split commands by semicolon and execute
        for command in sql_commands.split(';'):
            if command.strip():
                cursor.execute(command)
        
        connection.commit()
        print(f"Successfully executed SQL file: {filepath}")
        return True
        
    except Error as e:
        print(f"Error executing SQL file: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()

def update_user_passwords(connection):
    """Update user passwords with proper hashes."""
    cursor = connection.cursor()
    
    users = [
        ('moviefanatic', 'password123'),
        ('serieswatcher', 'password456'),
        ('animeguru', 'password789')
    ]
    
    try:
        for username, password in users:
            hashed = generate_password_hash(password)
            cursor.execute(
                "UPDATE users SET PasswordHash = %s WHERE Username = %s",
                (hashed, username)
            )
        
        connection.commit()
        print("User passwords updated successfully")
        print("\nTest credentials:")
        for username, password in users:
            print(f"  Username: {username}, Password: {password}")
        
        return True
        
    except Error as e:
        print(f"Error updating passwords: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()

def add_sample_data(connection):
    """Add additional sample data to the database."""
    cursor = connection.cursor()
    
    try:
        # Add more sample reviews
        sample_reviews = [
            (2, 1, 8.5, "Great show, but the pace slows down in middle seasons."),
            (3, 1, 9.8, "Masterpiece! The character development is incredible."),
            (1, 3, 8.7, "Amazing animation and storytelling. The ending was perfect."),
            (2, 4, 7.5, "Good superhero show, but could have been better."),
            (3, 5, 8.0, "Brilliant satire about wealth and power."),
            (1, 6, 7.0, "Fun adaptation, but the anime is better."),
            (2, 7, 9.0, "Incredible film! The social commentary is spot on."),
        ]
        
        for user_id, media_id, rating, comment in sample_reviews:
            try:
                cursor.execute("""
                    INSERT INTO review (UserID, MediaID, Rating, Comment)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, media_id, rating, comment))
            except mysql.connector.IntegrityError:
                # Skip if review already exists
                pass
        
        connection.commit()
        print("Sample data added successfully")
        return True
        
    except Error as e:
        print(f"Error adding sample data: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()

def main():
    """Main function to initialize the database."""
    print("Sirene Database Initialization Script")
    print("=" * 40)
    
    # Get database credentials
    host = input("MySQL Host [localhost]: ") or "localhost"
    user = input("MySQL User [root]: ") or "root"
    password = input("MySQL Password: ")
    
    # Connect to MySQL server (without database)
    print("\nConnecting to MySQL server...")
    connection = create_connection(host, user, password)
    
    if not connection:
        print("Failed to connect to MySQL server.")
        sys.exit(1)
    
    cursor = connection.cursor()
    
    try:
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS sirene")
        print("Database 'sirene' created/verified")
        
        # Switch to the database
        cursor.execute("USE sirene")
        
        # Check if tables exist
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if len(tables) == 0:
            print("\nNo tables found. Initializing database schema...")
            
            # Look for SQL file
            sql_file = "sirene.sql"
            if not os.path.exists(sql_file):
                print(f"Error: {sql_file} not found in current directory")
                sys.exit(1)
            
            # Execute SQL file
            if execute_sql_file(connection, sql_file):
                print("Database schema created successfully")
            else:
                print("Failed to create database schema")
                sys.exit(1)
        else:
            print(f"\nFound {len(tables)} existing tables in database")
        
        # Update user passwords
        print("\nUpdating user passwords...")
        update_user_passwords(connection)
        
        # Ask if user wants to add sample data
        add_samples = input("\nAdd additional sample data? (y/n): ").lower()
        if add_samples == 'y':
            add_sample_data(connection)
        
        print("\n" + "=" * 40)
        print("Database initialization complete!")
        print("\nYou can now run the Flask application with:")
        print("  python app.py")
        print("\nDefault login credentials have been set up.")
        
    except Error as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()