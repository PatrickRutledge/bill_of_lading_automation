import azure.functions as func
import logging
import os
import sys
import tempfile
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main(mytimer: func.TimerRequest) -> None:
    """
    Azure Function entry point for BOL processing
    Runs daily at 9:00 AM UTC
    """
    utc_timestamp = datetime.utcnow().replace(tzinfo=None).isoformat()
    
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info(f'BOL processing function executed at {utc_timestamp}')
    
    try:
        # Import our main processing logic
        from extract_and_insert_azure import process_bol_emails
        
        # Process emails and return results
        result = process_bol_emails()
        
        logging.info(f'BOL processing completed successfully: {result}')
        
    except Exception as e:
        logging.error(f'BOL processing failed: {str(e)}')
        raise e

    logging.info(f'BOL processing function completed at {datetime.utcnow().isoformat()}')
