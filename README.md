# Bill of Lading Automation System

This system automates the extraction of Bill of Lading (BOL) data from Gmail PDF attachments and inserts structured data into an Azure SQL database. The system is deployed as an Azure Function that runs automatically on a daily schedule.

## Features

- **Automated Gmail Processing**: Fetches unread emails with PDF attachments
- **PDF Text Extraction**: Extracts text content from PDF files using PyPDF2
- **BOL Data Parsing**: Uses regex patterns to extract structured BOL fields:
  - BOL Number
  - Shipper Name & Address
  - Consignee Name & Address
  - Carrier Name
  - Shipment & Delivery Dates
  - Origin & Destination Cities
  - Total Weight & Pieces
  - Freight Charges
  - Commodity Description
  - Reference Numbers
- **Database Integration**: Stores parsed data in Azure SQL Database
- **Comprehensive Logging**: Logs all processing attempts to both SQL and CSV
- **Error Handling**: Sends rejection emails for failed processing attempts
- **Azure Function Deployment**: Runs automatically on Azure with configurable timer schedule

## Architecture

- **Local Development**: `extract_and_insert.py` for testing and development
- **Azure Production**: `BolProcessor` Azure Function that runs daily at 9 AM UTC
- **Configuration Management**: Secure config system with template-based setup
- **Database**: Azure SQL Database with automated connection and logging

## Database Tables

### dbo.orders
Primary table for structured BOL data with fields for all extracted shipping information including:
- BOL details (number, references)
- Shipper and consignee information
- Carrier and routing details
- Weights, pieces, and charges
- Raw PDF text for reference

### dbo.order_log
Tracks every processing attempt with status, timestamp, error messages, and count of extracted fields.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup
Run the `database_setup_complete.sql` script on your Azure SQL Database to create all necessary tables and columns. This consolidated script:
- Creates or modifies the `dbo.orders` table with all BOL fields
- Creates the `dbo.order_log` table for processing tracking
- Adds performance indexes
- Is safe to run multiple times (uses IF NOT EXISTS checks)

This replaces all the individual SQL setup files from earlier development.

### 3. Configuration

**IMPORTANT**: This project uses a secure configuration system.

1. Copy the configuration template:
   ```bash
   cp config_template.py config.py
   ```

2. Edit `config.py` with your actual credentials:
   ```python
   # Gmail credentials (use App Password)
   EMAIL_USER = "your-email@gmail.com"
   EMAIL_PASS = "your-app-password"
   
   # Azure SQL credentials
   AZURE_SERVER = "your-server.database.windows.net"
   AZURE_DATABASE = "your-database-name"
   AZURE_USERNAME = "your-username@your-server"
   AZURE_PASSWORD = "your-password"
   
   # Rejection email recipient
   REJECTION_EMAIL = "fallback@yourdomain.com"
   ```

3. **Never commit `config.py` to git** - it contains sensitive credentials and is excluded by `.gitignore`

### 4. Azure Function Deployment

For production deployment, see `AZURE_CONFIGURATION_GUIDE.md` for detailed instructions on:
- Setting up Azure Function App
- Configuring environment variables securely
- Deploying the function code
- Monitoring and logging setup
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password for the application
3. Use the App Password (not your regular Gmail password) in the configuration

## Usage

### Local Development and Testing
Run the main script locally:
```bash
python extract_and_insert.py
```

### Production (Azure Function)
The system runs automatically as an Azure Function on a daily schedule (9 AM UTC). No manual intervention required.

### Processing Flow
The system will:
1. Connect to Gmail and fetch unread emails with PDF attachments
2. Download PDF attachments to the `attachments/` folder
3. Extract text from each PDF
4. Parse BOL data using regex patterns
5. Insert structured data into `dbo.orders`
6. Log results to `dbo.order_log` and `order_log.csv`
7. Send rejection emails for failed processing attempts
8. Mark processed emails as read

## BOL Parsing Patterns

The system uses regex patterns to extract BOL data. You may need to adjust these patterns in the `parse_bol_data()` function based on your specific BOL formats:

