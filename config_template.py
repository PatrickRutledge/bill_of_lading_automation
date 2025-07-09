# Configuration file for BOL automation
# Copy this file to config.py and fill in your actual values
# DO NOT commit config.py to the repository

# Gmail credentials (use an App Password, not your normal Gmail password)
IMAP_SERVER = "imap.gmail.com"
EMAIL_USER = "your_email@gmail.com"        # <-- Your actual Gmail address
EMAIL_PASS = "your_app_password_here"      # <-- Your Gmail App Password

# File and email settings
DOWNLOAD_DIR = "attachments"
LOG_CSV = "order_log.csv"
REJECTION_EMAIL = "your_fallback@email.com"  # <-- Your fallback email

# Azure SQL credentials
AZURE_SERVER = "your_server.database.windows.net"     # <-- Your Azure SQL server
AZURE_DATABASE = "OrderEntry"                          # <-- Your Azure SQL database name
AZURE_USERNAME = "your_username@your_server.database.windows.net"  # <-- Your Azure SQL username
AZURE_PASSWORD = "your_password_here"                  # <-- Your Azure SQL password
AZURE_DRIVER = "{ODBC Driver 18 for SQL Server}"
