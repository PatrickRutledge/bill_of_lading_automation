-- Add BOL columns to existing orders table
-- Run this in Azure Data Studio

-- Add all the BOL columns to the orders table if they don't exist
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'bol_number')
BEGIN
    ALTER TABLE dbo.orders ADD bol_number NVARCHAR(100);
    PRINT 'Added bol_number column';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'shipper_name')
BEGIN
    ALTER TABLE dbo.orders ADD shipper_name NVARCHAR(255);
    PRINT 'Added shipper_name column';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'shipper_address')
BEGIN
    ALTER TABLE dbo.orders ADD shipper_address NVARCHAR(500);
    PRINT 'Added shipper_address column';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'consignee_name')
BEGIN
    ALTER TABLE dbo.orders ADD consignee_name NVARCHAR(255);
    PRINT 'Added consignee_name column';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'consignee_address')
BEGIN
    ALTER TABLE dbo.orders ADD consignee_address NVARCHAR(500);
    PRINT 'Added consignee_address column';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'carrier_name')
BEGIN
    ALTER TABLE dbo.orders ADD carrier_name NVARCHAR(255);
    PRINT 'Added carrier_name column';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'shipment_date')
BEGIN
    ALTER TABLE dbo.orders ADD shipment_date NVARCHAR(50);
    PRINT 'Added shipment_date column';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'delivery_date')
BEGIN
    ALTER TABLE dbo.orders ADD delivery_date NVARCHAR(50);
    PRINT 'Added delivery_date column';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'origin_city')
BEGIN
    ALTER TABLE dbo.orders ADD origin_city NVARCHAR(255);
    PRINT 'Added origin_city column';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'destination_city')
BEGIN
    ALTER TABLE dbo.orders ADD destination_city NVARCHAR(255);
    PRINT 'Added destination_city column';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'total_weight')
BEGIN
    ALTER TABLE dbo.orders ADD total_weight FLOAT;
    PRINT 'Added total_weight column';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'total_pieces')
BEGIN
    ALTER TABLE dbo.orders ADD total_pieces INT;
    PRINT 'Added total_pieces column';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'freight_charges')
BEGIN
    ALTER TABLE dbo.orders ADD freight_charges FLOAT;
    PRINT 'Added freight_charges column';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'commodity_description')
BEGIN
    ALTER TABLE dbo.orders ADD commodity_description NVARCHAR(500);
    PRINT 'Added commodity_description column';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'reference_number')
BEGIN
    ALTER TABLE dbo.orders ADD reference_number NVARCHAR(100);
    PRINT 'Added reference_number column';
END

IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'updated_date')
BEGIN
    ALTER TABLE dbo.orders ADD updated_date DATETIME2 DEFAULT GETDATE();
    PRINT 'Added updated_date column';
END

-- Add extracted_fields column to order_log if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.order_log') AND name = 'extracted_fields')
BEGIN
    ALTER TABLE dbo.order_log ADD extracted_fields INT DEFAULT 0;
    PRINT 'Added extracted_fields column to order_log';
END

-- Create useful indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_orders_bol_number' AND object_id = OBJECT_ID('dbo.orders'))
BEGIN
    CREATE INDEX IX_orders_bol_number ON dbo.orders(bol_number);
    PRINT 'Created index on bol_number';
END

-- Check what we have now
SELECT 
    'orders' as TableName,
    COUNT(*) as ColumnCount
FROM sys.columns 
WHERE object_id = OBJECT_ID('dbo.orders')

UNION ALL

SELECT 
    'order_log' as TableName,
    COUNT(*) as ColumnCount
FROM sys.columns 
WHERE object_id = OBJECT_ID('dbo.order_log');

PRINT 'Database setup complete!';
