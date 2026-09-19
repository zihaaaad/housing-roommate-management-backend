# Housing & Roommate Management Platform - Backend

Backend for the Housing & Roommate Management Platform, built with **FastAPI**, **SQLAlchemy ORM**, **Pydantic V2**, and **JWT Authentication**.

---

## Tech Stack

- **Framework**: FastAPI
- **Database ORM**: SQLAlchemy 2.0
- **Database**: SQLite for development; supports PostgreSQL by updating the database URL
- **Data Validation**: Pydantic V2
- **Authentication**: JWT (Access and Refresh Tokens), Bcrypt password hashing
- **Testing**: Pytest with FastAPI TestClient
- **Package Manager**: pip or uv

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                     # App entry point, CORS, error handling
│   ├── config.py                   # Environment settings (.env)
│   ├── database.py                 # SQLite / PostgreSQL connection and session
│   ├── dependencies.py             # Auth dependencies and role checks
│   ├── core/
│   │   ├── exceptions.py           # Custom exception classes
│   │   ├── response.py             # Standard API response formats and pagination
│   │   └── security.py             # Password hashing, token generation and validation
│   ├── models/
│   │   ├── user.py                 # User model and roles
│   │   ├── profile.py              # User profile and roommate habits
│   │   ├── property.py             # Property listings
│   │   ├── room.py                 # Room details
│   │   ├── roommate_request.py     # Roommate connection requests
│   │   ├── inquiry.py              # Property viewing schedules
│   │   ├── application.py          # Rental applications
│   │   ├── notification.py         # User notifications
│   │   └── message.py              # User messages
│   ├── schemas/                    # Pydantic request and response schemas
│   ├── services/                   # Business logic and matching algorithm
│   └── routers/                    # API route handlers
├── tests/                          # Automated tests
├── Dockerfile                      # Docker container image
├── docker-compose.yml              # Docker setup for app and postgres database
├── .dockerignore                   # Docker build exclusions
├── seed.py                         # Seed script with test accounts
├── pytest.ini                      # Test configuration
├── requirements.txt                # Dependencies
├── .env.example                    # Environment template
└── API_DOCUMENTATION.md            # API documentation
```

---

## Requirements and Marking Rubric (50 Marks)

### 1. Authentication & Authorization (20 Marks)
- **Password Hashing**: Salted bcrypt hashing with cost factor 12.
- **JWT Flow**: Short-lived access tokens (`30m`) and refresh tokens (`7d`) with database hash tracking.
- **Route Protection & RBAC**: Role-based access control for `ADMIN`, `LANDLORD`, `TENANT`, and `ROOMMATE_SEEKER`.
- **Token Refresh**: Endpoint `/api/v1/auth/refresh` to get a new access token using a refresh token.
- **Password Reset**: Reset tokens with a 15-minute expiration time and SHA-256 hash storage.

### 2. Data Listing Extended (20 Marks)
- **Search**: Search across title, description, address, city, or ID (`?search=Dhaka`).
- **Filtering**:
  - Category: `APARTMENT`, `HOUSE`, `STUDIO`, `SHARED_FLAT`.
  - Status: `AVAILABLE`, `PENDING`, `LEASED`.
  - Date Range: `available_from_start` and `available_from_end`.
  - Price Range: `min_rent` and `max_rent`.
  - Other Filters: `min_bedrooms`, `min_bathrooms`, `is_pet_friendly`, `furnished_status`.
- **Sorting**: Sort by `created_at`, `base_monthly_rent`, `title`, or `available_from` (`asc` or `desc`).
- **Pagination**: Configurable page and limit with metadata (`page`, `limit`, `total_items`, `total_pages`).

### 3. CRUD & Forms (10 Marks)
- **CRUD Operations**: Complete CRUD for Users, Profiles, Properties, Rooms, Roommate Requests, Inquiries, Applications, and Messages.
- **Validation**: Pydantic V2 schema validation for all inputs, returning standard 422 errors on invalid data.

---

## Getting Started

### Option 1: Docker (Recommended)

Run the backend and PostgreSQL database with Docker Compose:

```bash
docker compose up --build
```

Populate the database with realistic seed data:

```bash
docker compose exec backend python seed.py
```

The API will be live at `http://127.0.0.1:8000`.

