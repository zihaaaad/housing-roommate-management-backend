# API Documentation — Housing & Roommate Management Platform

Base URL: `http://127.0.0.1:8000/api/v1`

All responses use this standard JSON format:
```json
{
  "success": true,
  "message": "Operation description",
  "data": { ... }
}
```

Paginated responses follow:
```json
{
  "success": true,
  "message": "Data retrieved successfully.",
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_items": 42,
    "total_pages": 5,
    "has_next_page": true,
    "has_prev_page": false
  }
}
```

---

## 1. Authentication & Security Module (`/auth`)

### 1.1 Register User
- **Method**: `POST`
- **Endpoint**: `/auth/register`
- **Access**: Public
- **Request Body**:
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePassword@123",
  "full_name": "John Doe",
  "phone_number": "+8801711000002",
  "role": "ROOMMATE_SEEKER"
}
```
- **Response**: `201 Created`
- **Error Codes**: `409 CONFLICT` (Duplicate email or username), `422 VALIDATION_ERROR`

### 1.2 Login User
- **Method**: `POST`
- **Endpoint**: `/auth/login`
- **Access**: Public
- **Request Body**:
```json
{
  "username_or_email": "user@example.com",
  "password": "SecurePassword@123"
}
```
- **Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOi...",
    "refresh_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "expires_in_seconds": 1800,
    "user": {
      "id": 1,
      "email": "user@example.com",
      "username": "johndoe",
      "full_name": "John Doe",
      "role": "ROOMMATE_SEEKER",
      "is_active": true,
      "is_verified": true
    }
  }
}
```
- **Error Codes**: `401 UNAUTHORIZED`

### 1.3 Refresh Access Token
- **Method**: `POST`
- **Endpoint**: `/auth/refresh`
- **Access**: Public (Requires valid refresh token)
- **Request Body**:
```json
{
  "refresh_token": "eyJhbGciOi..."
}
```
- **Response**: `200 OK`

### 1.4 Forgot Password
- **Method**: `POST`
- **Endpoint**: `/auth/forgot-password`
- **Access**: Public
- **Request Body**:
```json
{
  "email": "user@example.com"
}
```
- **Response**: `200 OK`

### 1.5 Reset Password
- **Method**: `POST`
- **Endpoint**: `/auth/reset-password`
- **Access**: Public
- **Request Body**:
```json
{
  "reset_token": "secure_random_token_from_email",
  "new_password": "BrandNewPassword@456"
}
```
- **Response**: `200 OK`

### 1.6 Change Password
- **Method**: `POST`
- **Endpoint**: `/auth/change-password`
- **Access**: Authenticated (`Bearer <access_token>`)
- **Request Body**:
```json
{
  "current_password": "BrandNewPassword@456",
  "new_password": "AnotherNewPassword@789"
}
```
- **Response**: `200 OK`

### 1.7 Current User Profile
- **Method**: `GET`
- **Endpoint**: `/auth/me`
- **Access**: Authenticated
- **Response**: `200 OK`

---

## 2. User & Preferences Profile Module (`/users`)

### 2.1 Get Current User's Profile Preferences
- **Method**: `GET`
- **Endpoint**: `/users/profile`
- **Access**: Authenticated

### 2.2 Update Profile Preferences
- **Method**: `PUT`
- **Endpoint**: `/users/profile`
- **Access**: Authenticated
- **Request Body**:
```json
{
  "bio": "Software developer looking for quiet place in Dhanmondi.",
  "occupation": "Developer",
  "age": 27,
  "gender": "Male",
  "budget_min": 8000.0,
  "budget_max": 15000.0,
  "preferred_city": "Dhaka",
  "preferred_neighborhood": "Dhanmondi",
  "cleanliness_level": "VERY_CLEAN",
  "sleep_schedule": "EARLY_BIRD",
  "smoking_habit": "NON_SMOKER",
  "pet_habit": "PET_FRIENDLY",
  "party_habit": "RARELY",
  "dietary_preference": "VEGETARIAN",
  "work_status": "REMOTE"
}
```
- **Response**: `200 OK`

### 2.3 Get My Complete Account Details
- **Method**: `GET`
- **Endpoint**: `/users/me/full`
- **Access**: Authenticated

