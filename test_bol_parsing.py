"""
BOL Parsing Test Utility
This script helps test and validate BOL parsing logic with sample PDFs.
"""

import os
from extract_and_insert import extract_text_from_pdf, parse_bol_data

def test_bol_parsing(pdf_path):
    """Test BOL parsing with a specific PDF file"""
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return
    
    print(f"Testing BOL parsing with: {pdf_path}")
    print("=" * 60)
    
    # Extract text
    text = extract_text_from_pdf(pdf_path)
    print(f"\nExtracted text length: {len(text)} characters")
    
    # Show first 500 characters of extracted text
    print(f"\nFirst 500 characters of extracted text:")
    print("-" * 40)
    print(text[:500])
    print("-" * 40)
    
    # Parse BOL data
    bol_data = parse_bol_data(text)
    
    # Display results
    print(f"\nParsed BOL Data:")
    print("=" * 40)
    for field, value in bol_data.items():
        if field != 'raw_text' and value is not None:
            print(f"{field:20}: {value}")
    
    # Count extracted fields
    extracted_count = len([v for k, v in bol_data.items() if v is not None and k != 'raw_text'])
    print(f"\nTotal fields extracted: {extracted_count} out of {len(bol_data) - 1}")
    
    return bol_data

def test_all_pdfs_in_attachments():
    """Test parsing for all PDFs in the attachments folder"""
    attachments_dir = "attachments"
    if not os.path.exists(attachments_dir):
        print(f"Error: Attachments directory not found: {attachments_dir}")
        return
    
    pdf_files = [f for f in os.listdir(attachments_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in {attachments_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF files to test:")
    
    results = {}
    for pdf_file in pdf_files:
        pdf_path = os.path.join(attachments_dir, pdf_file)
        print(f"\n{'='*80}")
        print(f"Testing: {pdf_file}")
        print(f"{'='*80}")
        
        try:
            bol_data = test_bol_parsing(pdf_path)
            extracted_count = len([v for k, v in bol_data.items() if v is not None and k != 'raw_text'])
            results[pdf_file] = extracted_count
        except Exception as e:
            print(f"Error testing {pdf_file}: {e}")
            results[pdf_file] = 0
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    for pdf_file, count in results.items():
        print(f"{pdf_file:40}: {count} fields extracted")

def show_regex_patterns():
    """Display the regex patterns being used for parsing"""
    print("Current BOL Parsing Patterns:")
    print("=" * 50)
    
    patterns = {
        "BOL Number": [
            r'(?:BOL|B/L|Bill of Lading)\s*(?:Number|No\.?|#)\s*:?\s*([A-Z0-9\-]+)',
            r'BOL\s*(\d+)',
            r'B/L\s*([A-Z0-9\-]+)',
        ],
        "Shipper": [
            r'(?:Shipper|From)\s*:?\s*\n?\s*([^\n]+(?:\n[^\n]+)*?)(?=\n(?:Consignee|To|Carrier|Date))',
        ],
        "Weight": [
            r'(?:Total\s*)?Weight\s*:?\s*([0-9,]+(?:\.\d+)?)\s*(?:lbs?|pounds?)?',
        ],
        "Date": [
            r'(?:Ship(?:ment)?\s*Date|Date\s*Shipped)\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        ]
    }
    
    for category, pattern_list in patterns.items():
        print(f"\n{category}:")
        for i, pattern in enumerate(pattern_list, 1):
            print(f"  {i}. {pattern}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test specific PDF file
        pdf_path = sys.argv[1]
        test_bol_parsing(pdf_path)
    else:
        # Show menu
        print("BOL Parsing Test Utility")
        print("=" * 30)
        print("1. Test all PDFs in attachments folder")
        print("2. Show regex patterns")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            test_all_pdfs_in_attachments()
        elif choice == "2":
            show_regex_patterns()
        elif choice == "3":
            print("Goodbye!")
        else:
            print("Invalid choice. Usage:")
            print("  python test_bol_parsing.py                    # Show menu")
            print("  python test_bol_parsing.py path/to/file.pdf   # Test specific file")
