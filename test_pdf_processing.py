#!/usr/bin/env python3
"""
Test script to process existing PDF files and show extracted data.
This will help verify the improved parsing works correctly.
"""

import os
import sys
import PyPDF2
import pyodbc
from datetime import datetime

# Add the current directory to path so we can import from extract_and_insert.py
sys.path.append('.')

# Import functions from the main script
from extract_and_insert import (
    extract_text_from_pdf, 
    parse_bol_data, 
    connect_sql,
    insert_bol_data_and_log,
    log_to_csv,
    log_to_sql
)

def test_pdf_processing():
    """Test the PDF processing with existing files"""
    
    attachments_dir = "attachments"
    
    if not os.path.exists(attachments_dir):
        print(f"Attachments directory '{attachments_dir}' not found!")
        return
    
    pdf_files = [f for f in os.listdir(attachments_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in '{attachments_dir}' directory!")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to test: {pdf_files}")
    
    # Connect to database (optional - comment out if you don't want to insert to DB)
    try:
        conn = connect_sql()
        print("✅ Connected to Azure SQL database.")
        db_connected = True
    except Exception as e:
        print(f"❌ Could not connect to Azure SQL: {e}")
        print("Will test parsing only (no database insertion).")
        db_connected = False
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(attachments_dir, pdf_file)
        print(f"\n{'='*80}")
        print(f"TESTING: {pdf_file}")
        print(f"{'='*80}")
        
        # Extract text from PDF
        print("\n1. Extracting text from PDF...")
        order_text = extract_text_from_pdf(pdf_path)
        
        if not order_text.strip():
            print("❌ No text extracted from this PDF!")
            continue
        
        # Parse BOL data from extracted text
        print("\n2. Parsing BOL data...")
        bol_data = parse_bol_data(order_text)
        
        # Display extracted data
        print("\n3. Extracted Data Summary:")
        print("-" * 40)
        non_null_count = 0
        for key, value in bol_data.items():
            if key == 'raw_text':
                continue  # Skip raw text in summary
            if value is not None:
                non_null_count += 1
                print(f"✅ {key}: {value}")
            else:
                print(f"❌ {key}: None")
        
        print(f"\n📊 Total fields extracted: {non_null_count} out of {len(bol_data) - 1}")
        
        # Test database insertion if connected
        if db_connected:
            print("\n4. Testing database insertion...")
            
            # Initialize log entry
            log_entry = {
                "email_from": "test@example.com",
                "email_subject": f"Test processing: {pdf_file}",
                "attachment_name": pdf_file,
                "status": "",
                "log_timestamp": datetime.now().isoformat(sep=' ', timespec='seconds'),
                "error_message": "",
                "extracted_fields": non_null_count
            }
            
            # Try to insert BOL data into database
            success = insert_bol_data_and_log(conn, bol_data, log_entry)
            
            if success:
                print("✅ Successfully inserted data into database!")
                # Log to SQL and CSV
                log_to_sql(conn, log_entry)
                log_to_csv(log_entry)
                print("✅ Logged to SQL and CSV.")
            else:
                print(f"❌ Failed to insert data: {log_entry.get('error_message', 'Unknown error')}")
                # Still log the failure
                log_to_sql(conn, log_entry)
                log_to_csv(log_entry)
        
        print(f"\n{'='*80}")
        print(f"FINISHED TESTING: {pdf_file}")
        print(f"{'='*80}")
    
    if db_connected:
        conn.close()
        print("\n🔌 Database connection closed.")
    
    print("\n🎉 Testing complete!")

if __name__ == "__main__":
    test_pdf_processing()
