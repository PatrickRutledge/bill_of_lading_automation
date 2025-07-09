import imaplib
import email
from email.header import decode_header
import os
import PyPDF2
import pyodbc
import csv
import smtplib
from email.message import EmailMessage
from datetime import datetime
import re

# ---- CONFIGURATION ----
# Import configuration from separate file (not committed to git)
try:
    from config import *
except ImportError:
    print("❌ Configuration file 'config.py' not found!")
    print("   Please copy 'config_template.py' to 'config.py' and fill in your credentials.")
    exit(1)

def connect_email():
    print("Connecting to Gmail IMAP...")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    print("Connected and logged in.")
    mail.select("inbox")
    return mail

def fetch_pdf_attachments(mail):
    print("Searching for unread emails with attachments...")
    status, messages = mail.search(None, '(UNSEEN)')
    if status != "OK":
        print("Error searching inbox.")
        return []
    msg_nums = messages[0].split()
    print(f"Found {len(msg_nums)} unread emails.")
    attachments = []
    for num in msg_nums:
        status, data = mail.fetch(num, "(RFC822)")
        if status != "OK":
            print("Failed to fetch message", num)
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
                        if not os.path.exists(DOWNLOAD_DIR):
                            os.makedirs(DOWNLOAD_DIR)
                        filepath = os.path.join(DOWNLOAD_DIR, decoded_filename)
                        with open(filepath, "wb") as f:
                            f.write(part.get_payload(decode=True))
                        print(f"Saved PDF attachment to {filepath}")
                        attachments.append({
                            "email_num": num,
                            "email_from": email_from,
                            "email_subject": subject,
                            "attachment_name": decoded_filename,
                            "attachment_path": filepath
                        })
                        found_pdf = True
        if not found_pdf:
            print(f"No PDF attachment found in email with subject: {subject}")
    print("Finished downloading attachments.")
    return attachments

def extract_text_from_pdf(pdf_path):
    print(f"Extracting text from {pdf_path} ...")
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    print(f"Extracted text ({len(text)} chars).")
    return text

