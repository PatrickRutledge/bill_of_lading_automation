-- Modifications for existing Bill of Lading database
-- Run this in Azure Data Studio to add missing components

-- 1. Create BillOfLadingData table if it doesn't exist
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='BillOfLadingData' AND xtype='U')
BEGIN
    CREATE TABLE dbo.BillOfLadingData (
        id INT IDENTITY(1,1) PRIMARY KEY,
        bol_number NVARCHAR(100),
        shipper_name NVARCHAR(255),
        shipper_address NVARCHAR(500),
        consignee_name NVARCHAR(255),
        consignee_address NVARCHAR(500),
        carrier_name NVARCHAR(255),
        shipment_date NVARCHAR(50),
        delivery_date NVARCHAR(50),
        origin_city NVARCHAR(255),
        destination_city NVARCHAR(255),
        total_weight FLOAT,
        total_pieces INT,
        freight_charges FLOAT,
        commodity_description NVARCHAR(500),
        reference_number NVARCHAR(100),
        raw_text NVARCHAR(MAX),
        created_date DATETIME2 DEFAULT GETDATE(),
        updated_date DATETIME2 DEFAULT GETDATE()
    );
    PRINT 'Created BillOfLadingData table';
END
ELSE
BEGIN
    PRINT 'BillOfLadingData table already exists';
END

-- 2. Add extracted_fields column to order_log if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.order_log') AND name = 'extracted_fields')
BEGIN
    ALTER TABLE dbo.order_log ADD extracted_fields INT DEFAULT 0;
    PRINT 'Added extracted_fields column to order_log table';
END
ELSE
BEGIN
    PRINT 'order_log table already has extracted_fields column';
END

-- 3. Create useful indexes for performance
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_BillOfLadingData_bol_number' AND object_id = OBJECT_ID('dbo.BillOfLadingData'))
BEGIN
    CREATE INDEX IX_BillOfLadingData_bol_number ON dbo.BillOfLadingData(bol_number);
    PRINT 'Created index on bol_number';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_BillOfLadingData_created_date' AND object_id = OBJECT_ID('dbo.BillOfLadingData'))
BEGIN
    CREATE INDEX IX_BillOfLadingData_created_date ON dbo.BillOfLadingData(created_date);
    PRINT 'Created index on created_date';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_order_log_log_timestamp' AND object_id = OBJECT_ID('dbo.order_log'))
BEGIN
    CREATE INDEX IX_order_log_log_timestamp ON dbo.order_log(log_timestamp);
    PRINT 'Created index on log_timestamp';
END

-- 4. Show current table status
PRINT 'Checking current table status...';

SELECT 
    'BillOfLadingData' as TableName,
    COUNT(*) as ColumnCount
FROM sys.columns 
WHERE object_id = OBJECT_ID('dbo.BillOfLadingData')

UNION ALL

SELECT 
    'order_log' as TableName,
    COUNT(*) as ColumnCount
FROM sys.columns 
WHERE object_id = OBJECT_ID('dbo.order_log')

UNION ALL

SELECT 
    'orders' as TableName,
    COUNT(*) as ColumnCount
FROM sys.columns 
WHERE object_id = OBJECT_ID('dbo.orders');

PRINT 'Database modifications complete!';
