import sqlite3
import bcrypt
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path="fitness_challenge.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with all required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')),
                age_group TEXT CHECK(age_group IN ('18-25', '26-35', '36-45', '46-55', '56+')),
                location TEXT,
                team_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id) REFERENCES teams (team_id)
            )
        ''')
        
        # Create Teams table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                team_id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (user_id)
            )
        ''')
        
        # Create Sports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sports (
                sport_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sport_name TEXT UNIQUE NOT NULL,
                unit TEXT NOT NULL,
                points_per_unit REAL NOT NULL,
                description TEXT
            )
        ''')
        
        # Create Performances table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performances (
                performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                sport_id INTEGER NOT NULL,
                value REAL NOT NULL,
                points_calculated REAL NOT NULL,
                date_recorded DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (sport_id) REFERENCES sports (sport_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize default sports data
        self.init_default_sports()
    
    def init_default_sports(self):
        """Initialize default sports with point calculations"""
        default_sports = [
            ("Running", "km", 10.0, "Distance running - 10 points per km"),
            ("Cycling", "km", 3.0, "Cycling - 3 points per km"),
            ("Swimming", "km", 50.0, "Swimming - 50 points per km"),
            ("Walking", "km", 5.0, "Walking - 5 points per km"),
            ("Push-ups", "reps", 0.5, "Push-ups - 0.5 points per rep"),
            ("Sit-ups", "reps", 0.3, "Sit-ups - 0.3 points per rep"),
            ("Plank", "minutes", 2.0, "Plank hold - 2 points per minute"),
            ("Yoga", "sessions", 15.0, "Yoga session (30 min) - 15 points per session"),
            ("Weight Training", "sessions", 20.0, "Weight training (45 min) - 20 points per session"),
            ("Basketball", "hours", 12.0, "Basketball - 12 points per hour"),
            ("Tennis", "hours", 15.0, "Tennis - 15 points per hour"),
            ("Football/Soccer", "hours", 18.0, "Football/Soccer - 18 points per hour")
        ]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for sport_name, unit, points_per_unit, description in default_sports:
            cursor.execute('''
                INSERT OR IGNORE INTO sports (sport_name, unit, points_per_unit, description)
                VALUES (?, ?, ?, ?)
            ''', (sport_name, unit, points_per_unit, description))
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password, hashed):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_user(self, username, password, full_name, email, gender=None, age_group=None, location=None):
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash, full_name, email, gender, age_group, location)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, full_name, email, gender, age_group, location))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
        except sqlite3.IntegrityError as e:
            conn.close()
            raise e
    
    def authenticate_user(self, username, password):
        """Authenticate user login"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id, password_hash FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result and self.verify_password(password, result[1]):
            return result[0]  # Return user_id
        return None
    
    def get_user_by_id(self, user_id):
        """Get user information by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.*, t.team_name 
            FROM users u 
            LEFT JOIN teams t ON u.team_id = t.team_id 
            WHERE u.user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        return result
    
    def get_all_sports(self):
        """Get all available sports"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM sports ORDER BY sport_name')
        results = cursor.fetchall()
        conn.close()
        return results
    
    def calculate_points(self, sport_id, value):
        """Calculate points for a performance"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT points_per_unit FROM sports WHERE sport_id = ?', (sport_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return value * result[0]
        return 0
    
    def add_performance(self, user_id, sport_id, value, date_recorded, notes=None):
        """Add a new performance entry"""
        points = self.calculate_points(sport_id, value)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performances (user_id, sport_id, value, points_calculated, date_recorded, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, sport_id, value, points, date_recorded, notes))
        
        performance_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return performance_id
    
    def get_user_performances(self, user_id):
        """Get all performances for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.*, s.sport_name, s.unit
            FROM performances p
            JOIN sports s ON p.sport_id = s.sport_id
            WHERE p.user_id = ?
            ORDER BY p.date_recorded DESC
        ''', (user_id,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def create_team(self, team_name, description, created_by):
        """Create a new team"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO teams (team_name, description, created_by)
                VALUES (?, ?, ?)
            ''', (team_name, description, created_by))
            
            team_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return team_id
        except sqlite3.IntegrityError as e:
            conn.close()
            raise e
    
    def get_all_teams(self):
        """Get all teams"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.*, u.full_name as creator_name,
                   COUNT(members.user_id) as member_count
            FROM teams t
            JOIN users u ON t.created_by = u.user_id
            LEFT JOIN users members ON t.team_id = members.team_id
            GROUP BY t.team_id
            ORDER BY t.team_name
        ''')
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def join_team(self, user_id, team_id):
        """Add user to a team"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET team_id = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?', 
                      (team_id, user_id))
        
        conn.commit()
        conn.close()

