"""
Debug script to examine PDF text extraction and BOL data parsing.
This will help us see what text is extracted and what patterns are/aren't matching.
"""

import PyPDF2
import os
import re
from extract_and_insert import parse_bol_data

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF and show detailed output"""
    print(f"Extracting text from {pdf_path}...")
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            print(f"PDF has {len(reader.pages)} pages")
            
            for page_num, page in enumerate(reader.pages):
                print(f"\n--- PAGE {page_num + 1} ---")
                page_text = page.extract_text()
                if page_text:
                    print(f"Page {page_num + 1} text length: {len(page_text)} characters")
                    text += page_text
                    # Show first 500 chars of each page
                    print("First 500 characters:")
                    print(repr(page_text[:500]))
                    print("\n" + "="*50 + "\n")
                else:
                    print(f"Page {page_num + 1}: No text extracted")
                    
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return None
    
    print(f"\nTotal extracted text: {len(text)} characters")
    return text

def debug_parsing_patterns(text):
    """Test individual regex patterns to see what matches"""
    print("\n" + "="*60)
    print("DEBUGGING REGEX PATTERNS")
    print("="*60)
    
    # Test BOL Number patterns
    print("\n--- BOL NUMBER PATTERNS ---")
    bol_patterns = [
        r'(?:BOL|B/L|Bill of Lading)\s*(?:Number|No\.?|#)\s*:?\s*([A-Z0-9\-]+)',
        r'BOL\s*(\d+)',
        r'B/L\s*([A-Z0-9\-]+)',
        r'Bill of Lading\s*([A-Z0-9\-]+)',
        r'(?:Bill|BOL).*?(\d{6,})',  # Look for longer numbers
        r'(\d{8,})',  # Any 8+ digit number
    ]
    
    for i, pattern in enumerate(bol_patterns):
        matches = re.findall(pattern, text, re.IGNORECASE)
        print(f"Pattern {i+1}: {pattern}")
        print(f"Matches: {matches}")
        print()
    
    # Test Shipper patterns
    print("\n--- SHIPPER PATTERNS ---")
    shipper_patterns = [
        r'(?:Shipper|From)\s*:?\s*\n?\s*([^\n]+)',
        r'SHIPPER\s*\n\s*([^\n]+)',
        r'Ship\s*To.*?\n([^\n]+)',
        r'(?:Ship|From).*?([A-Z][A-Za-z\s&.,]+(?:\n[A-Za-z\s0-9.,]+)*)',
    ]
    
    for i, pattern in enumerate(shipper_patterns):
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        print(f"Pattern {i+1}: {pattern}")
        print(f"Matches: {matches[:3]}")  # Show first 3 matches
        print()
    
    # Test Weight patterns
    print("\n--- WEIGHT PATTERNS ---")
    weight_patterns = [
        r'(?:Total\s*)?Weight\s*:?\s*([0-9,]+(?:\.\d+)?)\s*(?:lbs?|pounds?)?',
        r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:lbs?|pounds?)',
        r'Weight.*?(\d+[,\d]*\.?\d*)',
        r'(\d+)\s*(?:LB|lb|LBS|lbs)',
    ]
    
    for i, pattern in enumerate(weight_patterns):
        matches = re.findall(pattern, text, re.IGNORECASE)
        print(f"Pattern {i+1}: {pattern}")
        print(f"Matches: {matches}")
        print()
    
    # Look for common BOL keywords
    print("\n--- COMMON BOL KEYWORDS FOUND ---")
    keywords = ['shipper', 'consignee', 'carrier', 'weight', 'freight', 'delivery', 'origin', 'destination', 'pieces', 'total']
    for keyword in keywords:
        count = len(re.findall(keyword, text, re.IGNORECASE))
        print(f"'{keyword}': found {count} times")
    
    print("\n--- RAW TEXT SAMPLE (first 1000 chars) ---")
    print(repr(text[:1000]))

def main():
    """Main function to debug PDF extraction"""
    attachments_dir = "attachments"
    
    if not os.path.exists(attachments_dir):
        print(f"No {attachments_dir} directory found.")
        return
    
    # Find PDF files
    pdf_files = [f for f in os.listdir(attachments_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in {attachments_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF files:")
    for i, pdf in enumerate(pdf_files):
        print(f"{i+1}. {pdf}")
    
    # Let user choose which PDF to analyze
    if len(pdf_files) == 1:
        chosen_pdf = pdf_files[0]
        print(f"\nAnalyzing: {chosen_pdf}")
    else:
        try:
            choice = int(input(f"\nEnter number (1-{len(pdf_files)}) to analyze: ")) - 1
            chosen_pdf = pdf_files[choice]
        except (ValueError, IndexError):
            print("Invalid choice. Using first PDF.")
            chosen_pdf = pdf_files[0]
    
    pdf_path = os.path.join(attachments_dir, chosen_pdf)
    
    # Extract text
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("Could not extract text from PDF")
        return
    
    # Debug regex patterns
    debug_parsing_patterns(text)
    
    # Try the existing parsing function
    print("\n" + "="*60)
    print("TESTING EXISTING PARSE_BOL_DATA FUNCTION")
    print("="*60)
    
    bol_data = parse_bol_data(text)
    
    print("\nExtracted BOL Data:")
    for key, value in bol_data.items():
        if key != 'raw_text':  # Skip the long raw text field
            print(f"{key}: {value}")
    
    print(f"\nTotal non-null fields: {len([v for v in bol_data.values() if v is not None])}")

if __name__ == "__main__":
    main()
