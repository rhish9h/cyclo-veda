# Database Design

**Last Updated:** 2025-12-01  
**Schema Version:** v1.0

## Tables

### users

Stores user accounts and authentication data.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing ID |
| email | VARCHAR(255) | UNIQUE NOT NULL | User email address |
| username | VARCHAR(50) | UNIQUE NOT NULL | Display username |
| hashed_password | VARCHAR(255) | NOT NULL | bcrypt hash |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |
| is_superuser | BOOLEAN | DEFAULT FALSE | Admin privileges |
| created_at | TIMESTAMP | DEFAULT NOW() | Account creation |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update |

**Indexes:**
- UNIQUE INDEX on email
- UNIQUE INDEX on username

### strava_connections

Stores Strava OAuth tokens and connection data.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing ID |
| user_id | INTEGER | FOREIGN KEY users.id | Link to user |
| strava_athlete_id | BIGINT | UNIQUE NOT NULL | Strava athlete ID |
| access_token | TEXT | NOT NULL | Strava access token |
| refresh_token | TEXT | NOT NULL | Strava refresh token |
| expires_at | TIMESTAMP | NOT NULL | Token expiry |
| is_active | BOOLEAN | DEFAULT TRUE | Connection status |
| created_at | TIMESTAMP | DEFAULT NOW() | Connection created |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update |

**Indexes:**
- UNIQUE INDEX on strava_athlete_id
- INDEX on user_id
- INDEX on expires_at

### activities

Stores cycling activity data from Strava.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing ID |
| user_id | INTEGER | FOREIGN KEY users.id | Activity owner |
| strava_activity_id | BIGINT | UNIQUE NOT NULL | Strava activity ID |
| name | VARCHAR(255) | NOT NULL | Activity name |
| description | TEXT | NULL | Activity description |
| activity_type | VARCHAR(50) | NOT NULL | Ride, Run, etc. |
| distance | DECIMAL(10,2) | NULL | Distance in meters |
| duration | INTEGER | NULL | Duration in seconds |
| elevation_gain | INTEGER | NULL | Elevation in meters |
| start_date | TIMESTAMP | NOT NULL | UTC start time |
| start_date_local | TIMESTAMP | NOT NULL | Local start time |
| timezone | VARCHAR(50) | NULL | Timezone name |
| raw_data | JSONB | NULL | Complete Strava response |
| created_at | TIMESTAMP | DEFAULT NOW() | Record created |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update |

**Indexes:**
- UNIQUE INDEX on strava_activity_id
- INDEX on user_id
- INDEX on start_date
- INDEX on activity_type
- GIN INDEX on raw_data (for JSON queries)

### user_settings

Stores user preferences and configuration.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing ID |
| user_id | INTEGER | FOREIGN KEY users.id UNIQUE | Settings owner |
| preferences | JSONB | NULL | User preferences JSON |
| created_at | TIMESTAMP | DEFAULT NOW() | Settings created |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update |

**Indexes:**
- UNIQUE INDEX on user_id
- GIN INDEX on preferences (for JSON queries)

## Relationships

```
users (1) ←→ (many) strava_connections
users (1) ←→ (many) activities  
users (1) ←→ (1) user_settings
```

## Migration History

- **v1.0** (2025-12-01): Initial schema with users, strava_connections, activities, user_settings

## Notes

- All timestamps use UTC
- JSONB columns for flexible data storage
- Foreign key constraints ensure data integrity
- Indexes optimized for common query patterns
