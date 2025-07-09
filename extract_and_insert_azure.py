"""
Azure-compatible version of the BOL processing script.
This version uses environment variables for configuration and Azure blob storage for attachments.
"""

import imaplib
import email
from email.header import decode_header
import os
import PyPDF2
import pyodbc
import smtplib
from email.message import EmailMessage
from datetime import datetime
import re
import logging
import tempfile
import io

# Configure logging for Azure
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- AZURE CONFIGURATION ----
# These will be set as Application Settings in Azure Functions
def get_config():
    """Get configuration from environment variables (Azure Application Settings)"""
    config = {
        # Gmail credentials
        'IMAP_SERVER': os.environ.get('IMAP_SERVER', 'imap.gmail.com'),
        'EMAIL_USER': os.environ.get('EMAIL_USER'),
        'EMAIL_PASS': os.environ.get('EMAIL_PASS'),
        
        # Email settings
        'REJECTION_EMAIL': os.environ.get('REJECTION_EMAIL'),
        
        # Azure SQL credentials
        'AZURE_SERVER': os.environ.get('AZURE_SERVER'),
        'AZURE_DATABASE': os.environ.get('AZURE_DATABASE', 'OrderEntry'),
        'AZURE_USERNAME': os.environ.get('AZURE_USERNAME'),
        'AZURE_PASSWORD': os.environ.get('AZURE_PASSWORD'),
        'AZURE_DRIVER': os.environ.get('AZURE_DRIVER', '{ODBC Driver 18 for SQL Server}'),
    }
    
    # Validate required settings
    required_settings = ['EMAIL_USER', 'EMAIL_PASS', 'REJECTION_EMAIL', 
                        'AZURE_SERVER', 'AZURE_USERNAME', 'AZURE_PASSWORD']
    
    missing_settings = [key for key in required_settings if not config[key]]
    if missing_settings:
        raise ValueError(f"Missing required environment variables: {missing_settings}")
    
    return config

def connect_email(config):
    """Connect to Gmail IMAP"""
    logger.info("Connecting to Gmail IMAP...")
    mail = imaplib.IMAP4_SSL(config['IMAP_SERVER'])
    mail.login(config['EMAIL_USER'], config['EMAIL_PASS'])
    logger.info("Connected and logged in.")
    mail.select("inbox")
    return mail

