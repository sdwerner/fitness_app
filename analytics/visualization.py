"""
Analytics Visualization Module
Creates interactive charts and visualizations for the fitness challenge app
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class AnalyticsVisualizer:
    """Handles all visualization for analytics features"""
    
    def __init__(self):
        # Set consistent color scheme
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd',
            'light': '#17becf'
        }
        
        # Chart configuration
        self.chart_config = {
            'displayModeBar': False,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
        }
    
    def create_progress_timeline(self, daily_progress: pd.DataFrame, title: str = "Daily Progress") -> go.Figure:
        """Create a timeline chart showing daily progress"""
        if daily_progress.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No activity data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="gray")
            )
            fig.update_layout(
                title=title,
                height=400,
                showlegend=False
            )
            return fig
        
        # Create subplot with secondary y-axis
        fig = make_subplots(
            specs=[[{"secondary_y": True}]],
            subplot_titles=[title]
        )
        
        # Add daily points bar chart
        fig.add_trace(
            go.Bar(
                x=daily_progress['activity_date'],
                y=daily_progress['daily_points'],
                name='Daily Points',
                marker_color=self.colors['primary'],
                opacity=0.7
            ),
            secondary_y=False,
        )
        
        # Add cumulative points line
        fig.add_trace(
            go.Scatter(
                x=daily_progress['activity_date'],
                y=daily_progress['cumulative_points'],
                mode='lines+markers',
                name='Cumulative Points',
                line=dict(color=self.colors['success'], width=3),
                marker=dict(size=6)
            ),
            secondary_y=True,
        )
        
        # Update layout
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Daily Points", secondary_y=False)
        fig.update_yaxes(title_text="Cumulative Points", secondary_y=True)
        
        fig.update_layout(
            height=500,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    def create_sport_breakdown_pie(self, sport_breakdown: pd.DataFrame) -> go.Figure:
        """Create pie chart showing sport activity breakdown"""
        if sport_breakdown.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No sport data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="gray")
            )
            fig.update_layout(title="Sport Activity Breakdown", height=400)
            return fig
        
        fig = go.Figure(data=[
            go.Pie(
                labels=sport_breakdown['sport_name'],
                values=sport_breakdown['total_points'],
                hole=0.4,
                textinfo='label+percent',
                textposition='auto',
                marker=dict(
                    colors=px.colors.qualitative.Set3[:len(sport_breakdown)]
                )
            )
        ])
        
        fig.update_layout(
            title="Points by Sport",
            height=500,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.01
            )
        )
        
        return fig
    
    def create_weekly_progress_chart(self, weekly_data: pd.DataFrame) -> go.Figure:
        """Create weekly progress chart"""
        if weekly_data.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No weekly data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="gray")
            )
            fig.update_layout(title="Weekly Progress", height=400)
            return fig
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Weekly Points', 'Weekly Activities'),
            vertical_spacing=0.1,
            shared_xaxes=True
        )
        
        # Weekly points
        fig.add_trace(
            go.Bar(
                x=weekly_data['week'],
                y=weekly_data['weekly_points'],
                name='Weekly Points',
                marker_color=self.colors['primary'],
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Weekly activities
        fig.add_trace(
            go.Bar(
                x=weekly_data['week'],
                y=weekly_data['weekly_activities'],
                name='Weekly Activities',
                marker_color=self.colors['secondary'],
                showlegend=False
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=600,
            title_text="Weekly Progress Overview"
        )
        
        fig.update_xaxes(title_text="Week", row=2, col=1)
        fig.update_yaxes(title_text="Points", row=1, col=1)
        fig.update_yaxes(title_text="Activities", row=2, col=1)
        
        return fig
    
    def create_leaderboard_chart(self, leaderboard_data: pd.DataFrame, top_n: int = 10) -> go.Figure:
        """Create horizontal bar chart for leaderboard"""
        if leaderboard_data.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No leaderboard data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="gray")
            )
            fig.update_layout(title="Leaderboard", height=400)
            return fig
        
        # Take top N users
        top_users = leaderboard_data.head(top_n)
        
        # Create horizontal bar chart
        fig = go.Figure(data=[
            go.Bar(
                y=top_users['full_name'][::-1],  # Reverse for top-to-bottom display
                x=top_users['total_points'][::-1],
                orientation='h',
                marker=dict(
                    color=top_users['total_points'][::-1],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Points")
                ),
                text=top_users['total_points'][::-1],
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>' +
                             'Points: %{x}<br>' +
                             'Rank: %{customdata}<br>' +
                             '<extra></extra>',
                customdata=top_users['rank'][::-1]
            )
        ])
        
        fig.update_layout(
            title=f"Top {top_n} Leaderboard",
            xaxis_title="Total Points",
            yaxis_title="Users",
            height=max(400, top_n * 40),
            margin=dict(l=150)  # More space for names
        )
        
        return fig
    
    def create_ranking_gauge(self, user_ranking: Dict) -> go.Figure:
        """Create gauge chart showing user's ranking percentile"""
        percentile = user_ranking.get('percentile', 0)
        rank = user_ranking.get('rank', 0)
        total_users = user_ranking.get('total_users', 0)
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = percentile,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"Your Ranking<br>#{rank} of {total_users}"},
            delta = {'reference': 50, 'suffix': "th percentile"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': self.colors['primary']},
                'steps': [
                    {'range': [0, 25], 'color': "lightgray"},
                    {'range': [25, 50], 'color': "gray"},
                    {'range': [50, 75], 'color': "lightgreen"},
                    {'range': [75, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            height=400,
            font={'color': "darkblue", 'family': "Arial"}
        )
        
        return fig
    
    def create_team_comparison_chart(self, team_data: pd.DataFrame, top_n: int = 10) -> go.Figure:
        """Create team comparison chart"""
        if team_data.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No team data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="gray")
            )
            fig.update_layout(title="Team Leaderboard", height=400)
            return fig
        
        top_teams = team_data.head(top_n)
        
        fig = go.Figure()
        
        # Total team points
        fig.add_trace(go.Bar(
            name='Total Team Points',
            x=top_teams['team_name'],
            y=top_teams['total_team_points'],
            marker_color=self.colors['primary'],
            yaxis='y',
            offsetgroup=1
        ))
        
        # Average points per member (scaled for visibility)
        fig.add_trace(go.Bar(
            name='Avg Points per Member',
            x=top_teams['team_name'],
            y=top_teams['avg_points_per_member'],
            marker_color=self.colors['secondary'],
            yaxis='y2',
            offsetgroup=2
        ))
        
        # Create subplot with secondary y-axis
        fig.update_layout(
            xaxis=dict(title='Teams'),
            yaxis=dict(
                title='Total Team Points',
                titlefont=dict(color=self.colors['primary']),
                tickfont=dict(color=self.colors['primary'])
            ),
            yaxis2=dict(
                title='Average Points per Member',
                titlefont=dict(color=self.colors['secondary']),
                tickfont=dict(color=self.colors['secondary']),
                anchor="x",
                overlaying="y",
                side="right"
            ),
            title=f"Top {top_n} Teams Comparison",
            height=500,
            hovermode='x unified'
        )
        
        return fig
    
    def create_activity_heatmap(self, daily_progress: pd.DataFrame) -> go.Figure:
        """Create activity heatmap showing activity patterns"""
        if daily_progress.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No activity data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="gray")
            )
            fig.update_layout(title="Activity Heatmap", height=400)
            return fig
        
        # Prepare data for heatmap
        daily_progress['weekday'] = daily_progress['activity_date'].dt.day_name()
        daily_progress['week'] = daily_progress['activity_date'].dt.isocalendar().week
        
        # Create pivot table
        heatmap_data = daily_progress.pivot_table(
            values='daily_points',
            index='weekday',
            columns='week',
            fill_value=0
        )
        
        # Reorder weekdays
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = heatmap_data.reindex(weekday_order)
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='Viridis',
            hoverongaps=False,
            hovertemplate='Week: %{x}<br>Day: %{y}<br>Points: %{z}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Activity Heatmap by Day of Week",
            xaxis_title="Week of Year",
            yaxis_title="Day of Week",
            height=400
        )
        
        return fig

