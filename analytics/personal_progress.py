"""
Personal Progress Tracking Module
Provides detailed personal analytics and progress tracking
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .data_processing import AnalyticsDataProcessor
from .visualization import AnalyticsVisualizer

class PersonalProgressTracker:
    """Manages personal progress tracking and analytics"""
    
    def __init__(self, db_path: str):
        self.data_processor = AnalyticsDataProcessor(db_path)
        self.visualizer = AnalyticsVisualizer()
    
    def render_personal_dashboard(self, user_id: int):
        """Render comprehensive personal progress dashboard"""
        st.header("📈 Personal Progress Dashboard")
        
        # Get user progress data
        progress_data = self.data_processor.get_user_progress_data(user_id)
        user_ranking = self.data_processor.get_user_ranking(user_id)
        
        if progress_data['user_stats'].empty:
            st.info("No activity data found. Start recording your fitness activities to see your progress!")
            return
        
        user_stats = progress_data['user_stats'].iloc[0]
        
        # Display overview metrics
        self._render_overview_metrics(user_stats, user_ranking)
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Progress Charts", "🏃‍♂️ Sport Analysis", "📅 Activity Calendar", 
            "🎯 Goals & Achievements", "📋 Recent Activities"
        ])
        
        with tab1:
            self._render_progress_charts(progress_data)
        
        with tab2:
            self._render_sport_analysis(progress_data)
        
        with tab3:
            self._render_activity_calendar(progress_data)
        
        with tab4:
            self._render_goals_achievements(user_stats, progress_data)
        
        with tab5:
            self._render_recent_activities(progress_data['recent_activities'])
    
    def _render_overview_metrics(self, user_stats: pd.Series, user_ranking: Dict):
        """Render overview metrics cards"""
        st.subheader("🏆 Your Performance Overview")
        
        # Main metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Points",
                f"{user_stats['total_points']:,.1f}",
                delta=None,
                help="Total points earned across all activities"
            )
        
        with col2:
            st.metric(
                "Total Activities",
                f"{user_stats['total_activities']:,}",
                delta=None,
                help="Number of activities recorded"
            )
        
        with col3:
            st.metric(
                "Average Points",
                f"{user_stats['avg_points_per_activity']:.1f}",
                delta=None,
                help="Average points per activity"
            )
        
        with col4:
            st.metric(
                "Current Rank",
                f"#{user_ranking['rank']}",
                delta=f"{user_ranking['percentile']}th percentile",
                help=f"Your rank among {user_ranking['total_users']} participants"
            )
        
        # Additional info row
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if user_stats['team_name']:
                st.info(f"🏢 Team: **{user_stats['team_name']}**")
            else:
                st.info("🏢 No team assigned")
        
        with col2:
            if pd.notna(user_stats['first_activity_date']):
                days_active = (pd.to_datetime(user_stats['last_activity_date']) - 
                             pd.to_datetime(user_stats['first_activity_date'])).days + 1
                st.info(f"📅 Active for **{days_active}** days")
            else:
                st.info("📅 Just started!")
        
        with col3:
            if pd.notna(user_stats['last_activity_date']):
                last_activity = pd.to_datetime(user_stats['last_activity_date'])
                days_since = (datetime.now() - last_activity).days
                if days_since == 0:
                    st.success("🔥 Active today!")
                elif days_since == 1:
                    st.warning("⏰ Last active yesterday")
                else:
                    st.error(f"⚠️ Last active {days_since} days ago")
        
        # Ranking gauge
        if user_ranking['total_users'] > 1:
            st.subheader("🎯 Your Ranking")
            ranking_chart = self.visualizer.create_ranking_gauge(user_ranking)
            st.plotly_chart(ranking_chart, use_container_width=True, config=self.visualizer.chart_config)
    
    def _render_progress_charts(self, progress_data: Dict):
        """Render progress tracking charts"""
        st.subheader("📈 Progress Over Time")
        
        daily_progress = progress_data['daily_progress']
        
        if daily_progress.empty:
            st.info("No daily progress data available.")
            return
        
        # Time range selector
        col1, col2 = st.columns(2)
        with col1:
            time_range = st.selectbox(
                "Select Time Range",
                ["Last 7 days", "Last 30 days", "Last 90 days", "All time"],
                index=1,
                key="progress_time_range"
            )
        
        with col2:
            chart_type = st.selectbox(
                "Chart Type",
                ["Combined", "Points Only", "Activities Only"],
                key="progress_chart_type"
            )
        
        # Filter data based on time range
        if time_range != "All time":
            days = {"Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90}[time_range]
            cutoff_date = datetime.now() - timedelta(days=days)
            daily_progress = daily_progress[daily_progress['activity_date'] >= cutoff_date]
        
        if daily_progress.empty:
            st.info(f"No data available for {time_range.lower()}.")
            return
        
        # Create and display chart
        if chart_type == "Combined":
            chart = self.visualizer.create_progress_timeline(daily_progress, "Daily Progress Timeline")
        elif chart_type == "Points Only":
            import plotly.graph_objects as go
            chart = go.Figure()
            chart.add_trace(go.Scatter(
                x=daily_progress['activity_date'],
                y=daily_progress['daily_points'],
                mode='lines+markers',
                name='Daily Points',
                line=dict(color='blue', width=2),
                marker=dict(size=6)
            ))
            chart.update_layout(title="Daily Points", height=400)
        else:  # Activities Only
            import plotly.graph_objects as go
            chart = go.Figure()
            chart.add_trace(go.Bar(
                x=daily_progress['activity_date'],
                y=daily_progress['daily_activities'],
                name='Daily Activities',
                marker_color='orange'
            ))
            chart.update_layout(title="Daily Activities", height=400)
        
        st.plotly_chart(chart, use_container_width=True, config=self.visualizer.chart_config)
        
        # Weekly progress
        st.subheader("📊 Weekly Progress")
        weekly_data = self.data_processor.get_weekly_progress(
            progress_data['user_stats'].iloc[0].name if not progress_data['user_stats'].empty else 1,
            weeks=12
        )
        
        if not weekly_data.empty:
            weekly_chart = self.visualizer.create_weekly_progress_chart(weekly_data)
            st.plotly_chart(weekly_chart, use_container_width=True, config=self.visualizer.chart_config)
        else:
            st.info("No weekly progress data available.")
    
    def _render_sport_analysis(self, progress_data: Dict):
        """Render sport-specific analysis"""
        st.subheader("🏃‍♂️ Sport Performance Analysis")
        
        sport_breakdown = progress_data['sport_breakdown']
        
        if sport_breakdown.empty:
            st.info("No sport data available.")
            return
        
        # Sport breakdown pie chart
        col1, col2 = st.columns(2)
        
        with col1:
            pie_chart = self.visualizer.create_sport_breakdown_pie(sport_breakdown)
            st.plotly_chart(pie_chart, use_container_width=True, config=self.visualizer.chart_config)
        
        with col2:
            # Sport performance table
            st.subheader("Sport Performance Details")
            
            display_columns = [
                'sport_name', 'activity_count', 'total_points', 
                'total_performance', 'avg_performance', 'best_performance', 'unit'
            ]
            
            column_config = {
                'sport_name': st.column_config.TextColumn('Sport', width="medium"),
                'activity_count': st.column_config.NumberColumn('Activities', width="small"),
                'total_points': st.column_config.NumberColumn('Total Points', format="%.1f"),
                'total_performance': st.column_config.NumberColumn('Total', format="%.2f"),
                'avg_performance': st.column_config.NumberColumn('Average', format="%.2f"),
                'best_performance': st.column_config.NumberColumn('Best', format="%.2f"),
                'unit': st.column_config.TextColumn('Unit', width="small")
            }
            
            st.dataframe(
                sport_breakdown[display_columns],
                column_config=column_config,
                hide_index=True,
                use_container_width=True
            )
        
        # Sport-specific trends
        st.subheader("📈 Sport Performance Trends")
        
        selected_sport = st.selectbox(
            "Select sport to analyze",
            sport_breakdown['sport_name'].tolist(),
            key="sport_trend_select"
        )
        
        if selected_sport:
            self._render_sport_trend_analysis(selected_sport, progress_data)
    
    def _render_sport_trend_analysis(self, sport_name: str, progress_data: Dict):
        """Render trend analysis for a specific sport"""
        # This would require additional database queries for sport-specific daily data
        # For now, show a placeholder
        st.info(f"Detailed trend analysis for {sport_name} will be implemented in the next update.")
        
        # Show sport statistics
        sport_data = progress_data['sport_breakdown']
        sport_info = sport_data[sport_data['sport_name'] == sport_name].iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Activities", sport_info['activity_count'])
        
        with col2:
            st.metric("Total Points", f"{sport_info['total_points']:.1f}")
        
        with col3:
            st.metric(f"Average ({sport_info['unit']})", f"{sport_info['avg_performance']:.2f}")
        
        with col4:
            st.metric(f"Personal Best ({sport_info['unit']})", f"{sport_info['best_performance']:.2f}")
    
    def _render_activity_calendar(self, progress_data: Dict):
        """Render activity calendar/heatmap"""
        st.subheader("📅 Activity Calendar")
        
        daily_progress = progress_data['daily_progress']
        
        if daily_progress.empty:
            st.info("No activity calendar data available.")
            return
        
        # Create activity heatmap
        heatmap_chart = self.visualizer.create_activity_heatmap(daily_progress)
        st.plotly_chart(heatmap_chart, use_container_width=True, config=self.visualizer.chart_config)
        
        # Activity streak information
        st.subheader("🔥 Activity Streaks")
        
        # Calculate current streak
        daily_progress_sorted = daily_progress.sort_values('activity_date', ascending=False)
        current_streak = 0
        
        for i, row in daily_progress_sorted.iterrows():
            if row['daily_activities'] > 0:
                current_streak += 1
            else:
                break
        
        # Calculate longest streak (simplified)
        longest_streak = daily_progress[daily_progress['daily_activities'] > 0].shape[0]  # Simplified calculation
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Streak", f"{current_streak} days")
        
        with col2:
            st.metric("Longest Streak", f"{longest_streak} days")
        
        with col3:
            active_days = daily_progress[daily_progress['daily_activities'] > 0].shape[0]
            total_days = daily_progress.shape[0]
            consistency = (active_days / total_days * 100) if total_days > 0 else 0
            st.metric("Consistency", f"{consistency:.1f}%")
    
    def _render_goals_achievements(self, user_stats: pd.Series, progress_data: Dict):
        """Render goals and achievements section"""
        st.subheader("🎯 Goals & Achievements")
        
        # Achievement badges
        st.subheader("🏅 Achievements Unlocked")
        
        achievements = []
        total_points = user_stats['total_points']
        total_activities = user_stats['total_activities']
        
        # Point-based achievements
        if total_points >= 1000:
            achievements.append(("🥇", "Point Master", "Earned 1000+ points"))
        elif total_points >= 500:
            achievements.append(("🥈", "Point Collector", "Earned 500+ points"))
        elif total_points >= 100:
            achievements.append(("🥉", "Getting Started", "Earned 100+ points"))
        
        # Activity-based achievements
        if total_activities >= 50:
            achievements.append(("🏃‍♂️", "Activity Champion", "Completed 50+ activities"))
        elif total_activities >= 20:
            achievements.append(("🚀", "Active Member", "Completed 20+ activities"))
        elif total_activities >= 5:
            achievements.append(("⭐", "First Steps", "Completed 5+ activities"))
        
        # Sport diversity achievements
        sport_count = len(progress_data['sport_breakdown'])
        if sport_count >= 5:
            achievements.append(("🌟", "Multi-Sport Athlete", f"Active in {sport_count} sports"))
        elif sport_count >= 3:
            achievements.append(("🎯", "Diverse Athlete", f"Active in {sport_count} sports"))
        
        if achievements:
            cols = st.columns(min(len(achievements), 4))
            for i, (emoji, title, description) in enumerate(achievements):
                with cols[i % 4]:
                    st.success(f"{emoji} **{title}**\n\n{description}")
        else:
            st.info("Complete your first activity to start earning achievements!")
        
        # Goal setting section
        st.subheader("🎯 Set Your Goals")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input(
                "Weekly Points Goal",
                value="100",
                help="Set your weekly points target",
                key="weekly_points_goal"
            )
        
        with col2:
            st.text_input(
                "Weekly Activities Goal",
                value="5",
                help="Set your weekly activities target",
                key="weekly_activities_goal"
            )
        
        if st.button("Save Goals", key="save_goals"):
            st.success("Goals saved! (Feature will be fully implemented in next update)")
    
    def _render_recent_activities(self, recent_activities: pd.DataFrame):
        """Render recent activities list"""
        st.subheader("📋 Recent Activities")
        
        if recent_activities.empty:
            st.info("No recent activities found.")
            return
        
        # Display recent activities
        for _, activity in recent_activities.iterrows():
            with st.expander(
                f"{activity['sport_name']} - {activity['value']} {activity['unit']} "
                f"({activity['points']:.1f} pts) - {activity['date'].strftime('%Y-%m-%d')}"
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Sport:** {activity['sport_name']}")
                    st.write(f"**Performance:** {activity['value']} {activity['unit']}")
                    st.write(f"**Points Earned:** {activity['points']:.1f}")
                
                with col2:
                    st.write(f"**Date:** {activity['date'].strftime('%Y-%m-%d %H:%M')}")
                    if pd.notna(activity['notes']) and activity['notes'].strip():
                        st.write(f"**Notes:** {activity['notes']}")
                    else:
                        st.write("**Notes:** No notes added")
    
    def render_comparison_view(self, user_id: int):
        """Render comparison with other users"""
        st.header("⚖️ Performance Comparison")
        
        # Get user's data
        user_ranking = self.data_processor.get_user_ranking(user_id)
        leaderboard_data = self.data_processor.get_leaderboard_data(50)
        
        if leaderboard_data.empty:
            st.info("No comparison data available.")
            return
        
        # Find user in leaderboard
        user_data = leaderboard_data[leaderboard_data.index == user_id]
        
        if user_data.empty:
            st.info("User data not found in leaderboard.")
            return
        
        user_row = user_data.iloc[0]
        
        # Show comparison with nearby users
        st.subheader("🎯 Compare with Nearby Ranks")
        
        user_rank = user_row['rank']
        start_rank = max(1, user_rank - 2)
        end_rank = min(len(leaderboard_data), user_rank + 2)
        
        nearby_users = leaderboard_data[
            (leaderboard_data['rank'] >= start_rank) & 
            (leaderboard_data['rank'] <= end_rank)
        ]
        
        # Highlight current user
        def highlight_user(row):
            if row.name == user_id:
                return ['background-color: lightblue'] * len(row)
            return [''] * len(row)
        
        display_columns = ['rank', 'full_name', 'total_points', 'total_activities', 'avg_points_per_activity']
        
        st.dataframe(
            nearby_users[display_columns].style.apply(highlight_user, axis=1),
            hide_index=True,
            use_container_width=True
        )
        
        # Performance gaps
        st.subheader("📊 Performance Gaps")
        
        if user_rank > 1:
            user_above = leaderboard_data[leaderboard_data['rank'] == user_rank - 1].iloc[0]
            points_gap = user_above['total_points'] - user_row['total_points']
            st.info(f"You need **{points_gap:.1f} more points** to reach rank #{user_rank - 1}")
        
        if user_rank < len(leaderboard_data):
            user_below = leaderboard_data[leaderboard_data['rank'] == user_rank + 1].iloc[0]
            points_lead = user_row['total_points'] - user_below['total_points']
            st.success(f"You are **{points_lead:.1f} points** ahead of rank #{user_rank + 1}")

