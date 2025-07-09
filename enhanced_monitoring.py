"""
Enhanced monitoring script for BOL automation.
This adds success notifications and better error handling.
"""

def send_success_email(email_to, processed_count, extracted_fields_summary):
    """Send a success notification email when PDFs are processed"""
    print(f"Sending success notification to {email_to}...")
    
    msg = EmailMessage()
    msg['Subject'] = f"BOL Processing Success - {processed_count} documents processed"
    msg['From'] = EMAIL_USER
    msg['To'] = email_to
    
    content = f"""
    ✅ BOL Automation Success Report
    
    Successfully processed {processed_count} PDF document(s).
    
    Processing Summary:
    {extracted_fields_summary}
    
    All data has been inserted into the database and logged.
    
    This is an automated message from your BOL processing system.
    """
    
    msg.set_content(content)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        print("Success notification sent.")
    except Exception as e:
        print(f"Failed to send success notification: {e}")

def generate_daily_report():
    """Generate a daily processing report"""
    try:
        conn = connect_sql()
        cursor = conn.cursor()
        
        # Get today's processing stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_processed,
                SUM(CASE WHEN status = 'processed' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as failed,
                AVG(CAST(extracted_fields as FLOAT)) as avg_fields_extracted
            FROM dbo.order_log 
            WHERE CAST(log_timestamp as DATE) = CAST(GETDATE() as DATE)
        """)
        
        stats = cursor.fetchone()
        
        report = f"""
        📊 Daily BOL Processing Report - {datetime.now().strftime('%Y-%m-%d')}
        
        Total Documents: {stats[0]}
        Successful: {stats[1]}
        Failed: {stats[2]}
        Average Fields Extracted: {stats[3]:.1f if stats[3] else 0}
        
        Success Rate: {(stats[1]/stats[0]*100) if stats[0] > 0 else 0:.1f}%
        """
        
        print(report)
        conn.close()
        return report
        
    except Exception as e:
        print(f"Error generating daily report: {e}")
        return None

# Add this to your main() function for enhanced monitoring
def enhanced_main():
    """Enhanced main function with better monitoring"""
    print("Script started.")
    
    # Validate configuration
    if not validate_configuration():
        print("Configuration validation failed. Exiting.")
        return
    
    # Connect to email and database
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
    
    # Process documents
    processed_count = 0
    success_count = 0
    summary_lines = []
    
    for att in pdf_attachments:
        print(f"\n--- Processing {att['attachment_name']} ---")
        
        # Extract and parse data
        order_text = extract_text_from_pdf(att["attachment_path"])
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
        success = insert_bol_data_and_log(conn, bol_data, log_entry)
        
        # Log results
        log_to_sql(conn, log_entry)
        log_to_csv(log_entry)
        
        # Track processing
        processed_count += 1
        if success:
            success_count += 1
            fields_count = log_entry.get('extracted_fields', 0)
            summary_lines.append(f"✅ {att['attachment_name']}: {fields_count} fields extracted")
        else:
            summary_lines.append(f"❌ {att['attachment_name']}: Processing failed")
            send_rejection_email(REJECTION_EMAIL, att["email_subject"], att["attachment_path"])
        
        print(f"--- Finished processing {att['attachment_name']} ---")
    
    # Send success notification if any documents were processed successfully
    if success_count > 0:
        summary = "\n".join(summary_lines)
        send_success_email(EMAIL_USER, processed_count, summary)
    
    conn.close()
    print(f"Script complete. Processed {processed_count} documents, {success_count} successful.")

if __name__ == "__main__":
    enhanced_main()
