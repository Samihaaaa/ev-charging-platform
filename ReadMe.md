# EV Charging Platform
A full-stack web application that allows users to find EV charging stations, view available charging slots, and book slots in real-time.

## Features
- **User Registration & Login** (JWT Authentication with fallback password hashing)
- **View EV Charging Stations** (Map and list views)
- **Check Available Charging Slots** (Real-time slot availability)
- **Book Charging Slots** (Instant booking with confirmation)
- **Cancel Bookings** (Immediate UI updates and slot release)
- **Dashboard with real-time data** (User stats and recent activity)
- **Error Handling** (Comprehensive error messages and debug logging)
- **CORS Enabled** (Cross-origin requests supported)

## Tech Stack
### Backend
- **FastAPI** (Python web framework)
- **SQLite** (Database - lightweight, no setup required)
- **SQLAlchemy** (ORM)
- **JWT Authentication** (Secure token-based auth)
- **Passlib** (Password hashing with SHA256 fallback)
- **CORS Middleware** (Cross-origin support)

### Frontend
- **HTML5** (Modern semantic markup)
- **CSS3** (Responsive design with CSS variables)
- **JavaScript** (Fetch API, React hooks pattern)
- **No build tools required** (Vanilla JS)

## Recent Fixes & Improvements
- **Fixed Login Authentication**: Resolved "Incorrect password" issues with proper password verification
- **Fixed Account Creation**: Registration now works with SHA256 password hashing fallback
- **Fixed Booking Cancellation**: Immediate UI updates and proper slot availability
- **Fixed Error Display**: No more "[object Object]" errors - proper string messages
- **Fixed CORS Issues**: Frontend can now communicate with backend
- **Fixed API URLs**: Using full backend URLs for all requests
- **Added Debug Logging**: Comprehensive logging for troubleshooting

## Database
- **SQLite** database (`ev.db`) - no external database required
- **Auto-seeded** with Bangalore EV charging stations on startup
- **User accounts** with secure password hashing
- **Booking management** with status tracking

## Quick Start

### Prerequisites
- Python 3.7+
- Node.js (optional, for frontend development)

### 1) Clone and Setup
```bash
git clone <repository-url>
cd ev_charging_platform
```

### 2) Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### 3) Start Backend Server
```bash
# Option 1: Using the startup script
python run_backend.py

# Option 2: Using uvicorn directly
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

### 4) Frontend Setup
```bash
cd frontend
# Use any local server (Live Server extension in VS Code, Python's http.server, etc.)
# Or simply open index.html in a browser with CORS disabled
```

### 5) Access the Application
- **Frontend**: `http://localhost:5500` (or your local server)
- **Backend API**: `http://127.0.0.1:8001`
- **API Documentation**: `http://127.0.0.1:8001/docs`

## Default Login Credentials
For testing, create a new account using the registration form or check the backend database for existing test users.

## API Endpoints
### Authentication
- `POST /auth/login` - User login
- `POST /users/` - User registration

### Stations & Bookings
- `GET /stations/` - Get all charging stations
- `GET /stations/{id}/slots` - Get available slots for a station
- `POST /bookings/` - Create a booking
- `DELETE /bookings/{id}` - Cancel a booking
- `GET /bookings/my` - Get user's bookings

### Dashboard
- `GET /stations/` - Station statistics
- `GET /bookings/my` - User booking data

## Project Structure
```
ev_charging_platform/
|
backend/
|--- app/
|   |--- routers/          # API endpoints
|   |--- models.py         # Database models
|   |--- auth.py           # Authentication logic
|   |--- main.py           # FastAPI app
|--- requirements.txt       # Python dependencies
|--- run_backend.py        # Startup script
|
frontend/
|--- src/
|   |--- pages/            # Page components
|   |--- services/         # API service layer
|--- index.html            # Main application
```

## Development Features
- **Hot reload** backend with `--reload` flag
- **Auto-generated API docs** at `/docs`
- **Debug logging** for troubleshooting
- **Error handling** with user-friendly messages
- **Responsive design** works on all devices

## Troubleshooting
- **Login Issues**: Check browser console for debug logs
- **CORS Errors**: Ensure backend is running on port 8001
- **Database Issues**: Delete `ev.db` to reset database
- **Registration Issues**: Check backend logs for password hashing errors


