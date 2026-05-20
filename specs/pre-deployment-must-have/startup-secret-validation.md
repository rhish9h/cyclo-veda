# Startup Secret Validation

Assert that critical secrets (SECRET_KEY, database credentials, Strava keys) are not using insecure defaults at application startup, failing fast before the app serves traffic.