def parse_bol_data(text):
    """
    Parse shipping/logistics data from extracted PDF text.
    This function extracts key shipment fields using regex patterns
    tailored for delivery reports and shipping manifests.
    """
    print("Parsing shipping data from extracted text...")
    
    # Initialize data dictionary with default values
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
        'raw_text': text[:4000]  # Store first 4000 chars of raw text for reference
    }
    
    try:
        # BOL/Load ID patterns - updated for your document format
        bol_patterns = [
            r'Load ID:\s*(\d+)',  # "Load ID: 08186456"
            r'Order:\s*([0-9\-]+)',  # "Order: 181688-01"
            r'(\d{8,})',  # Any 8+ digit number (like 08186456)
            r'(?:BOL|B/L|Bill of Lading)\s*(?:Number|No\.?|#)\s*:?\s*([A-Z0-9\-]+)',
            r'BOL\s*(\d+)',
            r'B/L\s*([A-Z0-9\-]+)'
        ]
        for pattern in bol_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                bol_data['bol_number'] = match.group(1).strip()
                break
        
        # Shipper patterns - updated for your format
        # Look for the shipping site information
        if 'LITTLE FALLS DISTRIBUTION CENT' in text:
            bol_data['shipper_name'] = 'LITTLE FALLS DISTRIBUTION CENT'
            # Look for the address
            address_match = re.search(r'Address:\s*\n\s*([^\n]+)\s*\n\s*([^\n]+)', text, re.IGNORECASE)
            if address_match:
                bol_data['shipper_address'] = f"{address_match.group(1).strip()}, {address_match.group(2).strip()}"
        
        # Alternative shipper patterns if the above doesn't work
        shipper_patterns = [
            r'Site:\s*\n\s*([^\n]+)',  # "Site: LITTLE FALLS DISTRIBUTION CENT"
            r'Site:\s*([^\n]+)',       # Alternative site pattern
            r'(?:Ship From|Origin).*?\n([^\n]+)',
            r'(?:Shipper|From)\s*:?\s*\n?\s*([^\n]+(?:\n[^\n]+)*?)(?=\n(?:Consignee|To|Carrier|Date))',
            r'SHIPPER\s*\n\s*([^\n]+(?:\n[^\n]+)*?)(?=\n\s*CONSIGNEE)',
        ]
        if not bol_data['shipper_name']:  # Only if we haven't found it yet
            for pattern in shipper_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    shipper_info = match.group(1).strip()
                    if shipper_info and not shipper_info.lower().startswith('address'):
                        lines = [line.strip() for line in shipper_info.split('\n') if line.strip()]
                        if lines:
                            bol_data['shipper_name'] = lines[0]
                            if len(lines) > 1:
                                bol_data['shipper_address'] = ' '.join(lines[1:])
                    break
        
        # Consignee patterns - updated for your format
        consignee_patterns = [
            r'(\d+\s+[A-Z][A-Z\s]+DRIVE)\s*\n\s*([A-Z\s,]+\d{5})\s*\n\s*([A-Z\s]+INDUSTRIES)',  # Address pattern
            r'Stop\s*\n\s*Customer & Comments.*?\n.*?\n.*?\n\d+\s*\n\s*([^\n]+)\s*\n\s*([^\n]+)\s*\n\s*([^\n]+)',
            r'(?:Consignee|To)\s*:?\s*\n?\s*([^\n]+(?:\n[^\n]+)*?)(?=\n(?:Carrier|Date|Description))',
            r'CONSIGNEE\s*\n\s*([^\n]+(?:\n[^\n]+)*?)(?=\n\s*(?:CARRIER|DATE))',
        ]
        for pattern in consignee_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                if len(match.groups()) == 3:  # Address pattern match
                    bol_data['consignee_address'] = match.group(1).strip()
                    bol_data['consignee_name'] = match.group(3).strip()
                else:
                    consignee_info = match.group(1).strip()
                    lines = [line.strip() for line in consignee_info.split('\n') if line.strip()]
                    if lines:
                        bol_data['consignee_name'] = lines[0]
                        if len(lines) > 1:
                            bol_data['consignee_address'] = ' '.join(lines[1:])
                break
        
        # Carrier patterns - updated for your format
        carrier_patterns = [
            r'Carrier:\s*\n\s*([^\n]+)',            r'([A-Z\s,]+(?:LOGISTICS|TRANSPORT|TRUCKING|FREIGHT)[^\n]*)',
            r'(?:Carrier|Motor Carrier)\s*:?\s*([^\n]+)',
            r'CARRIER\s*\n\s*([^\n]+)',
        ]
        for pattern in carrier_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                carrier_name = match.group(1).strip()
                # Skip if it's just a label
                if carrier_name and not carrier_name.lower().startswith(('load id', 'carrier:')):
                    bol_data['carrier_name'] = carrier_name
                    break
        
        # Date patterns - updated based on pattern analysis  
        date_patterns = [
            r'([0-9]{1,2}-[A-Za-z]{3}-[0-9]{4})\s+[0-9]{2}:[0-9]{2}',  # "11-Jun-2025 00:00" format
            r'Ship Date:\s*\n\s*([0-9]{1,2}-[A-Za-z]{3}-[0-9]{4})',  # "Ship Date: 11-Jun-2025"
            r'Delivery Date:\s*\n\s*([0-9]{1,2}-[A-Za-z]{3}-[0-9]{4})',  # "Delivery Date: ..."
            r'Appt Date:\s*\n\s*([0-9]{1,2}-[A-Za-z]{3}-[0-9]{4})',  # "Appt Date: 12-Jun-2025"
            r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY format found in PDFs
            r'(?:Ship(?:ment)?\s*Date|Date\s*Shipped)\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'(?:Delivery\s*Date|Date\s*Delivered)\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        ]
        
        # Track which dates we find
        dates_found = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                dates_found.extend(matches)
        
        # Assign dates - first one as ship date, second as delivery date if available
        if len(dates_found) >= 2:
            bol_data['shipment_date'] = dates_found[1]  # Usually the earlier date is ship date
            bol_data['delivery_date'] = dates_found[0]  # Usually the later date is delivery date
        elif len(dates_found) == 1:
            # If only one date, try to determine which it is based on context
            date_value = dates_found[0]
            # Look for context clues around the date
            if re.search(rf'{re.escape(date_value)}.*(?:ship|departure)', text, re.IGNORECASE):
                bol_data['shipment_date'] = date_value
            elif re.search(rf'{re.escape(date_value)}.*(?:delivery|arrival|appt)', text, re.IGNORECASE):
                bol_data['delivery_date'] = date_value
            else:
                # Default to delivery date if no context
                bol_data['delivery_date'] = date_value
        
        # Weight patterns - updated for your format
        weight_patterns = [
            r'(\d{2,3},\d{3})\s*lbs',  # "44,000 lbs"
            r'(\d{5,6})\s*(?:\n|$)',  # "44000" at end of line
            r'(?:Total\s*)?Weight\s*:?\s*([0-9,]+(?:\.\d+)?)\s*(?:lbs?|pounds?)?',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:lbs?|pounds?)',
        ]
        for pattern in weight_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                weight_str = match.group(1).replace(',', '')
                try:
                    weight_val = float(weight_str)
                    # Only accept reasonable weight values (not tiny numbers like "1")
                    if weight_val > 100:
                        bol_data['total_weight'] = weight_val
                        break
                except ValueError:
                    continue
        
        # Pieces patterns - updated for your format
        pieces_patterns = [
            r'Roll\s*\n\s*(\d+)',  # "Roll 163"
            r'Units\s*\n\s*Qty\s*\n\s*Weight\s*\n\s*\d+\s*\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n(\d+)',
            r'(?:Total\s*)?Pieces\s*:?\s*(\d+)',
            r'(?:Total\s*)?Count\s*:?\s*(\d+)',
            r'(\d+)\s*pieces?',
        ]
        for pattern in pieces_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                try:
                    pieces_val = int(match.group(1))
                    # Only accept reasonable piece counts
                    if pieces_val > 0 and pieces_val < 10000:
                        bol_data['total_pieces'] = pieces_val
                        break
                except ValueError:
                    continue
        
        # Freight charges patterns - updated for your format
        freight_patterns = [
            r'(?:Freight\s*Charges?|Total\s*Charges?)\s*:?\s*\$?([0-9,]+(?:\.\d{2})?)',
            r'\$([0-9,]+(?:\.\d{2})?)\s*(?:freight|total)',
        ]
        for pattern in freight_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                charge_str = match.group(1).replace(',', '')
                try:
                    bol_data['freight_charges'] = float(charge_str)
                    break
                except ValueError:
                    continue
        
        # Origin and destination cities - updated for your format
        city_patterns = [
            r'LITTLE FALLS, NY\s+(\d{5})',  # Origin city from Site section
            r'MONTVILLE, NJ\s+(\d{5})',     # Destination city from delivery address
            r'([A-Z\s]+),\s*([A-Z]{2})\s+(\d{5})',  # General city, state, zip pattern
        ]
        for pattern in city_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if 'LITTLE FALLS' in pattern:
                    bol_data['origin_city'] = 'LITTLE FALLS, NY'
                elif 'MONTVILLE' in pattern:
                    bol_data['destination_city'] = 'MONTVILLE, NJ'
                elif len(match.groups()) >= 3:
                    city_state = f"{match.group(1).strip()}, {match.group(2).strip()}"
                    # Try to determine if this is origin or destination based on context
                    if not bol_data['origin_city']:
                        bol_data['origin_city'] = city_state
                    elif not bol_data['destination_city']:
                        bol_data['destination_city'] = city_state
        
        # Commodity description - updated for your format
        commodity_patterns = [
            r'Grade Desc:\s*([^\n]+(?:\n[^\n]+)*?)(?=\n(?:Width|PO#|Part#))',  # Get full description including next line
            r'(?:Part#|Part Number):\s*([^\n]+)',  # "Part#: 65022SFI"
            r'(?:Commodity|Description|Contents)\s*:?\s*([^\n]+)',
            r'DESCRIPTION\s*\n\s*([^\n]+)',
        ]
        for pattern in commodity_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                desc = match.group(1).strip()
                # Clean up the description
                desc = ' '.join(desc.split())  # Remove extra whitespace
                bol_data['commodity_description'] = desc
                break
        
        # Reference number - updated for your format
        ref_patterns = [
            r'Order:\s*([0-9\-]+)',        # "Order: 181688-01"
            r'PO#:\s*([A-Z0-9\-]+)',       # "PO#: 441727"
            r'(?:Reference|Ref\.?)\s*(?:Number|No\.?|#)\s*:?\s*([A-Z0-9\-]+)',
            r'REF\s*([A-Z0-9\-]+)',
        ]
        for pattern in ref_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                bol_data['reference_number'] = match.group(1).strip()
                break
        
    except Exception as e:
        print(f"Error parsing BOL data: {e}")
    
    # Log what was extracted
    extracted_fields = [k for k, v in bol_data.items() if v is not None and k != 'raw_text']
    print(f"Successfully extracted {len(extracted_fields)} BOL fields: {extracted_fields}")
    
    return bol_data