### 2.4 Get User by ID
- **Method**: `GET`
- **Endpoint**: `/users/{user_id}`
- **Access**: Public

### 2.5 List All Users (Admin Only)
- **Method**: `GET`
- **Endpoint**: `/users?search=&role=&page=1&limit=10`
- **Access**: Admin only (`ADMIN` role)

### 2.6 Toggle User Active Status (Admin Only)
- **Method**: `PATCH`
- **Endpoint**: `/users/{user_id}/status?is_active=true`
- **Access**: Admin only

### 2.7 Update Basic Profile Details
- **Method**: `PUT`
- **Endpoint**: `/users/me/basic`
- **Access**: Authenticated
- **Request Body**:
```json
{
  "full_name": "Tanvir Hasan",
  "phone_number": "+8801712020101",
  "avatar_url": "https://example.com/avatar.jpg"
}
```
- **Response**: `200 OK`

### 2.8 Update User Role (Admin Only)
- **Method**: `PATCH`
- **Endpoint**: `/users/{user_id}/role`
- **Access**: Admin only
- **Request Body**:
```json
{
  "role": "LANDLORD"
}
```
- **Response**: `200 OK`

### 2.9 Delete Own Account
- **Method**: `DELETE`
- **Endpoint**: `/users/me`
- **Access**: Authenticated
- **Response**: `200 OK`

### 2.10 Delete User (Admin Only)
- **Method**: `DELETE`
- **Endpoint**: `/users/{user_id}`
- **Access**: Admin only
- **Response**: `200 OK`

---

## 3. Property & Room Listings Module (`/properties` & `/rooms`)

### 3.1 Create Property Listing
- **Method**: `POST`
- **Endpoint**: `/properties`
- **Access**: Landlord or Admin (`LANDLORD`, `ADMIN`)
- **Request Body**:
```json
{
  "title": "3-Bedroom Family Flat in Dhanmondi",
  "description": "Spacious flat with fast wifi and generator backup.",
  "property_type": "APARTMENT",
  "address": "House 42, Road 8A, Dhanmondi",
  "city": "Dhaka",
  "state": "Dhaka Division",
  "postal_code": "1209",
  "country": "Bangladesh",
  "total_bedrooms": 3,
  "total_bathrooms": 3,
  "square_feet": 1550,
  "furnished_status": "FURNISHED",
  "is_pet_friendly": true,
  "is_smoking_allowed": false,
  "parking_available": true,
  "amenities": "WIFI,ELEVATOR,GENERATOR_BACKUP,BALCONY",
  "base_monthly_rent": 32000.0,
  "security_deposit": 32000.0,
  "utilities_included": true,
  "lease_duration_months": 12
}
```
- **Response**: `201 Created`

### 3.2 List Properties (Extended Search & Filtering)
- **Method**: `GET`
- **Endpoint**: `/properties`
- **Access**: Public
- **Query Parameters**:
  - `search`: string (matches title, description, city, address, or ID)
  - `property_type`: `APARTMENT` | `HOUSE` | `STUDIO` | `SHARED_FLAT`
  - `status`: `AVAILABLE` | `PENDING` | `LEASED`
  - `city`: string
  - `min_rent`: number
  - `max_rent`: number
  - `min_bedrooms`: number
  - `min_bathrooms`: number
  - `is_pet_friendly`: boolean
  - `furnished_status`: `FURNISHED` | `SEMI_FURNISHED` | `UNFURNISHED`
  - `sort_by`: `created_at` | `base_monthly_rent` | `title` | `available_from`
  - `sort_order`: `asc` | `desc`
  - `page`: integer (default: 1)
  - `limit`: integer (default: 10, max: 100)

### 3.3 Get Landlord's Own Listings
- **Method**: `GET`
- **Endpoint**: `/properties/my-listings`
- **Access**: Landlord or Admin

### 3.4 Get Property Details
- **Method**: `GET`
- **Endpoint**: `/properties/{property_id}`
- **Access**: Public

### 3.5 Update Property Listing
- **Method**: `PUT`
- **Endpoint**: `/properties/{property_id}`
- **Access**: Landlord owner or Admin

### 3.6 Delete Property Listing
- **Method**: `DELETE`
- **Endpoint**: `/properties/{property_id}`
- **Access**: Landlord owner or Admin