To stop the containers:

```bash
docker compose down
```

---

### Option 2: Local Python Setup

1. Create and activate a virtual environment:

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.\.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Seed the database:

```bash
python seed.py
```

4. Start the development server:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Interactive API documentation:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

---

## Seed Test Accounts

| Role | Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **ADMIN** | `admin@housing.com` | `Admin@123456` | Platform administration & moderation |
| **LANDLORD** | `rafiq.landlord@housing.com` | `Landlord@123456` | Owns Dhanmondi apartment and Chittagong studio |
| **LANDLORD** | `nasreen.landlord@housing.com` | `Landlord@123456` | Owns Bashundhara R/A shared flat listing |
| **ROOMMATE_SEEKER** | `tanvir.hasan@seeker.com` | `Seeker@123456` | Software engineer looking for roommate in Dhaka (Dhanmondi) |
| **ROOMMATE_SEEKER** | `arif.rahman@seeker.com` | `Seeker@123456` | Product designer seeking compatible roommate in Dhaka |
| **TENANT** | `sadia.chowdhury@seeker.com` | `Seeker@123456` | Graduate student at University of Dhaka |

---

## Running the Automated Test Suite

Run the full pytest suite:
```bash
pytest -v
```

---

## Switch to PostgreSQL

To use PostgreSQL instead of SQLite:
1. Update `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/housing_roommates_db
   ```
2. Run the seed script or start the app:
   ```bash
   python seed.py
   ```
   `psycopg2-binary` is already included in `requirements.txt`.

---

## Frontend Integration Notes

You can connect this backend directly to React, Next.js, Vue, or any mobile client.

### 1. Base URL and API Docs
- **Base API URL**: `http://127.0.0.1:8000/api/v1`
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`
- **CORS**: Enabled for all origins by default. Calls from `http://localhost:3000` or `http://localhost:5173` will work right away.

### 2. Standard Response Format
All endpoints return responses in this JSON format:

**Standard Success Response**:
```json
{
  "success": true,
  "message": "Operation completed successfully.",
  "data": { ... }
}
```

**Paginated Success Response**:
```json
{
  "success": true,
  "message": "Items retrieved successfully.",
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_items": 25,
    "total_pages": 3,
    "has_next_page": true,
    "has_prev_page": false
  }
}
```

**Error Response**:
```json
{
  "success": false,
  "message": "Clear explanation of the error",
  "error_code": "RESOURCE_NOT_FOUND",
  "details": null
}
```

### 3. Authentication & JWT Interceptor
1. **Login**: Send `POST /api/v1/auth/login` with `{ "username_or_email": "...", "password": "..." }`.
2. **Store Tokens**: Save `access_token` and `refresh_token` in localStorage or secure cookies.
3. **Attach Header**: Send `Authorization: Bearer <access_token>` with all authenticated requests.
4. **Auto-Refresh**: If an API call returns `401 UNAUTHORIZED`, call `POST /api/v1/auth/refresh` with `{ "refresh_token": "..." }` to obtain a fresh access token without logging the user out.

### 4. Key Frontend Workflows
- **Property Listing & Filters**: `GET /api/v1/properties?city=Dhaka&min_rent=10000&max_rent=35000&page=1&limit=10`. Supports search queries, category filters, and sorting.
- **Property Details**: `GET /api/v1/properties/{id}` returns the full listing including landlord contact card and nested room list.
- **Schedule Viewing**: `POST /api/v1/inquiries` with `property_id` and `scheduled_viewing_date`.
- **Submit Application**: `POST /api/v1/applications` with `property_id`, optional `room_id`, monthly income, and emergency contact details.
- **Roommate Matching**: `GET /api/v1/roommates/matches` returns ranked candidate profiles with an itemized compatibility score (budget, location, cleanliness, sleep schedule, habits).
- **Direct Messaging**: `GET /api/v1/messages/conversation/{other_user_id}` and `POST /api/v1/messages`.
- **Notifications**: `GET /api/v1/notifications/unread-count` for navbar badges, and `GET /api/v1/notifications` for the notification center.

