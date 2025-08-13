"""
Leaderboards Module
Implements various leaderboard views and ranking systems
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
from .data_processing import AnalyticsDataProcessor
from .visualization import AnalyticsVisualizer

class LeaderboardManager:
    """Manages all leaderboard functionality"""
    
    def __init__(self, db_path: str):
        self.data_processor = AnalyticsDataProcessor(db_path)
        self.visualizer = AnalyticsVisualizer()
    
    def render_overall_leaderboard(self, limit: int = 50):
        """Render the main overall leaderboard"""
        st.header("🏆 Overall Leaderboard")
        
        # Get leaderboard data
        leaderboard_data = self.data_processor.get_leaderboard_data(limit)
        
        if leaderboard_data.empty:
            st.info("No performance data available yet. Be the first to record an activity!")
            return
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 Chart View", "📋 Table View", "📈 Statistics"])
        
        with tab1:
            # Show top performers chart
            top_n = st.slider("Show top N users", 5, min(20, len(leaderboard_data)), 10, key="overall_top_n")
            chart = self.visualizer.create_leaderboard_chart(leaderboard_data, top_n)
            st.plotly_chart(chart, use_container_width=True, config=self.visualizer.chart_config)
        
        with tab2:
            # Show detailed table
            st.subheader("Detailed Rankings")
            
            # Add filters
            col1, col2, col3 = st.columns(3)
            with col1:
                gender_filter = st.selectbox(
                    "Filter by Gender",
                    ["All"] + list(leaderboard_data['gender'].dropna().unique()),
                    key="gender_filter"
                )
            with col2:
                age_filter = st.selectbox(
                    "Filter by Age Group",
                    ["All"] + list(leaderboard_data['age_group'].dropna().unique()),
                    key="age_filter"
                )
            with col3:
                team_filter = st.selectbox(
                    "Filter by Team",
                    ["All"] + list(leaderboard_data['team_name'].dropna().unique()),
                    key="team_filter"
                )
            
            # Apply filters
            filtered_data = leaderboard_data.copy()
            if gender_filter != "All":
                filtered_data = filtered_data[filtered_data['gender'] == gender_filter]
            if age_filter != "All":
                filtered_data = filtered_data[filtered_data['age_group'] == age_filter]
            if team_filter != "All":
                filtered_data = filtered_data[filtered_data['team_name'] == team_filter]
            
            # Recalculate rankings for filtered data
            if not filtered_data.empty:
                filtered_data = filtered_data.reset_index(drop=True)
                filtered_data['filtered_rank'] = range(1, len(filtered_data) + 1)
            
            # Display table
            if not filtered_data.empty:
                display_columns = [
                    'filtered_rank', 'full_name', 'total_points', 'total_activities',
                    'avg_points_per_activity', 'team_name', 'gender', 'age_group', 'location'
                ]
                
                column_config = {
                    'filtered_rank': st.column_config.NumberColumn('Rank', width="small"),
                    'full_name': st.column_config.TextColumn('Name', width="medium"),
                    'total_points': st.column_config.NumberColumn('Total Points', format="%.1f"),
                    'total_activities': st.column_config.NumberColumn('Activities', width="small"),
                    'avg_points_per_activity': st.column_config.NumberColumn('Avg Points', format="%.1f"),
                    'team_name': st.column_config.TextColumn('Team'),
                    'gender': st.column_config.TextColumn('Gender', width="small"),
                    'age_group': st.column_config.TextColumn('Age Group', width="small"),
                    'location': st.column_config.TextColumn('Location')
                }
                
                st.dataframe(
                    filtered_data[display_columns],
                    column_config=column_config,
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No users match the selected filters.")
        
        with tab3:
            # Show statistics
            self._render_leaderboard_statistics(leaderboard_data)
    
    def render_team_leaderboard(self, limit: int = 20):
        """Render team leaderboard"""
        st.header("👥 Team Leaderboard")
        
        team_data = self.data_processor.get_team_leaderboard(limit)
        
        if team_data.empty:
            st.info("No team data available yet.")
            return
        
        # Create tabs
        tab1, tab2 = st.tabs(["📊 Chart View", "📋 Table View"])
        
        with tab1:
            top_n = st.slider("Show top N teams", 5, min(15, len(team_data)), 10, key="team_top_n")
            chart = self.visualizer.create_team_comparison_chart(team_data, top_n)
            st.plotly_chart(chart, use_container_width=True, config=self.visualizer.chart_config)
        
        with tab2:
            st.subheader("Team Rankings")
            
            display_columns = [
                'team_rank', 'team_name', 'total_team_points', 'member_count',
                'avg_points_per_member', 'total_team_activities'
            ]
            
            column_config = {
                'team_rank': st.column_config.NumberColumn('Rank', width="small"),
                'team_name': st.column_config.TextColumn('Team Name', width="medium"),
                'total_team_points': st.column_config.NumberColumn('Total Points', format="%.1f"),
                'member_count': st.column_config.NumberColumn('Members', width="small"),
                'avg_points_per_member': st.column_config.NumberColumn('Avg per Member', format="%.1f"),
                'total_team_activities': st.column_config.NumberColumn('Total Activities')
            }
            
            st.dataframe(
                team_data[display_columns],
                column_config=column_config,
                hide_index=True,
                use_container_width=True
            )
    
    def render_sport_leaderboards(self):
        """Render sport-specific leaderboards"""
        st.header("🏃‍♂️ Sport Leaderboards")
        
        # Get available sports
        sports = self.data_processor.get_available_sports()
        
        if not sports:
            st.info("No sports data available.")
            return
        
        # Sport selection
        selected_sport = st.selectbox("Select Sport", sports, key="sport_leaderboard_select")
        
        if selected_sport:
            sport_data = self.data_processor.get_sport_leaderboard(selected_sport, 30)
            
            if sport_data.empty:
                st.info(f"No performance data available for {selected_sport}.")
                return
            
            # Create tabs
            tab1, tab2 = st.tabs(["📊 Chart View", "📋 Table View"])
            
            with tab1:
                top_n = st.slider("Show top N performers", 5, min(15, len(sport_data)), 10, key="sport_top_n")
                
                # Create sport-specific chart
                top_performers = sport_data.head(top_n)
                
                import plotly.graph_objects as go
                fig = go.Figure(data=[
                    go.Bar(
                        y=top_performers['full_name'][::-1],
                        x=top_performers['total_points'][::-1],
                        orientation='h',
                        marker_color='lightblue',
                        text=top_performers['total_performance'][::-1].round(2),
                        textposition='auto',
                        hovertemplate='<b>%{y}</b><br>' +
                                     f'Points: %{{x}}<br>' +
                                     f'Performance: %{{text}} {sport_data.iloc[0]["unit"]}<br>' +
                                     '<extra></extra>'
                    )
                ])
                
                fig.update_layout(
                    title=f"Top {top_n} {selected_sport} Performers",
                    xaxis_title="Total Points",
                    yaxis_title="Athletes",
                    height=max(400, top_n * 40),
                    margin=dict(l=150)
                )
                
                st.plotly_chart(fig, use_container_width=True, config=self.visualizer.chart_config)
            
            with tab2:
                st.subheader(f"{selected_sport} Rankings")
                
                display_columns = [
                    'sport_rank', 'full_name', 'total_points', 'total_performance',
                    'activity_count', 'avg_performance', 'best_performance'
                ]
                
                unit = sport_data.iloc[0]['unit'] if not sport_data.empty else ""
                
                column_config = {
                    'sport_rank': st.column_config.NumberColumn('Rank', width="small"),
                    'full_name': st.column_config.TextColumn('Name', width="medium"),
                    'total_points': st.column_config.NumberColumn('Total Points', format="%.1f"),
                    'total_performance': st.column_config.NumberColumn(f'Total ({unit})', format="%.2f"),
                    'activity_count': st.column_config.NumberColumn('Activities', width="small"),
                    'avg_performance': st.column_config.NumberColumn(f'Avg ({unit})', format="%.2f"),
                    'best_performance': st.column_config.NumberColumn(f'Best ({unit})', format="%.2f")
                }
                
                st.dataframe(
                    sport_data[display_columns],
                    column_config=column_config,
                    hide_index=True,
                    use_container_width=True
                )
    
    def render_demographic_leaderboards(self):
        """Render demographic-based leaderboards"""
        st.header("👨‍👩‍👧‍👦 Demographic Leaderboards")
        
        leaderboard_data = self.data_processor.get_leaderboard_data(100)
        
        if leaderboard_data.empty:
            st.info("No demographic data available.")
            return
        
        # Create tabs for different demographics
        tab1, tab2, tab3 = st.tabs(["👫 Gender", "🎂 Age Group", "📍 Location"])
        
        with tab1:
            self._render_gender_leaderboard(leaderboard_data)
        
        with tab2:
            self._render_age_group_leaderboard(leaderboard_data)
        
        with tab3:
            self._render_location_leaderboard(leaderboard_data)
    
    def _render_gender_leaderboard(self, data: pd.DataFrame):
        """Render gender-based leaderboard"""
        st.subheader("Gender Performance Comparison")
        
        gender_data = data.groupby('gender').agg({
            'total_points': ['sum', 'mean', 'count'],
            'total_activities': 'sum'
        }).round(2)
        
        gender_data.columns = ['Total Points', 'Avg Points', 'Participants', 'Total Activities']
        gender_data = gender_data.reset_index()
        
        if not gender_data.empty:
            # Create comparison chart
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Total Points by Gender', 'Average Points by Gender'),
                specs=[[{"type": "bar"}, {"type": "bar"}]]
            )
            
            fig.add_trace(
                go.Bar(x=gender_data['gender'], y=gender_data['Total Points'], name='Total Points'),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Bar(x=gender_data['gender'], y=gender_data['Avg Points'], name='Avg Points'),
                row=1, col=2
            )
            
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True, config=self.visualizer.chart_config)
            
            # Show table
            st.dataframe(gender_data, hide_index=True, use_container_width=True)
    
    def _render_age_group_leaderboard(self, data: pd.DataFrame):
        """Render age group leaderboard"""
        st.subheader("Age Group Performance Comparison")
        
        age_data = data.groupby('age_group').agg({
            'total_points': ['sum', 'mean', 'count'],
            'total_activities': 'sum'
        }).round(2)
        
        age_data.columns = ['Total Points', 'Avg Points', 'Participants', 'Total Activities']
        age_data = age_data.reset_index()
        
        if not age_data.empty:
            # Create chart
            import plotly.express as px
            fig = px.bar(age_data, x='age_group', y='Avg Points', 
                        title='Average Points by Age Group',
                        color='Participants', color_continuous_scale='viridis')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True, config=self.visualizer.chart_config)
            
            # Show table
            st.dataframe(age_data, hide_index=True, use_container_width=True)
    
    def _render_location_leaderboard(self, data: pd.DataFrame):
        """Render location-based leaderboard"""
        st.subheader("Location Performance Comparison")
        
        location_data = data.groupby('location').agg({
            'total_points': ['sum', 'mean', 'count'],
            'total_activities': 'sum'
        }).round(2)
        
        location_data.columns = ['Total Points', 'Avg Points', 'Participants', 'Total Activities']
        location_data = location_data.reset_index().sort_values('Total Points', ascending=False)
        
        if not location_data.empty:
            # Show top locations
            top_locations = location_data.head(10)
            
            import plotly.graph_objects as go
            fig = go.Figure(data=[
                go.Bar(
                    x=top_locations['location'],
                    y=top_locations['Total Points'],
                    marker_color='lightcoral',
                    text=top_locations['Participants'],
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>Total Points: %{y}<br>Participants: %{text}<extra></extra>'
                )
            ])
            
            fig.update_layout(
                title="Top Locations by Total Points",
                xaxis_title="Location",
                yaxis_title="Total Points",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True, config=self.visualizer.chart_config)
            
            # Show table
            st.dataframe(location_data, hide_index=True, use_container_width=True)
    
    def _render_leaderboard_statistics(self, data: pd.DataFrame):
        """Render overall leaderboard statistics"""
        if data.empty:
            return
        
        st.subheader("📊 Leaderboard Statistics")
        
        # Calculate statistics
        total_users = len(data)
        total_points = data['total_points'].sum()
        avg_points = data['total_points'].mean()
        total_activities = data['total_activities'].sum()
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Participants", total_users)
        
        with col2:
            st.metric("Total Points", f"{total_points:,.1f}")
        
        with col3:
            st.metric("Average Points", f"{avg_points:.1f}")
        
        with col4:
            st.metric("Total Activities", f"{total_activities:,}")
        
        # Show distribution charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Points distribution
            import plotly.express as px
            fig = px.histogram(data, x='total_points', nbins=20, 
                             title='Points Distribution')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True, config=self.visualizer.chart_config)
        
        with col2:
            # Activities distribution
            fig = px.histogram(data, x='total_activities', nbins=20, 
                             title='Activities Distribution')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True, config=self.visualizer.chart_config)