### 3.7 Add Room to Property
- **Method**: `POST`
- **Endpoint**: `/properties/{property_id}/rooms`
- **Access**: Property owner or Admin
- **Request Body**:
```json
{
  "room_name": "Master Suite Bedroom",
  "room_type": "MASTER_WITH_BATH",
  "monthly_rent": 1200.0,
  "security_deposit": 600.0,
  "is_available": true,
  "private_bathroom": true,
  "square_feet": 220
}
```
- **Response**: `201 Created`

### 3.8 List Rooms for Property
- **Method**: `GET`
- **Endpoint**: `/properties/{property_id}/rooms`
- **Access**: Public

### 3.9 Get Room by ID
- **Method**: `GET`
- **Endpoint**: `/rooms/{room_id}`
- **Access**: Public

### 3.10 Update Room
- **Method**: `PUT`
- **Endpoint**: `/rooms/{room_id}`
- **Access**: Property owner or Admin

### 3.11 Delete Room
- **Method**: `DELETE`
- **Endpoint**: `/rooms/{room_id}`
- **Access**: Property owner or Admin

---

## 4. Roommate Matching & Requests Module (`/roommates`)

### 4.1 Get Roommate Compatibility Recommendations
- **Method**: `GET`
- **Endpoint**: `/roommates/matches?city=Dhaka&min_score=60.0&limit=20`
- **Access**: Authenticated
- **Response**: `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "user": {
        "id": 5,
        "full_name": "Arif Rahman",
        "email": "arif.rahman@seeker.com",
        "role": "ROOMMATE_SEEKER"
      },
      "profile": {
        "preferred_city": "Dhaka",
        "budget_min": 9000.0,
        "budget_max": 16000.0,
        "cleanliness_level": "VERY_CLEAN"
      },
      "compatibility": {
        "overall_score": 93.5,
        "budget_score": 100.0,
        "location_score": 100.0,
        "cleanliness_score": 100.0,
        "sleep_schedule_score": 100.0,
        "habits_score": 95.0,
        "party_score": 85.0
      }
    }
  ]
}
```

### 4.2 Send Roommate Request
- **Method**: `POST`
- **Endpoint**: `/roommates/requests`
- **Access**: Authenticated
- **Request Body**:
```json
{
  "recipient_id": 5,
  "property_id": 1,
  "message": "Hi! We matched with a 93% compatibility score. Interested in sharing a 2BR downtown?"
}
```
- **Response**: `201 Created`

### 4.3 Update Roommate Request Status (Accept / Reject / Cancel)
- **Method**: `PUT`
- **Endpoint**: `/roommates/requests/{request_id}`
- **Access**: Request recipient or requester (for cancellation)
- **Request Body**:
```json
{
  "status": "ACCEPTED",
  "response_message": "Awesome, let's schedule a meet-up!"
}
```
- **Response**: `200 OK`

### 4.4 List Received Roommate Requests
- **Method**: `GET`
- **Endpoint**: `/roommates/requests/received`
- **Access**: Authenticated

### 4.5 List Sent Roommate Requests
- **Method**: `GET`
- **Endpoint**: `/roommates/requests/sent`
- **Access**: Authenticated

### 4.6 Delete Sent Roommate Request
- **Method**: `DELETE`
- **Endpoint**: `/roommates/requests/{request_id}`
- **Access**: Requester or Admin
- **Response**: `200 OK`

---

## 5. Viewings & Inquiries Module (`/inquiries`)

### 5.1 Schedule Property Viewing
- **Method**: `POST`
- **Endpoint**: `/inquiries`
- **Access**: Authenticated
- **Request Body**:
```json
{
  "property_id": 1,
  "scheduled_viewing_date": "2026-09-25T14:30:00Z",
  "notes": "Would like to see the master bedroom."
}
```
- **Response**: `201 Created`

### 5.2 List My Viewing Inquiries
- **Method**: `GET`
- **Endpoint**: `/inquiries/my-inquiries`
- **Access**: Authenticated

### 5.3 List Landlord Received Inquiries
- **Method**: `GET`
- **Endpoint**: `/inquiries/landlord-inquiries`
- **Access**: Landlord or Admin

### 5.4 Get Viewing Inquiry by ID
- **Method**: `GET`
- **Endpoint**: `/inquiries/{inquiry_id}`
- **Access**: Participant or Admin

