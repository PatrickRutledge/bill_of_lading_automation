-- Add BOL columns to existing tables
-- This script safely adds only the missing columns needed for BOL automation

-- First, let's check what tables exist and add missing columns

-- Add BOL-specific columns to the existing orders table (if they don't exist)
-- This makes the orders table compatible with BillOfLadingData structure

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'bol_number')
BEGIN
    ALTER TABLE dbo.orders ADD bol_number NVARCHAR(100);
    PRINT 'Added bol_number column to orders table';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'shipper_name')
BEGIN
    ALTER TABLE dbo.orders ADD shipper_name NVARCHAR(255);
    PRINT 'Added shipper_name column to orders table';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'shipper_address')
BEGIN
    ALTER TABLE dbo.orders ADD shipper_address NVARCHAR(500);
    PRINT 'Added shipper_address column to orders table';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'consignee_name')
BEGIN
    ALTER TABLE dbo.orders ADD consignee_name NVARCHAR(255);
    PRINT 'Added consignee_name column to orders table';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'consignee_address')
BEGIN
    ALTER TABLE dbo.orders ADD consignee_address NVARCHAR(500);
    PRINT 'Added consignee_address column to orders table';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'carrier_name')
BEGIN
    ALTER TABLE dbo.orders ADD carrier_name NVARCHAR(255);
    PRINT 'Added carrier_name column to orders table';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'shipment_date')
BEGIN
    ALTER TABLE dbo.orders ADD shipment_date NVARCHAR(50);
    PRINT 'Added shipment_date column to orders table';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'delivery_date')
BEGIN
    ALTER TABLE dbo.orders ADD delivery_date NVARCHAR(50);
    PRINT 'Added delivery_date column to orders table';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'origin_city')
BEGIN
    ALTER TABLE dbo.orders ADD origin_city NVARCHAR(255);
    PRINT 'Added origin_city column to orders table';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'destination_city')
BEGIN
    ALTER TABLE dbo.orders ADD destination_city NVARCHAR(255);
    PRINT 'Added destination_city column to orders table';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'total_weight')
BEGIN
    ALTER TABLE dbo.orders ADD total_weight FLOAT;
    PRINT 'Added total_weight column to orders table';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'total_pieces')
BEGIN
    ALTER TABLE dbo.orders ADD total_pieces INT;
    PRINT 'Added total_pieces column to orders table';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'freight_charges')
BEGIN
    ALTER TABLE dbo.orders ADD freight_charges FLOAT;
    PRINT 'Added freight_charges column to orders table';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'commodity_description')
BEGIN
    ALTER TABLE dbo.orders ADD commodity_description NVARCHAR(500);
    PRINT 'Added commodity_description column to orders table';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'reference_number')
BEGIN
    ALTER TABLE dbo.orders ADD reference_number NVARCHAR(100);
    PRINT 'Added reference_number column to orders table';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'updated_date')
BEGIN
    ALTER TABLE dbo.orders ADD updated_date DATETIME2 DEFAULT GETDATE();
    PRINT 'Added updated_date column to orders table';
END

-- Add extracted_fields column to order_log if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.order_log') AND name = 'extracted_fields')
BEGIN
    ALTER TABLE dbo.order_log ADD extracted_fields INT DEFAULT 0;
    PRINT 'Added extracted_fields column to order_log table';
END

-- Create indexes for better performance
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_orders_bol_number' AND object_id = OBJECT_ID('dbo.orders'))
BEGIN
    CREATE INDEX IX_orders_bol_number ON dbo.orders(bol_number);
    PRINT 'Created index on orders.bol_number';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_orders_created_date' AND object_id = OBJECT_ID('dbo.orders'))
BEGIN
    CREATE INDEX IX_orders_created_date ON dbo.orders(created_date);
    PRINT 'Created index on orders.created_date';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_order_log_log_timestamp' AND object_id = OBJECT_ID('dbo.order_log'))
BEGIN
    CREATE INDEX IX_order_log_log_timestamp ON dbo.order_log(log_timestamp);
    PRINT 'Created index on order_log.log_timestamp';
END

PRINT 'Database modification complete! Your existing orders table now supports BOL data.';
