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
    Runs every minute (for testing)
    """
    utc_timestamp = datetime.utcnow().replace(tzinfo=None).isoformat()
    
    # Enhanced logging for Application Insights
    logging.info(f'=== BOL PROCESSOR STARTED ===')
    logging.info(f'Function executed at {utc_timestamp}')
    logging.info(f'Timer past due: {mytimer.past_due}')
    
    if mytimer.past_due:
        logging.warning('The timer is past due!')

    try:
        # Import our main processing logic
        logging.info('Importing BOL processing module...')
        from extract_and_insert_azure import process_bol_emails
        
        # Process emails and return results
        logging.info('Starting email processing...')
        result = process_bol_emails()
        
        logging.info(f'BOL processing completed successfully')
        logging.info(f'Processing result: {result}')
        
    except ImportError as e:
        logging.error(f'Failed to import processing module: {str(e)}')
        logging.error(f'Python path: {sys.path}')
        logging.error(f'Current working directory: {os.getcwd()}')
        raise e
    except Exception as e:
        logging.error(f'BOL processing failed with error: {str(e)}')
        logging.error(f'Error type: {type(e).__name__}')
        raise e

    completion_time = datetime.utcnow().isoformat()
    logging.info(f'=== BOL PROCESSOR COMPLETED at {completion_time} ===')
