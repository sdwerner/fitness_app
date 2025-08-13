"""
Analytics Data Processing Module
Handles data aggregation and processing for analytics features
"""

import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import streamlit as st

class AnalyticsDataProcessor:
    """Handles data processing for analytics features"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    @st.cache_data(ttl=60)  # Cache for 1 minute for real-time updates
    def get_leaderboard_data(_self, limit: int = 50) -> pd.DataFrame:
        """Get leaderboard data with user rankings"""
        query = """
        SELECT 
            u.user_id,
            u.username,
            u.full_name,
            u.gender,
            u.age_group,
            u.location,
            t.team_name,
            COALESCE(SUM(p.points_calculated), 0) as total_points,
            COUNT(p.performance_id) as total_activities,
            MAX(p.date_recorded) as last_activity_date,
            AVG(p.points_calculated) as avg_points_per_activity
        FROM users u
        LEFT JOIN performances p ON u.user_id = p.user_id
        LEFT JOIN teams t ON u.team_id = t.team_id
        GROUP BY u.user_id, u.username, u.full_name, u.gender, u.age_group, u.location, t.team_name
        ORDER BY total_points DESC, total_activities DESC
        LIMIT ?
        """
        
        with _self.get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=(limit,))
            
            # Add ranking
            df['rank'] = range(1, len(df) + 1)
            df = df.set_index('user_id')
            
            # Format last activity date
            df['last_activity_date'] = pd.to_datetime(df['last_activity_date'], errors='coerce')
            df['days_since_last_activity'] = (datetime.now() - df['last_activity_date']).dt.days
            
            return df
    
    @st.cache_data(ttl=60)
    def get_team_leaderboard(_self, limit: int = 20) -> pd.DataFrame:
        """Get team leaderboard data"""
        query = """
        SELECT 
            t.team_name,
            t.description,
            COUNT(DISTINCT u.user_id) as member_count,
            COALESCE(SUM(p.points_calculated), 0) as total_team_points,
            COALESCE(AVG(p.points_calculated), 0) as avg_points_per_member,
            COUNT(p.performance_id) as total_team_activities,
            MAX(p.date_recorded) as last_team_activity
        FROM teams t
        LEFT JOIN users u ON t.team_id = u.team_id
        LEFT JOIN performances p ON u.user_id = p.user_id
        GROUP BY t.team_id, t.team_name, t.description
        HAVING member_count > 0
        ORDER BY total_team_points DESC, avg_points_per_member DESC
        LIMIT ?
        """
        
        with _self.get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=(limit,))
            df['team_rank'] = range(1, len(df) + 1)
            df['last_team_activity'] = pd.to_datetime(df['last_team_activity'], errors='coerce')
            return df
    
    @st.cache_data(ttl=60)
    def get_sport_leaderboard(_self, sport_name: str, limit: int = 20) -> pd.DataFrame:
        """Get sport-specific leaderboard"""
        query = """
        SELECT 
            u.username,
            u.full_name,
            s.sport_name,
            s.unit,
            SUM(p.value) as total_performance,
            SUM(p.points_calculated) as total_points,
            COUNT(p.performance_id) as activity_count,
            AVG(p.value) as avg_performance,
            MAX(p.value) as best_performance,
            MAX(p.date_recorded) as last_activity
        FROM users u
        JOIN performances p ON u.user_id = p.user_id
        JOIN sports s ON p.sport_id = s.sport_id
        WHERE s.sport_name = ?
        GROUP BY u.user_id, u.username, u.full_name, s.sport_name, s.unit
        ORDER BY total_points DESC, total_performance DESC
        LIMIT ?
        """
        
        with _self.get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=(sport_name, limit))
            df['sport_rank'] = range(1, len(df) + 1)
            df['last_activity'] = pd.to_datetime(df['last_activity'], errors='coerce')
            return df
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_user_progress_data(_self, user_id: int) -> Dict:
        """Get comprehensive progress data for a specific user"""
        
        # Basic user stats
        user_query = """
        SELECT 
            u.username,
            u.full_name,
            u.gender,
            u.age_group,
            u.location,
            t.team_name,
            MIN(p.date_recorded) as first_activity_date,
            MAX(p.date_recorded) as last_activity_date,
            COUNT(p.performance_id) as total_activities,
            SUM(p.points_calculated) as total_points,
            AVG(p.points_calculated) as avg_points_per_activity
        FROM users u
        LEFT JOIN performances p ON u.user_id = p.user_id
        LEFT JOIN teams t ON u.team_id = t.team_id
        WHERE u.user_id = ?
        GROUP BY u.user_id
        """
        
        # Daily progress data
        daily_query = """
        SELECT 
            DATE(p.date_recorded) as activity_date,
            COUNT(p.performance_id) as daily_activities,
            SUM(p.points_calculated) as daily_points,
            SUM(SUM(p.points_calculated)) OVER (ORDER BY DATE(p.date_recorded)) as cumulative_points
        FROM performances p
        WHERE p.user_id = ?
        GROUP BY DATE(p.date_recorded)
        ORDER BY activity_date
        """
        
        # Sport breakdown
        sport_query = """
        SELECT 
            s.sport_name,
            s.unit,
            COUNT(p.performance_id) as activity_count,
            SUM(p.value) as total_performance,
            SUM(p.points_calculated) as total_points,
            AVG(p.value) as avg_performance,
            MAX(p.value) as best_performance
        FROM performances p
        JOIN sports s ON p.sport_id = s.sport_id
        WHERE p.user_id = ?
        GROUP BY s.sport_id, s.sport_name, s.unit
        ORDER BY total_points DESC
        """
        
        # Recent activities
        recent_query = """
        SELECT 
            p.date_recorded as date,
            s.sport_name,
            s.unit,
            p.value,
            p.points_calculated as points,
            p.notes
        FROM performances p
        JOIN sports s ON p.sport_id = s.sport_id
        WHERE p.user_id = ?
        ORDER BY p.date_recorded DESC
        LIMIT 10
        """
        
        with _self.get_connection() as conn:
            user_stats = pd.read_sql_query(user_query, conn, params=(user_id,))
            daily_progress = pd.read_sql_query(daily_query, conn, params=(user_id,))
            sport_breakdown = pd.read_sql_query(sport_query, conn, params=(user_id,))
            recent_activities = pd.read_sql_query(recent_query, conn, params=(user_id,))
            
            # Convert dates
            if not daily_progress.empty:
                daily_progress['activity_date'] = pd.to_datetime(daily_progress['activity_date'])
            
            if not recent_activities.empty:
                recent_activities['date'] = pd.to_datetime(recent_activities['date'])
            
            return {
                'user_stats': user_stats,
                'daily_progress': daily_progress,
                'sport_breakdown': sport_breakdown,
                'recent_activities': recent_activities
            }
    
    @st.cache_data(ttl=60)
    def get_user_ranking(_self, user_id: int) -> Dict:
        """Get user's current ranking and percentile"""
        
        # Get user's total points
        user_points_query = """
        SELECT COALESCE(SUM(points_calculated), 0) as user_points
        FROM performances
        WHERE user_id = ?
        """
        
        # Get all users' points for ranking
        all_points_query = """
        SELECT 
            u.user_id,
            COALESCE(SUM(p.points_calculated), 0) as total_points
        FROM users u
        LEFT JOIN performances p ON u.user_id = p.user_id
        GROUP BY u.user_id
        ORDER BY total_points DESC
        """
        
        with _self.get_connection() as conn:
            user_points_df = pd.read_sql_query(user_points_query, conn, params=(user_id,))
            all_points_df = pd.read_sql_query(all_points_query, conn)
            
            if user_points_df.empty:
                return {'rank': 0, 'total_users': 0, 'percentile': 0, 'user_points': 0}
            
            user_points = user_points_df.iloc[0]['user_points']
            
            # Find user's rank
            all_points_df['rank'] = range(1, len(all_points_df) + 1)
            user_rank_row = all_points_df[all_points_df['user_id'] == user_id]
            
            if user_rank_row.empty:
                return {'rank': 0, 'total_users': len(all_points_df), 'percentile': 0, 'user_points': user_points}
            
            user_rank = user_rank_row.iloc[0]['rank']
            total_users = len(all_points_df)
            percentile = ((total_users - user_rank + 1) / total_users) * 100
            
            return {
                'rank': user_rank,
                'total_users': total_users,
                'percentile': round(percentile, 1),
                'user_points': user_points
            }
    
    @st.cache_data(ttl=300)
    def get_available_sports(_self) -> List[str]:
        """Get list of all available sports"""
        query = "SELECT sport_name FROM sports ORDER BY sport_name"
        
        with _self.get_connection() as conn:
            df = pd.read_sql_query(query, conn)
            return df['sport_name'].tolist()
    
    @st.cache_data(ttl=300)
    def get_weekly_progress(_self, user_id: int, weeks: int = 12) -> pd.DataFrame:
        """Get weekly progress data for the user"""
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=weeks)
        
        query = """
        SELECT 
            strftime('%Y-%W', p.date_recorded) as week,
            COUNT(p.performance_id) as weekly_activities,
            SUM(p.points_calculated) as weekly_points,
            AVG(p.points_calculated) as avg_points_per_activity
        FROM performances p
        WHERE p.user_id = ? AND p.date_recorded >= ?
        GROUP BY strftime('%Y-%W', p.date_recorded)
        ORDER BY week
        """
        
        with _self.get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=(user_id, start_date.strftime('%Y-%m-%d')))
            return df

