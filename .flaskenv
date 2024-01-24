DEBUG=True

FLASK_ENV=development
#FLASK_APP=gcp_prototype

# OAuth Configuration - Google Provider
GOOGLE_CLIENT_ID            = "740552632578-ott3n8c7rj1u8cfmjgaaaj3etmon0sl7.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET        = "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"
DISCOVERY_URL               = "https://accounts.google.com/.well-known/openid-configuration"

# SQL Configuration
SQLALCHEMY_DATABASE_URI         = "sqlite:///sqlite_db.db"
SQLALCHEMY_TRACK_MODIFICATIONS  = True