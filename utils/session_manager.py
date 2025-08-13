import streamlit as st
from database.db_manager import DatabaseManager

class SessionManager:
    def __init__(self):
        self.db = DatabaseManager()
        
        # Initialize session state variables
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None
        if 'username' not in st.session_state:
            st.session_state.username = None
        if 'user_data' not in st.session_state:
            st.session_state.user_data = None
    
    def login(self, username, password):
        """Attempt to log in user"""
        user_id = self.db.authenticate_user(username, password)
        if user_id:
            st.session_state.logged_in = True
            st.session_state.user_id = user_id
            st.session_state.username = username
            self.refresh_user_data()
            return True
        return False
    
    def logout(self):
        """Log out current user"""
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.user_data = None
    
    def refresh_user_data(self):
        """Refresh user data from database"""
        if st.session_state.user_id:
            st.session_state.user_data = self.db.get_user_by_id(st.session_state.user_id)
    
    def is_logged_in(self):
        """Check if user is logged in"""
        return st.session_state.logged_in
    
    def get_current_user_id(self):
        """Get current user ID"""
        return st.session_state.user_id
    
    def get_current_username(self):
        """Get current username"""
        return st.session_state.username
    
    def get_user_data(self):
        """Get current user data"""
        return st.session_state.user_data
    
    def require_login(self):
        """Decorator/function to require login for a page"""
        if not self.is_logged_in():
            st.warning("Please log in to access this page.")
            st.stop()
    
    def register_user(self, username, password, full_name, email, gender=None, age_group=None, location=None):
        """Register a new user"""
        try:
            user_id = self.db.create_user(username, password, full_name, email, gender, age_group, location)
            return user_id
        except Exception as e:
            return None

