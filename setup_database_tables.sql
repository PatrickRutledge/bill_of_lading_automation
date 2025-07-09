-- Bill of Lading Automation Database Setup Script
-- Run this script on your Azure SQL Database to create the necessary tables

-- Create the BillOfLadingData table
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
        shipment_date NVARCHAR(50),  -- Storing as string initially, can convert to DATE later
        delivery_date NVARCHAR(50),  -- Storing as string initially, can convert to DATE later
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

-- Update the order_log table to include extracted_fields column if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.order_log') AND name = 'extracted_fields')
BEGIN
    ALTER TABLE dbo.order_log ADD extracted_fields INT DEFAULT 0;
    PRINT 'Added extracted_fields column to order_log table';
END
ELSE
BEGIN
    PRINT 'order_log table already has extracted_fields column';
END

-- Create the order_log table if it doesn't exist
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='order_log' AND xtype='U')
BEGIN
    CREATE TABLE dbo.order_log (
        id INT IDENTITY(1,1) PRIMARY KEY,
        email_from NVARCHAR(255),
        email_subject NVARCHAR(500),
        attachment_name NVARCHAR(255),
        status NVARCHAR(50),
        log_timestamp DATETIME2,
        error_message NVARCHAR(MAX),
        extracted_fields INT DEFAULT 0
    );
    PRINT 'Created order_log table';
END
ELSE
BEGIN
    PRINT 'order_log table already exists';
END

-- Create the orders table if it doesn't exist (for legacy support)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='orders' AND xtype='U')
BEGIN
    CREATE TABLE dbo.orders (
        id INT IDENTITY(1,1) PRIMARY KEY,
        raw_text NVARCHAR(MAX),
        created_date DATETIME2 DEFAULT GETDATE()
    );
    PRINT 'Created orders table';
END
ELSE
BEGIN
    PRINT 'orders table already exists';
END

-- Create indexes for better performance
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_BillOfLadingData_bol_number')
BEGIN
    CREATE INDEX IX_BillOfLadingData_bol_number ON dbo.BillOfLadingData(bol_number);
    PRINT 'Created index on bol_number';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_BillOfLadingData_created_date')
BEGIN
    CREATE INDEX IX_BillOfLadingData_created_date ON dbo.BillOfLadingData(created_date);
    PRINT 'Created index on created_date';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_order_log_log_timestamp')
BEGIN
    CREATE INDEX IX_order_log_log_timestamp ON dbo.order_log(log_timestamp);
    PRINT 'Created index on log_timestamp';
END

PRINT 'Database setup complete!';
