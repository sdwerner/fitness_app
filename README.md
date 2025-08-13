# Fitness Challenge App

A comprehensive Streamlit application for managing team fitness challenges with user registration, performance tracking, and analytics.

## Features

- **User Management**: Registration, login, profile management
- **Team System**: Create and join teams for group challenges
- **Performance Tracking**: Record activities across multiple sports with automatic point calculation
- **Analytics Dashboard**: Individual and team performance comparisons
- **Demographic Analytics**: Performance breakdowns by location, age group, and gender
- **Customizable Scoring**: Easy-to-modify point system for different sports

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup Instructions

1. **Clone or download the application files**
   ```bash
   # If you have the files, navigate to the project directory
   cd fitness_challenge_app
   ```

2. **Install required packages**
   ```bash
   pip install streamlit pandas bcrypt plotly
   ```

3. **Run the application**
   ```bash
   streamlit run main.py
   ```

4. **Access the application**
   - Open your web browser and go to `http://localhost:8501`
   - The application will automatically create the SQLite database on first run

## Usage Guide

### Getting Started

1. **Register a new account**
   - Click on "Register" in the sidebar
   - Fill in your details (username, password, full name, email are required)
   - Optional: Add gender, age group, and location for analytics

2. **Login**
   - Use your username and password to log in
   - You'll be redirected to the main dashboard

### Recording Performance

1. **Navigate to "Record Performance"**
2. **Select a sport** from the dropdown menu
3. **Enter your performance value** (distance, time, reps, etc.)
4. **Choose the date** of your activity
5. **Add optional notes**
6. **Submit** - points will be automatically calculated

### Team Management

1. **Create a new team**
   - Go to "Team Management"
   - Enter team name and description
   - Click "Create Team"

2. **Join an existing team**
   - Select from available teams
   - Click "Join Team"

### Viewing Analytics

- **Dashboard**: Overview of your performance and recent activities
- **Performance History**: Detailed list of all your recorded activities
- **Analytics**: Comparative performance data (coming in future updates)

## Sports and Scoring System

The app includes 12 predefined sports with the following point system:

| Sport | Unit | Points per Unit |
|-------|------|----------------|
| Running | km | 10.0 |
| Cycling | km | 3.0 |
| Swimming | km | 50.0 |
| Walking | km | 5.0 |
| Push-ups | reps | 0.5 |
| Sit-ups | reps | 0.3 |
| Plank | minutes | 2.0 |
| Yoga | sessions | 15.0 |
| Weight Training | sessions | 20.0 |
| Basketball | hours | 12.0 |
| Tennis | hours | 15.0 |
| Football/Soccer | hours | 18.0 |

## Customization

### Adding New Sports

1. **Access the database** (fitness_challenge.db)
2. **Add to sports table**:
   ```sql
   INSERT INTO sports (sport_name, unit, points_per_unit, description)
   VALUES ('New Sport', 'unit', points_value, 'Description');
   ```

### Modifying Point Values

1. **Update the sports table**:
   ```sql
   UPDATE sports SET points_per_unit = new_value WHERE sport_name = 'Sport Name';
   ```

### Customizing Age Groups

Modify the age group options in:
- `database/db_manager.py` (database constraints)
- `main.py` (form options)

### Styling Customization

- **Colors and themes**: Modify the CSS in `main.py`
- **Layout**: Adjust column layouts and component arrangements
- **Metrics**: Add or modify dashboard metrics

## File Structure

```
fitness_challenge_app/
├── main.py                 # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── database/
│   ├── __init__.py
│   └── db_manager.py      # Database operations
├── utils/
│   ├── __init__.py
│   └── session_manager.py # User session management
├── pages/                 # Future: Additional pages
├── static/                # Future: Static assets
└── config/                # Future: Configuration files
```

## Database Schema

- **users**: User accounts and profiles
- **teams**: Team information
- **sports**: Available sports and scoring
- **performances**: Individual performance records

## Security Features

- **Password hashing**: Uses bcrypt for secure password storage
- **Session management**: Streamlit session-based authentication
- **Input validation**: Prevents SQL injection and validates user input

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all packages are installed with `pip install -r requirements.txt`
2. **Database errors**: Delete `fitness_challenge.db` to reset the database
3. **Port conflicts**: Use `streamlit run main.py --server.port 8502` for different port

### Support

For issues or feature requests, check the application logs in the terminal where you ran the Streamlit command.

## Future Enhancements

- Advanced analytics and visualizations
- Data export functionality
- Admin panel for managing sports and users
- Mobile-responsive design improvements
- Integration with fitness tracking devices
- Leaderboards and achievements system

## License

This application is provided as-is for fitness challenge management purposes.

