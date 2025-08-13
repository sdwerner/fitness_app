import streamlit as st
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.session_manager import SessionManager
from database.db_manager import DatabaseManager
from analytics.leaderboards import LeaderboardManager
from analytics.personal_progress import PersonalProgressTracker

# Configure Streamlit page
st.set_page_config(
    page_title="Fitness Challenge App",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session manager
session_manager = SessionManager()

def main():
    """Main application function"""
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sidebar-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown('<h1 class="main-header">🏃‍♂️ Fitness Challenge App</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown('<h2 class="sidebar-header">Navigation</h2>', unsafe_allow_html=True)
        
        if session_manager.is_logged_in():
            user_data = session_manager.get_user_data()
            st.success(f"Welcome, {user_data[3]}!")  # full_name is at index 3
            
            # Navigation menu for logged-in users
            page = st.selectbox(
                "Choose a page:",
                [
                    "Dashboard",
                    "Record Performance", 
                    "Performance History",
                    "Team Management",
                    "Leaderboards",
                    "Personal Progress",
                    "Profile Settings"
                ]
            )
            
            if st.button("Logout"):
                session_manager.logout()
                st.rerun()
        else:
            # Navigation for non-logged-in users
            page = st.selectbox(
                "Choose a page:",
                ["Login", "Register"]
            )
    
    # Route to appropriate page
    if not session_manager.is_logged_in():
        if page == "Register":
            show_register_page()
        else:
            show_login_page()
    else:
        if page == "Dashboard":
            show_dashboard()
        elif page == "Record Performance":
            show_record_performance()
        elif page == "Performance History":
            show_performance_history()
        elif page == "Team Management":
            show_team_management()
        elif page == "Leaderboards":
            show_leaderboards()
        elif page == "Personal Progress":
            show_personal_progress()
        elif page == "Profile Settings":
            show_profile_settings()

def show_login_page():
    """Display login page"""
    st.header("Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username and password:
                if session_manager.login(username, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Please enter both username and password")

def show_register_page():
    """Display registration page"""
    st.header("Register New User")
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username*")
            password = st.text_input("Password*", type="password")
            full_name = st.text_input("Full Name*")
            email = st.text_input("Email*")
        
        with col2:
            gender = st.selectbox("Gender", ["", "Male", "Female", "Other"])
            age_group = st.selectbox("Age Group", ["", "18-25", "26-35", "36-45", "46-55", "56+"])
            location = st.text_input("Location")
        
        submit_button = st.form_submit_button("Register")
        
        if submit_button:
            if username and password and full_name and email:
                user_id = session_manager.register_user(
                    username, password, full_name, email,
                    gender if gender else None,
                    age_group if age_group else None,
                    location if location else None
                )
                if user_id:
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Registration failed. Username or email might already exist.")
            else:
                st.error("Please fill in all required fields (*)")

def show_dashboard():
    """Display main dashboard"""
    st.header("Personal Dashboard")
    
    user_data = session_manager.get_user_data()
    db = DatabaseManager()
    
    # Get user performances
    performances = db.get_user_performances(session_manager.get_current_user_id())
    
    if performances:
        # Calculate total points
        total_points = sum([p[4] for p in performances])  # points_calculated is at index 4
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Points", f"{total_points:.1f}")
        
        with col2:
            st.metric("Total Activities", len(performances))
        
        with col3:
            if user_data[7]:  # team_name
                st.metric("Team", user_data[7])
            else:
                st.metric("Team", "No team")
        
        # Recent activities
        st.subheader("Recent Activities")
        recent_performances = performances[:5]  # Show last 5
        
        for perf in recent_performances:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.write(f"**{perf[7]}**")  # sport_name
                with col2:
                    st.write(f"{perf[3]} {perf[8]}")  # value and unit
                with col3:
                    st.write(f"{perf[4]:.1f} pts")  # points
                with col4:
                    st.write(perf[5])  # date_recorded
    else:
        st.info("No activities recorded yet. Start by recording your first performance!")
        if st.button("Record Performance"):
            st.session_state.page = "Record Performance"
            st.rerun()

def show_record_performance():
    """Display performance recording page"""
    st.header("Record Performance")
    
    db = DatabaseManager()
    sports = db.get_all_sports()
    
    with st.form("performance_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            sport_options = {f"{sport[1]} ({sport[2]})": sport[0] for sport in sports}
            selected_sport = st.selectbox("Select Sport", list(sport_options.keys()))
            sport_id = sport_options[selected_sport]
            
            # Get sport details for point calculation
            selected_sport_data = next(sport for sport in sports if sport[0] == sport_id)
            
            value = st.number_input(f"Performance ({selected_sport_data[2]})", min_value=0.0, step=0.1)
            
        with col2:
            date_recorded = st.date_input("Date")
            notes = st.text_area("Notes (optional)")
            
            # Show calculated points
            if value > 0:
                calculated_points = value * selected_sport_data[3]
                st.info(f"Points to be awarded: {calculated_points:.1f}")
        
        submit_button = st.form_submit_button("Record Performance")
        
        if submit_button:
            if value > 0:
                performance_id = db.add_performance(
                    session_manager.get_current_user_id(),
                    sport_id,
                    value,
                    date_recorded,
                    notes if notes else None
                )
                if performance_id:
                    st.success("Performance recorded successfully!")
                else:
                    st.error("Failed to record performance")
            else:
                st.error("Please enter a valid performance value")

def show_performance_history():
    """Display performance history page"""
    st.header("Performance History")
    
    db = DatabaseManager()
    performances = db.get_user_performances(session_manager.get_current_user_id())
    
    if performances:
        # Create a table of performances
        import pandas as pd
        
        df_data = []
        for perf in performances:
            df_data.append({
                "Date": perf[5],
                "Sport": perf[7],
                "Performance": f"{perf[3]} {perf[8]}",
                "Points": f"{perf[4]:.1f}",
                "Notes": perf[6] if perf[6] else ""
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
        
        # Summary statistics
        st.subheader("Summary")
        total_points = sum([p[4] for p in performances])
        st.metric("Total Points", f"{total_points:.1f}")
        
    else:
        st.info("No performances recorded yet.")

def show_team_management():
    """Display team management page"""
    st.header("Team Management")
    
    db = DatabaseManager()
    user_data = session_manager.get_user_data()
    
    # Current team status
    if user_data[6]:  # team_id
        st.success(f"You are currently a member of: **{user_data[7]}**")
        if st.button("Leave Team"):
            db.join_team(session_manager.get_current_user_id(), None)
            session_manager.refresh_user_data()
            st.rerun()
    else:
        st.info("You are not currently a member of any team.")
    
    # Create new team
    st.subheader("Create New Team")
    with st.form("create_team_form"):
        team_name = st.text_input("Team Name")
        description = st.text_area("Team Description")
        
        if st.form_submit_button("Create Team"):
            if team_name:
                try:
                    team_id = db.create_team(team_name, description, session_manager.get_current_user_id())
                    db.join_team(session_manager.get_current_user_id(), team_id)
                    session_manager.refresh_user_data()
                    st.success("Team created successfully!")
                    st.rerun()
                except:
                    st.error("Team name already exists")
            else:
                st.error("Please enter a team name")
    
    # Join existing team
    st.subheader("Join Existing Team")
    teams = db.get_all_teams()
    
    if teams:
        team_options = {f"{team[1]} ({team[5]} members)": team[0] for team in teams}
        selected_team = st.selectbox("Select Team to Join", [""] + list(team_options.keys()))
        
        if selected_team and st.button("Join Team"):
            team_id = team_options[selected_team]
            db.join_team(session_manager.get_current_user_id(), team_id)
            session_manager.refresh_user_data()
            st.success("Joined team successfully!")
            st.rerun()

def show_leaderboards():
    """Display leaderboards page"""
    db_path = os.path.join(os.path.dirname(__file__), 'fitness_challenge.db')
    leaderboard_manager = LeaderboardManager(db_path)
    
    # Create tabs for different leaderboard views
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏆 Overall", "👥 Teams", "🏃‍♂️ Sports", "👨‍👩‍👧‍👦 Demographics"
    ])
    
    with tab1:
        leaderboard_manager.render_overall_leaderboard()
    
    with tab2:
        leaderboard_manager.render_team_leaderboard()
    
    with tab3:
        leaderboard_manager.render_sport_leaderboards()
    
    with tab4:
        leaderboard_manager.render_demographic_leaderboards()

def show_personal_progress():
    """Display personal progress page"""
    db_path = os.path.join(os.path.dirname(__file__), 'fitness_challenge.db')
    progress_tracker = PersonalProgressTracker(db_path)
    
    user_id = session_manager.get_current_user_id()
    
    # Create tabs for different progress views
    tab1, tab2 = st.tabs(["📈 My Progress", "⚖️ Compare with Others"])
    
    with tab1:
        progress_tracker.render_personal_dashboard(user_id)
    
    with tab2:
        progress_tracker.render_comparison_view(user_id)

def show_profile_settings():
    """Display profile settings page"""
    st.header("Profile Settings")
    
    user_data = session_manager.get_user_data()
    db = DatabaseManager()
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name", value=user_data[3])
            email = st.text_input("Email", value=user_data[4])
            gender = st.selectbox("Gender", ["", "Male", "Female", "Other"], 
                                index=["", "Male", "Female", "Other"].index(user_data[5] or ""))
        
        with col2:
            age_group = st.selectbox("Age Group", ["", "18-25", "26-35", "36-45", "46-55", "56+"],
                                   index=["", "18-25", "26-35", "36-45", "46-55", "56+"].index(user_data[6] or ""))
            location = st.text_input("Location", value=user_data[7] or "")
        
        if st.form_submit_button("Update Profile"):
            # Note: This would require additional database methods to update user info
            st.success("Profile update functionality will be implemented in the next phase.")

if __name__ == "__main__":
    main()