def send_rejection_email(rejection_to, original_subject, pdf_path):
    print(f"Sending rejection email to {rejection_to} ...")
    msg = EmailMessage()
    msg['Subject'] = f"Order Rejected: {original_subject}"
    msg['From'] = EMAIL_USER
    msg['To'] = rejection_to
    msg.set_content("Order data could not be inserted into the database. See attached PDF.")
    with open(pdf_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=os.path.basename(pdf_path))
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        print("Rejection email sent.")
    except Exception as e:
        print("Failed to send rejection email:", e)

def log_to_csv(log_entry):
    file_exists = os.path.isfile(LOG_CSV)
    with open(LOG_CSV, "a", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=log_entry.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(log_entry)

def insert_bol_data_and_log(conn, bol_data, log_entry):
    """
    Insert parsed BOL data into dbo.orders table.
    This uses the existing orders table with the newly added BOL columns.
    """
    try:
        cursor = conn.cursor()
        
        # Insert BOL data into orders table
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
        
        # Add extracted data info to log
        extracted_count = len([v for v in bol_data.values() if v is not None]) - 1  # -1 for raw_text
        log_entry['extracted_fields'] = extracted_count
        
        print(f"Successfully inserted BOL data into dbo.orders. Extracted {extracted_count} fields.")
        return True
        
    except Exception as e:
        log_entry['status'] = 'rejected'
        log_entry['error_message'] = str(e)
        print(f"Failed to insert BOL data: {e}")
        return False

def log_to_sql(conn, log_entry):
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
        print("Logged to SQL order_log.")
    except Exception as e:
        print("Failed to log to SQL:", e)

def connect_sql():
    conn_str = (
        f"DRIVER={AZURE_DRIVER};"
        f"SERVER={AZURE_SERVER};"
        f"DATABASE={AZURE_DATABASE};"
        f"UID={AZURE_USERNAME};"
        f"PWD={AZURE_PASSWORD};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str)

def validate_configuration():
    """
    Validate that all required configuration is set before running.
    """
    print("Validating configuration...")
    
    errors = []
    warnings = []
    
    # Check email configuration
    if EMAIL_USER == "patrickscottrutledge@gmail.com":
        warnings.append("EMAIL_USER is still set to the default. Update with your Gmail address.")
    
    if EMAIL_PASS == "YOUR_GMAIL_APP_PASSWORD_HERE":
        errors.append("EMAIL_PASS is still set to the default. Update with your Gmail App Password.")
    
    # Check Azure SQL configuration
    if AZURE_SERVER == "mcleod.database.windows.net":
        warnings.append("AZURE_SERVER is still set to the default. Update with your Azure SQL server.")
    
    if AZURE_USERNAME == "trucker@mcleod.database.windows.net":
        warnings.append("AZURE_USERNAME is still set to the default. Update with your Azure SQL username.")
    
    if AZURE_PASSWORD == "YOUR_AZURE_SQL_PASSWORD_HERE":
        errors.append("AZURE_PASSWORD is still set to the default. Update with your Azure SQL password.")
    
    # Check rejection email
    if REJECTION_EMAIL == "pat@burnfiddlesticks.com":
        warnings.append("REJECTION_EMAIL is still set to the default. Update with your fallback email.")
    
    # Display results
    if errors:
        print("\n❌ CONFIGURATION ERRORS (must fix before running):")
        for error in errors:
            print(f"   • {error}")
    
    if warnings:
        print("\n⚠️  CONFIGURATION WARNINGS (recommended to update):")
        for warning in warnings:
            print(f"   • {warning}")
    
    if not errors and not warnings:
        print("✅ Configuration looks good!")
        return True
    
    if errors:
        print(f"\n❌ Found {len(errors)} error(s). Please update the configuration before running.")
        return False
    
    if warnings:
        print(f"\n⚠️  Found {len(warnings)} warning(s). You may want to update these settings.")
        response = input("Continue anyway? (y/N): ").lower().strip()
        return response == 'y'
    
    return True

def main():
    print("Script started.")
    
    # Validate configuration before proceeding
    if not validate_configuration():
        print("Configuration validation failed. Exiting.")
        return
    
    mail = connect_email()
    pdf_attachments = fetch_pdf_attachments(mail)
    if not pdf_attachments:
        print("No PDF attachments found in unread emails.")
        return

    try:
        conn = connect_sql()
        print("Connected to Azure SQL database.")
    except Exception as e:
        print("Could not connect to Azure SQL:", e)
        return

    for att in pdf_attachments:
        print(f"\n--- Processing {att['attachment_name']} ---")
        
        # Extract text from PDF
        order_text = extract_text_from_pdf(att["attachment_path"])
        
        # Parse BOL data from extracted text
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
        
        # Insert BOL data into database
        success = insert_bol_data_and_log(conn, bol_data, log_entry)
        
        # Always log to SQL and CSV
        log_to_sql(conn, log_entry)
        log_to_csv(log_entry)
        
        # On failure, send rejection email
        if not success:
            send_rejection_email(REJECTION_EMAIL, att["email_subject"], att["attachment_path"])
        
        print(f"--- Finished processing {att['attachment_name']} ---")
    
    conn.close()
    print("Script complete.")

if __name__ == "__main__":
    main()