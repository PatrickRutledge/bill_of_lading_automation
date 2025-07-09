# Bill of Lading Automation System

This system automates the extraction of Bill of Lading (BOL) data from Gmail PDF attachments and inserts structured data into an Azure SQL database.

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

## Database Tables

### dbo.BillOfLadingData
Primary table for structured BOL data with fields for all extracted information.

### dbo.order_log
Tracks every processing attempt with status, timestamp, error messages, and count of extracted fields.

### dbo.orders
Legacy table for raw text storage (maintained for compatibility).

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup
Run the `setup_database_tables.sql` script on your Azure SQL Database to create the necessary tables and indexes.

### 3. Configuration
Update the configuration section in `extract_and_insert.py`:

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

### 4. Gmail App Password Setup
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password for the application
3. Use the App Password (not your regular Gmail password) in the configuration

## Usage

Run the main script:
```bash
python extract_and_insert.py
```

The script will:
1. Connect to Gmail and fetch unread emails with PDF attachments
2. Download PDF attachments to the `attachments/` folder
3. Extract text from each PDF
4. Parse BOL data using regex patterns
5. Insert structured data into `dbo.BillOfLadingData`
6. Log results to `dbo.order_log` and `order_log.csv`
7. Send rejection emails for failed processing attempts

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
1. Add new columns to the `dbo.BillOfLadingData` table
2. Add parsing logic in the `parse_bol_data()` function
3. Update the `insert_bol_data_and_log()` function to include the new fields

### Adjusting Parsing Patterns
Modify the regex patterns in `parse_bol_data()` to match your specific BOL formats. Test patterns using sample BOL text to ensure accuracy.

## Security Notes

- Use Gmail App Passwords instead of regular passwords
- Store database credentials securely
- Consider using environment variables for sensitive configuration
- Enable Azure SQL firewall rules for your IP addresses

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
├── extract_and_insert.py      # Main automation script
├── requirements.txt           # Python dependencies
├── setup_database_tables.sql  # Database setup script
├── README.md                  # This documentation
├── order_log.csv             # Processing log (created during execution)
└── attachments/              # Downloaded PDF attachments (created during execution)
```