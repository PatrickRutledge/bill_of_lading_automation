"""
Simple reporting dashboard for BOL automation.
Run this to see processing statistics and recent activity.
"""

import pyodbc
from datetime import datetime, timedelta
from extract_and_insert import connect_sql

def print_processing_stats():
    """Display processing statistics"""
    try:
        conn = connect_sql()
        cursor = conn.cursor()
        
        print("📊 BOL PROCESSING DASHBOARD")
        print("=" * 60)
        
        # Overall stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_documents,
                SUM(CASE WHEN status = 'processed' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as failed
            FROM dbo.order_log
        """)
        
        overall = cursor.fetchone()
        success_rate = (overall[1] / overall[0] * 100) if overall[0] > 0 else 0
        
        print(f"\n📈 OVERALL STATISTICS")
        print(f"Total Documents Processed: {overall[0]}")
        print(f"Successful: {overall[1]}")
        print(f"Failed: {overall[2]}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Last 7 days stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_documents,
                SUM(CASE WHEN status = 'processed' THEN 1 ELSE 0 END) as successful,
                AVG(CAST(extracted_fields as FLOAT)) as avg_fields
            FROM dbo.order_log
            WHERE log_timestamp >= DATEADD(day, -7, GETDATE())
        """)
        
        recent = cursor.fetchone()
        
        print(f"\n📅 LAST 7 DAYS")
        print(f"Documents Processed: {recent[0] or 0}")
        print(f"Successful: {recent[1] or 0}")
        print(f"Average Fields Extracted: {recent[2]:.1f if recent[2] else 0}")
        
        # Recent activity
        cursor.execute("""
            SELECT TOP 10
                log_timestamp,
                attachment_name,
                status,
                extracted_fields,
                CASE WHEN LEN(error_message) > 50 
                     THEN LEFT(error_message, 50) + '...' 
                     ELSE error_message 
                END as short_error
            FROM dbo.order_log
            ORDER BY log_timestamp DESC
        """)
        
        recent_activity = cursor.fetchall()
        
        print(f"\n📋 RECENT ACTIVITY (Last 10 documents)")
        print("-" * 60)
        print(f"{'Timestamp':<20} {'File':<25} {'Status':<10} {'Fields':<6} {'Error'}")
        print("-" * 60)
        
        for row in recent_activity:
            timestamp = row[0][:16] if row[0] else ""  # Truncate timestamp
            filename = row[1][:24] if row[1] else ""   # Truncate filename
            status = "✅" if row[2] == 'processed' else "❌"
            fields = row[3] or 0
            error = row[4] or ""
            
            print(f"{timestamp:<20} {filename:<25} {status:<10} {fields:<6} {error}")
        
        # Most common errors
        cursor.execute("""
            SELECT 
                error_message,
                COUNT(*) as error_count
            FROM dbo.order_log
            WHERE status = 'rejected' AND error_message IS NOT NULL
            GROUP BY error_message
            ORDER BY COUNT(*) DESC
        """)
        
        errors = cursor.fetchall()
        
        if errors:
            print(f"\n❌ COMMON ERRORS")
            print("-" * 60)
            for error in errors[:5]:  # Show top 5 errors
                error_msg = error[0][:100] + "..." if len(error[0]) > 100 else error[0]
                print(f"({error[1]}x) {error_msg}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")

def show_recent_orders():
    """Show recently processed orders from the main orders table"""
    try:
        conn = connect_sql()
        cursor = conn.cursor()
        
        print(f"\n🚚 RECENT ORDERS (Last 10)")
        print("=" * 80)
        
        cursor.execute("""
            SELECT TOP 10
                bol_number,
                shipper_name,
                consignee_name,
                carrier_name,
                total_weight,
                total_pieces,
                created_date
            FROM dbo.orders
            WHERE bol_number IS NOT NULL
            ORDER BY created_date DESC
        """)
        
        orders = cursor.fetchall()
        
        if orders:
            print(f"{'BOL #':<12} {'Shipper':<20} {'Consignee':<20} {'Carrier':<15} {'Weight':<8} {'Pieces':<6} {'Date'}")
            print("-" * 95)
            
            for order in orders:
                bol = order[0] or ""
                shipper = (order[1] or "")[:19]
                consignee = (order[2] or "")[:19]
                carrier = (order[3] or "")[:14]
                weight = f"{order[4]:,.0f}" if order[4] else ""
                pieces = order[5] or ""
                date = order[6].strftime('%m/%d %H:%M') if order[6] else ""
                
                print(f"{bol:<12} {shipper:<20} {consignee:<20} {carrier:<15} {weight:<8} {pieces:<6} {date}")
        else:
            print("No orders found in the database.")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error retrieving orders: {e}")

def main():
    """Main dashboard function"""
    print_processing_stats()
    show_recent_orders()
    
    print(f"\n🕐 Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nTip: Run this script regularly to monitor your BOL automation!")

if __name__ == "__main__":
    main()