def fetch_pdf_attachments(mail):
    """Fetch PDF attachments from unread emails"""
    logger.info("Searching for unread emails with attachments...")
    status, messages = mail.search(None, '(UNSEEN)')
    if status != "OK":
        logger.error("Error searching inbox.")
        return []
    
    msg_nums = messages[0].split()
    logger.info(f"Found {len(msg_nums)} unread emails.")
    attachments = []
    
    for num in msg_nums:
        status, data = mail.fetch(num, "(RFC822)")
        if status != "OK":
            logger.warning(f"Failed to fetch message {num}")
            continue
            
        msg = email.message_from_bytes(data[0][1])
        email_from = email.utils.parseaddr(msg.get("From"))[1]
        subject, encoding = decode_header(msg.get("Subject"))[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8", errors="replace")
        
        found_pdf = False
        for part in msg.walk():
            content_dispo = part.get("Content-Disposition", "")
            if part.get_content_maintype() == "multipart":
                continue
            if "attachment" in content_dispo:
                filename = part.get_filename()
                if filename:
                    decoded_filename, enc = decode_header(filename)[0]
                    if isinstance(decoded_filename, bytes):
                        decoded_filename = decoded_filename.decode(enc or "utf-8", errors="replace")
                    if decoded_filename.lower().endswith(".pdf"):
                        # Store PDF content in memory instead of file system
                        pdf_content = part.get_payload(decode=True)
                        logger.info(f"Found PDF attachment: {decoded_filename}")
                        attachments.append({
                            "email_num": num,
                            "email_from": email_from,
                            "email_subject": subject,
                            "attachment_name": decoded_filename,
                            "pdf_content": pdf_content
                        })
                        found_pdf = True
        
        if not found_pdf:
            logger.info(f"No PDF attachment found in email with subject: {subject}")
    
    logger.info(f"Finished processing emails. Found {len(attachments)} PDF attachments.")
    return attachments

def extract_text_from_pdf_content(pdf_content, filename):
    """Extract text from PDF content in memory"""
    logger.info(f"Extracting text from {filename}...")
    text = ""
    try:
        pdf_stream = io.BytesIO(pdf_content)
        reader = PyPDF2.PdfReader(pdf_stream)
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        logger.error(f"Error reading {filename}: {e}")
    
    logger.info(f"Extracted text ({len(text)} chars) from {filename}.")
    return text

# Import the parse_bol_data function from the original script
def parse_bol_data(text):
    """Parse shipping/logistics data from extracted PDF text"""
    # This is the same function from extract_and_insert.py
    # Including it here for Azure deployment
    logger.info("Parsing shipping data from extracted text...")
    
    bol_data = {
        'bol_number': None,
        'shipper_name': None,
        'shipper_address': None,
        'consignee_name': None,
        'consignee_address': None,
        'carrier_name': None,
        'shipment_date': None,
        'delivery_date': None,
        'origin_city': None,
        'destination_city': None,
        'total_weight': None,
        'total_pieces': None,
        'freight_charges': None,
        'commodity_description': None,
        'reference_number': None,
        'raw_text': text[:4000]
    }
    
    try:
        # BOL/Load ID patterns
        bol_patterns = [
            r'Load ID:\s*(\d+)',
            r'Order:\s*([0-9\-]+)',
            r'(\d{8,})',
            r'(?:BOL|B/L|Bill of Lading)\s*(?:Number|No\.?|#)\s*:?\s*([A-Z0-9\-]+)',
            r'BOL\s*(\d+)',
            r'B/L\s*([A-Z0-9\-]+)'
        ]
        for pattern in bol_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                bol_data['bol_number'] = match.group(1).strip()
                break
        
        # Shipper patterns
        if 'LITTLE FALLS DISTRIBUTION CENT' in text:
            bol_data['shipper_name'] = 'LITTLE FALLS DISTRIBUTION CENT'
            address_match = re.search(r'Address:\s*\n\s*([^\n]+)\s*\n\s*([^\n]+)', text, re.IGNORECASE)
            if address_match:
                bol_data['shipper_address'] = f"{address_match.group(1).strip()}, {address_match.group(2).strip()}"
        
        # Consignee patterns
        consignee_patterns = [
            r'(\d+\s+[A-Z][A-Z\s]+DRIVE)\s*\n\s*([A-Z\s,]+\d{5})\s*\n\s*([A-Z\s]+INDUSTRIES)',
            r'Stop\s*\n\s*Customer & Comments.*?\n.*?\n.*?\n\d+\s*\n\s*([^\n]+)\s*\n\s*([^\n]+)\s*\n\s*([^\n]+)',
        ]
        for pattern in consignee_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                if len(match.groups()) == 3:
                    bol_data['consignee_address'] = match.group(1).strip()
                    bol_data['consignee_name'] = match.group(3).strip()
                break
        
        # Carrier patterns
        carrier_patterns = [
            r'([A-Z\s,]+(?:LOGISTICS|TRANSPORT|TRUCKING|FREIGHT)[^\n]*)',
        ]
        for pattern in carrier_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                carrier_name = match.group(1).strip()
                if carrier_name and not carrier_name.lower().startswith(('load id', 'carrier:')):
                    bol_data['carrier_name'] = carrier_name
                    break
        
        # Date patterns
        date_patterns = [
            r'([0-9]{1,2}-[A-Za-z]{3}-[0-9]{4})\s+[0-9]{2}:[0-9]{2}',
            r'(\d{1,2}/\d{1,2}/\d{4})',
        ]
        dates_found = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                dates_found.extend(matches)
        
        if len(dates_found) >= 2:
            bol_data['shipment_date'] = dates_found[1]
            bol_data['delivery_date'] = dates_found[0]
        elif len(dates_found) == 1:
            bol_data['delivery_date'] = dates_found[0]
        
        # Weight patterns
        weight_patterns = [
            r'(\d{2,3},\d{3})\s*lbs',
            r'(\d{5,6})\s*(?:\n|$)',
        ]
        for pattern in weight_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                weight_str = match.group(1).replace(',', '')
                try:
                    weight_val = float(weight_str)
                    if weight_val > 100:
                        bol_data['total_weight'] = weight_val
                        break
                except ValueError:
                    continue
        
        # Pieces patterns
        pieces_patterns = [
            r'Roll\s*\n\s*(\d+)',
        ]
        for pattern in pieces_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                try:
                    pieces_val = int(match.group(1))
                    if pieces_val > 0 and pieces_val < 10000:
                        bol_data['total_pieces'] = pieces_val
                        break
                except ValueError:
                    continue
        
        # Commodity description
        commodity_patterns = [
            r'Grade Desc:\s*([^\n]+(?:\n[^\n]+)*?)(?=\n(?:Width|PO#|Part#))',
        ]
        for pattern in commodity_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                desc = match.group(1).strip()
                desc = ' '.join(desc.split())
                bol_data['commodity_description'] = desc
                break
        
        # Reference number
        ref_patterns = [
            r'Order:\s*([0-9\-]+)',
            r'PO#:\s*([A-Z0-9\-]+)',
        ]
        for pattern in ref_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                bol_data['reference_number'] = match.group(1).strip()
                break
        
        # Cities
        if 'LITTLE FALLS' in text:
            bol_data['origin_city'] = 'LITTLE FALLS, NY'
        if 'MONTVILLE' in text:
            bol_data['destination_city'] = 'MONTVILLE, NJ'
        elif 'PLAINFIELD' in text:
            bol_data['destination_city'] = 'PLAINFIELD, NJ'
        
    except Exception as e:
        logger.error(f"Error parsing BOL data: {e}")
    
    extracted_fields = [k for k, v in bol_data.items() if v is not None and k != 'raw_text']
    logger.info(f"Successfully extracted {len(extracted_fields)} BOL fields: {extracted_fields}")
    
    return bol_data

def connect_sql(config):
    """Connect to Azure SQL Database"""
    
    # Log available ODBC drivers for debugging
    try:
        available_drivers = pyodbc.drivers()
        logging.info(f"Available ODBC drivers: {available_drivers}")
    except Exception as e:
        logging.warning(f"Could not list ODBC drivers: {e}")
    
    # Try different drivers available in Azure Functions Linux environment
    drivers_to_try = [
        "{ODBC Driver 17 for SQL Server}",  # Most common in Azure Linux
        "{ODBC Driver 13 for SQL Server}",  # Older but widely available
        "{ODBC Driver 11 for SQL Server}",  # Even older fallback
        "{FreeTDS}",                        # Open source driver
        "{SQL Server}",                     # Basic driver
    ]
    
    last_error = None
    for driver in drivers_to_try:
        try:
            conn_str = (
                f"DRIVER={driver};"
                f"SERVER={config['AZURE_SERVER']};"
                f"DATABASE={config['AZURE_DATABASE']};"
                f"UID={config['AZURE_USERNAME']};"
                f"PWD={config['AZURE_PASSWORD']};"
                "Encrypt=yes;"
                "TrustServerCertificate=no;"
                "Connection Timeout=30;"
            )
            logging.info(f"Trying SQL driver: {driver}")
            conn = pyodbc.connect(conn_str)
            logging.info(f"✅ Successfully connected with driver: {driver}")
            return conn
        except Exception as e:
            logging.warning(f"❌ Driver {driver} failed: {str(e)}")
            last_error = e
            continue
    
    # If all drivers fail, raise the last error
    logging.error(f"All SQL drivers failed. Last error: {last_error}")
    raise last_error

def insert_bol_data_and_log(conn, bol_data, log_entry):
    """Insert parsed BOL data into dbo.orders table"""
    try:
        cursor = conn.cursor()
        
        insert_query = '''
            INSERT INTO dbo.orders (
                bol_number, shipper_name, shipper_address, consignee_name, consignee_address,
                carrier_name, shipment_date, delivery_date, origin_city, destination_city,
                total_weight, total_pieces, freight_charges, commodity_description,
                reference_number, raw_text, created_date, updated_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        cursor.execute(insert_query, (
            bol_data.get('bol_number'),
            bol_data.get('shipper_name'),
            bol_data.get('shipper_address'),
            bol_data.get('consignee_name'),
            bol_data.get('consignee_address'),
            bol_data.get('carrier_name'),
            bol_data.get('shipment_date'),
            bol_data.get('delivery_date'),
            bol_data.get('origin_city'),
            bol_data.get('destination_city'),
            bol_data.get('total_weight'),
            bol_data.get('total_pieces'),
            bol_data.get('freight_charges'),
            bol_data.get('commodity_description'),
            bol_data.get('reference_number'),
            bol_data.get('raw_text'),
            datetime.now(),
            datetime.now()
        ))
        
        conn.commit()
        log_entry['status'] = 'processed'
        log_entry['error_message'] = ''
        
        extracted_count = len([v for v in bol_data.values() if v is not None]) - 1
        log_entry['extracted_fields'] = extracted_count
        
        logger.info(f"Successfully inserted BOL data into dbo.orders. Extracted {extracted_count} fields.")
        return True
        
    except Exception as e:
        log_entry['status'] = 'rejected'
        log_entry['error_message'] = str(e)
        logger.error(f"Failed to insert BOL data: {e}")
        return False

def log_to_sql(conn, log_entry):
    """Log processing attempt to SQL"""
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO dbo.order_log 
            (email_from, email_subject, attachment_name, status, log_timestamp, error_message, extracted_fields)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            log_entry['email_from'],
            log_entry['email_subject'],
            log_entry['attachment_name'],
            log_entry['status'],
            log_entry['log_timestamp'],
            log_entry['error_message'],
            log_entry.get('extracted_fields', 0)
        ))
        conn.commit()
        logger.info("Logged to SQL order_log.")
    except Exception as e:
        logger.error(f"Failed to log to SQL: {e}")

def send_rejection_email(config, original_subject, pdf_content, filename):
    """Send rejection email with PDF attachment"""
    logger.info(f"Sending rejection email to {config['REJECTION_EMAIL']}...")
    msg = EmailMessage()
    msg['Subject'] = f"Order Rejected: {original_subject}"
    msg['From'] = config['EMAIL_USER']
    msg['To'] = config['REJECTION_EMAIL']
    msg.set_content("Order data could not be inserted into the database. See attached PDF.")
    
    msg.add_attachment(pdf_content, maintype="application", subtype="pdf", filename=filename)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(config['EMAIL_USER'], config['EMAIL_PASS'])
            smtp.send_message(msg)
        logger.info("Rejection email sent.")
    except Exception as e:
        logger.error(f"Failed to send rejection email: {e}")

def process_bol_emails():
    """Main processing function for Azure"""
    logger.info("=== Starting BOL Email Processing ===")
    
    try:
        logger.info("Loading configuration from environment variables...")
        config = get_config()
        logger.info("Configuration loaded successfully")
        
        # Connect to email
        logger.info("Connecting to Gmail...")
        mail = connect_email(config)
        
        logger.info("Fetching PDF attachments...")
        pdf_attachments = fetch_pdf_attachments(mail)
        
        if not pdf_attachments:
            logger.info("No PDF attachments found in unread emails.")
            return {"processed": 0, "successful": 0, "failed": 0}
        
        logger.info(f"Found {len(pdf_attachments)} PDF attachments to process")
        
        # Connect to database
        logger.info("Connecting to Azure SQL database...")
        conn = connect_sql(config)
        logger.info("Connected to Azure SQL database successfully")
        
        processed_count = 0
        success_count = 0
        failed_count = 0
        
        for att in pdf_attachments:
            logger.info(f"--- Processing attachment {processed_count + 1}/{len(pdf_attachments)}: {att['attachment_name']} ---")
            
            # Extract text from PDF
            logger.info("Extracting text from PDF...")
            order_text = extract_text_from_pdf_content(att['pdf_content'], att['attachment_name'])
            logger.info(f"Extracted {len(order_text)} characters from PDF")
            
            # Parse BOL data
            logger.info("Parsing BOL data...")
            bol_data = parse_bol_data(order_text)
            
            # Initialize log entry
            log_entry = {
                "email_from": att["email_from"],
                "email_subject": att["email_subject"],
                "attachment_name": att["attachment_name"],
                "status": "",
                "log_timestamp": datetime.now().isoformat(sep=' ', timespec='seconds'),
                "error_message": "",
                "extracted_fields": 0
            }
            
            # Insert data
            logger.info("Inserting BOL data into database...")
            success = insert_bol_data_and_log(conn, bol_data, log_entry)
            
            # Log results
            logger.info("Logging processing results...")
            log_to_sql(conn, log_entry)
            
            processed_count += 1
            if success:
                success_count += 1
                logger.info(f"✅ Successfully processed {att['attachment_name']}")
            else:
                failed_count += 1
                logger.warning(f"❌ Failed to process {att['attachment_name']}")
                logger.info("Sending rejection email...")
                send_rejection_email(config, att["email_subject"], att['pdf_content'], att['attachment_name'])
            
            logger.info(f"--- Completed processing {att['attachment_name']} ---")
        
        logger.info("Closing database connection...")
        conn.close()
        
        result = {
            "processed": processed_count,
            "successful": success_count,
            "failed": failed_count
        }
        
        logger.info(f"=== BOL Processing Complete ===")
        logger.info(f"Summary: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ BOL processing failed with error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        raise e

if __name__ == "__main__":
    # For local testing
    result = process_bol_emails()
    print(f"Processing result: {result}")