### 5.5 Update Viewing Status (Confirm / Reschedule / Cancel)
- **Method**: `PATCH`
- **Endpoint**: `/inquiries/{inquiry_id}/status`
- **Access**: Landlord or Admin (or applicant for cancel)
- **Request Body**:
```json
{
  "status": "CONFIRMED",
  "landlord_notes": "Viewing confirmed for 2:30 PM."
}
```
- **Response**: `200 OK`

### 5.6 Delete Viewing Inquiry
- **Method**: `DELETE`
- **Endpoint**: `/inquiries/{inquiry_id}`
- **Access**: Participant or Admin
- **Response**: `200 OK`

---

## 6. Rental Applications Module (`/applications`)

### 6.1 Submit Rental Application
- **Method**: `POST`
- **Endpoint**: `/applications`
- **Access**: Authenticated
- **Request Body**:
```json
{
  "property_id": 1,
  "room_id": 1,
  "proposed_move_in_date": "2026-10-01T00:00:00Z",
  "lease_duration_months": 12,
  "monthly_income": 75000.0,
  "credit_score": 750,
  "employment_status": "Software Engineer (Full-Time)",
  "emergency_contact_name": "Kamal Hossain",
  "emergency_contact_phone": "+8801711998877"
}
```
- **Response**: `201 Created`

### 6.2 Get Submitted Applications
- **Method**: `GET`
- **Endpoint**: `/applications/my-applications`
- **Access**: Authenticated

### 6.3 Get Landlord Applications
- **Method**: `GET`
- **Endpoint**: `/applications/landlord-applications`
- **Access**: Landlord or Admin

### 6.4 Get Application Details
- **Method**: `GET`
- **Endpoint**: `/applications/{application_id}`
- **Access**: Applicant, Landlord, or Admin

### 6.5 Update Application Status (Approve / Reject / Withdraw)
- **Method**: `PATCH`
- **Endpoint**: `/applications/{application_id}/status`
- **Access**: Landlord or Admin (Applicant for `WITHDRAWN`)
- **Request Body**:
```json
{
  "status": "APPROVED",
  "landlord_decision_notes": "Application accepted after verification."
}
```
- **Response**: `200 OK`

### 6.6 Delete Rental Application
- **Method**: `DELETE`
- **Endpoint**: `/applications/{application_id}`
- **Access**: Applicant or Admin
- **Response**: `200 OK`

---

## 7. Notifications Module (`/notifications`)

### 7.1 List User Notifications
- **Method**: `GET`
- **Endpoint**: `/notifications?unread_only=false`
- **Access**: Authenticated

### 7.2 Mark Single Notification as Read
- **Method**: `PATCH`
- **Endpoint**: `/notifications/{notification_id}/read`
- **Access**: Recipient only

### 7.3 Mark All Notifications as Read
- **Method**: `POST`
- **Endpoint**: `/notifications/mark-all-read`
- **Access**: Authenticated

### 7.4 Get Unread Notification Count
- **Method**: `GET`
- **Endpoint**: `/notifications/unread-count`
- **Access**: Authenticated

### 7.5 Clear Read Notifications
- **Method**: `DELETE`
- **Endpoint**: `/notifications/clear-read`
- **Access**: Authenticated
- **Response**: `200 OK`

### 7.6 Delete Single Notification
- **Method**: `DELETE`
- **Endpoint**: `/notifications/{notification_id}`
- **Access**: Recipient only
- **Response**: `200 OK`

---

## 8. Internal Messaging Module (`/messages`)

### 8.1 Send Direct Message
- **Method**: `POST`
- **Endpoint**: `/messages`
- **Access**: Authenticated
- **Request Body**:
```json
{
  "receiver_id": 2,
  "property_id": 1,
  "content": "Hi! Is this property still available for move-in next month?"
}
```
- **Response**: `201 Created`

### 8.2 Get Conversation Thread
- **Method**: `GET`
- **Endpoint**: `/messages/conversation/{other_user_id}`
- **Access**: Authenticated
- **Response**: `200 OK` (Auto-marks incoming messages as read)

### 8.3 Delete Direct Message
- **Method**: `DELETE`
- **Endpoint**: `/messages/{message_id}`
- **Access**: Sender or Admin
- **Response**: `200 OK`

