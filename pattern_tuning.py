"""
Pattern tuning helper for BOL automation.
This helps you test and improve regex patterns for better data extraction.
"""

import re
import os
from extract_and_insert import extract_text_from_pdf

def test_date_extraction(text):
    """Test different date patterns to improve date extraction"""
    print("\n🗓️  TESTING DATE PATTERNS")
    print("-" * 50)
    
    # Your PDFs seem to have dates like "11-Jun-2025 00:00"
    date_patterns = [
        r'Ship Date:\s*\n\s*([0-9]{1,2}-[A-Za-z]{3}-[0-9]{4})',
        r'Delivery Date:\s*\n\s*([0-9]{1,2}-[A-Za-z]{3}-[0-9]{4})',
        r'Appt Date:\s*\n\s*([0-9]{1,2}-[A-Za-z]{3}-[0-9]{4})',
        r'([0-9]{1,2}-[A-Za-z]{3}-[0-9]{4})\s+[0-9]{2}:[0-9]{2}',  # Date with time
        r'Date[^:]*:\s*([0-9]{1,2}-[A-Za-z]{3}-[0-9]{4})',  # Any "Date:" field
    ]
    
    for i, pattern in enumerate(date_patterns):
        matches = re.findall(pattern, text, re.IGNORECASE)
        print(f"Pattern {i+1}: {pattern}")
        if matches:
            print(f"  ✅ Found: {matches}")
        else:
            print(f"  ❌ No matches")
        print()

def test_address_extraction(text):
    """Test patterns for better address extraction"""
    print("\n🏠 TESTING ADDRESS PATTERNS")
    print("-" * 50)
    
    # Look for address patterns in your documents
    address_patterns = [
        r'(\d+\s+[A-Z][A-Z\s]+(?:STREET|ST|DRIVE|DR|AVENUE|AVE|ROAD|RD|LANE|LN)\.?)\s*\n\s*([A-Z\s,]+\d{5})',
        r'Address:\s*\n\s*([^\n]+)\s*\n\s*([A-Z\s,]+\d{5})',
        r'(\d+\s+[A-Z][^\n,]+)\s*\n\s*([A-Z]+,\s*[A-Z]{2}\s+\d{5})',
    ]
    
    for i, pattern in enumerate(address_patterns):
        matches = re.findall(pattern, text, re.IGNORECASE)
        print(f"Pattern {i+1}: {pattern}")
        if matches:
            for match in matches[:3]:  # Show first 3
                print(f"  ✅ Street: {match[0]}")
                print(f"     City/State/Zip: {match[1]}")
        else:
            print(f"  ❌ No matches")
        print()

def find_missing_dates_in_text(text):
    """Look for any date-like patterns that we might be missing"""
    print("\n🔍 SEARCHING FOR ANY DATE PATTERNS")
    print("-" * 50)
    
    # Look for various date formats
    all_date_patterns = [
        r'\d{1,2}/\d{1,2}/\d{4}',      # MM/DD/YYYY
        r'\d{1,2}-\d{1,2}-\d{4}',      # MM-DD-YYYY
        r'\d{1,2}-[A-Za-z]{3}-\d{4}',  # DD-Mon-YYYY
        r'[A-Za-z]{3}\s+\d{1,2},?\s+\d{4}',  # Mon DD, YYYY
        r'\d{4}-\d{2}-\d{2}',          # YYYY-MM-DD
    ]
    
    for pattern in all_date_patterns:
        matches = re.findall(pattern, text)
        if matches:
            print(f"Pattern {pattern}: {matches}")

def analyze_pdf_for_improvements(pdf_path):
    """Analyze a specific PDF to suggest improvements"""
    print(f"\n📋 ANALYZING: {os.path.basename(pdf_path)}")
    print("=" * 70)
    
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("❌ Could not extract text")
        return
    
    # Test different extraction methods
    test_date_extraction(text)
    test_address_extraction(text)
    find_missing_dates_in_text(text)
    
    # Look for any patterns we might have missed
    print("\n🔍 LOOKING FOR ADDITIONAL PATTERNS")
    print("-" * 50)
    
    # Search for potential fields we're not capturing
    potential_fields = [
        ('Load/Truck Number', r'(?:Load|Truck|Vehicle)\s*(?:ID|Number|#)\s*:?\s*([A-Z0-9\-]+)'),
        ('Driver Name', r'Driver\s*:?\s*([A-Za-z\s]+)'),
        ('Special Instructions', r'(?:Instructions|Notes|Comments)\s*:?\s*([^\n]+)'),
        ('Delivery Window', r'(?:Delivery|Appt)\s*(?:Window|Time)\s*:?\s*([^\n]+)'),
        ('Contact Phone', r'(?:Phone|Tel|Contact)\s*:?\s*([\d\-\(\)\s]+)'),
    ]
    
    for field_name, pattern in potential_fields:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            print(f"✅ {field_name}: {matches}")
        else:
            print(f"❌ {field_name}: Not found")

def main():
    """Main function to analyze PDFs for improvements"""
    attachments_dir = "attachments"
    
    if not os.path.exists(attachments_dir):
        print(f"❌ Directory '{attachments_dir}' not found")
        return
    
    pdf_files = [f for f in os.listdir(attachments_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"❌ No PDF files found in '{attachments_dir}'")
        return
    
    print(f"🔍 Found {len(pdf_files)} PDF files to analyze")
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(attachments_dir, pdf_file)
        analyze_pdf_for_improvements(pdf_path)
    
    print("\n✅ Analysis complete!")
    print("\nTip: Use the patterns that show '✅ Found' to improve your regex in extract_and_insert.py")

if __name__ == "__main__":
    main()