- **BOL Numbers**: Looks for "BOL", "B/L", or "Bill of Lading" followed by alphanumeric identifiers
- **Addresses**: Extracts multi-line address information for shippers and consignees
- **Dates**: Recognizes various date formats (MM/DD/YYYY, MM-DD-YYYY, etc.)
- **Weights**: Extracts numeric values followed by "lbs", "pounds", etc.
- **Monetary Values**: Recognizes dollar amounts for freight charges

## Logging and Monitoring

### CSV Logging
All processing attempts are logged to `order_log.csv` with:
- Email details (from, subject, attachment name)
- Processing status (processed/rejected)
- Timestamp
- Error messages
- Count of successfully extracted fields

### SQL Logging
Identical logging is maintained in the `dbo.order_log` table for database queries and reporting.

## Error Handling

- **Connection Failures**: Script logs errors and exits gracefully
- **PDF Processing Errors**: Individual PDFs that fail are logged as rejected
- **Database Errors**: SQL errors are captured and logged with full error messages
- **Parsing Failures**: BOL data extraction continues even if some fields can't be parsed

## Customization

### Adding New BOL Fields
1. Add new columns to the `dbo.orders` table
2. Add parsing logic in the `parse_bol_data()` function
3. Update the `insert_bol_data_and_log()` function to include the new fields

### Adjusting Parsing Patterns
Modify the regex patterns in `parse_bol_data()` to match your specific BOL formats. Test patterns using sample BOL text to ensure accuracy.

## Security Notes

- **Configuration Security**: Uses `config.py` (excluded from git) for sensitive credentials
- **Gmail App Passwords**: Uses App Passwords instead of regular Gmail passwords
- **Azure Security**: Stores credentials as Azure Function App environment variables
- **Database Security**: Uses encrypted connections to Azure SQL Database
- **Firewall Protection**: Azure SQL configured with appropriate firewall rules
- **Template System**: `config_template.py` provides safe setup guidance without exposing secrets

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed via `pip install -r requirements.txt`
2. **Database Connection**: Verify Azure SQL credentials and firewall settings
3. **Gmail Authentication**: Use App Passwords, not regular Gmail passwords
4. **PDF Parsing**: Some PDFs may have text extraction issues - check the raw_text field for debugging

### Debugging BOL Parsing

To debug BOL parsing issues:
1. Check the `raw_text` field in the database to see extracted PDF text
2. Test regex patterns against sample text
3. Add print statements in `parse_bol_data()` to trace pattern matching
4. Review the `extracted_fields` count in logs to see how many fields were successfully parsed

## File Structure

```
bill_of_lading_automation/
├── extract_and_insert.py         # Main automation script (local development)
├── extract_and_insert_azure.py   # Azure Function compatible version
├── config.py                     # Local configuration (not in git)
├── config_template.py            # Configuration template (safe for git)
├── requirements.txt              # Python dependencies (local)
├── requirements_azure.txt        # Azure Function dependencies
├── database_setup_complete.sql   # Complete database setup script
├── AZURE_CONFIGURATION_GUIDE.md  # Azure deployment instructions
├── README.md                     # This documentation
├── .gitignore                    # Protects sensitive files from git
├── .funcignore                   # Azure Function deployment exclusions
├── BolProcessor/                 # Azure Function
│   ├── __init__.py               # Azure Function main code
│   └── function.json             # Function configuration (timer schedule)
├── order_log.csv                 # Processing log (created during execution)
├── attachments/                  # Downloaded PDF attachments (ignored by git)
└── diagnostic_scripts/           # Various monitoring and testing scripts
```

## Production Status

✅ **DEPLOYED AND ACTIVE**

The system is currently deployed and running in production:
- **Azure Function**: `bol-processor-func` running daily at 9 AM UTC
- **Database**: Azure SQL Database with `dbo.orders` and `dbo.order_log` tables
- **Schedule**: Processes emails once per day (configurable in `BolProcessor/function.json`)
- **Monitoring**: Logs visible in Azure Application Insights
- **Last Update**: Timer changed from every minute to daily schedule for production use

### Current Configuration
- **Timer Schedule**: `"0 0 9 * * *"` (9 AM UTC daily)
- **Database**: Successfully inserting BOL data into `dbo.orders`
- **Logging**: All attempts tracked in `dbo.order_log`
- **Security**: All credentials secured via Azure environment variables