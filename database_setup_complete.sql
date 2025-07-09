-- ====================================================================
-- Bill of Lading Automation - Complete Database Setup Script
-- ====================================================================
-- This script sets up all necessary tables and columns for the BOL automation
-- Run this script on a fresh Azure SQL Database OR on an existing database
-- It's safe to run multiple times (uses IF NOT EXISTS checks)
-- ====================================================================

USE [OrderEntry];  -- Replace with your database name if different
GO

PRINT '====================================================================';
PRINT 'Starting Bill of Lading Automation Database Setup';
PRINT 'Script will create/modify tables: dbo.orders, dbo.order_log';
PRINT '====================================================================';

-- ====================================================================
-- 1. CREATE OR MODIFY dbo.orders TABLE
-- ====================================================================

-- Create the orders table if it doesn't exist
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='orders' AND xtype='U')
BEGIN
    PRINT 'Creating new dbo.orders table...';
    
    CREATE TABLE dbo.orders (
        id INT IDENTITY(1,1) PRIMARY KEY,
        
        -- BOL/Shipping Fields
        bol_number NVARCHAR(100),
        shipper_name NVARCHAR(255),
        shipper_address NVARCHAR(500),
        consignee_name NVARCHAR(255),
        consignee_address NVARCHAR(500),
        carrier_name NVARCHAR(255),
        shipment_date NVARCHAR(50),          -- String format for flexible date parsing
        delivery_date NVARCHAR(50),          -- String format for flexible date parsing
        origin_city NVARCHAR(255),
        destination_city NVARCHAR(255),
        total_weight FLOAT,
        total_pieces INT,
        freight_charges FLOAT,
        commodity_description NVARCHAR(500),
        reference_number NVARCHAR(100),
        
        -- Metadata Fields
        raw_text NVARCHAR(MAX),              -- Full PDF text for reference
        created_date DATETIME2 DEFAULT GETDATE(),
        updated_date DATETIME2 DEFAULT GETDATE()
    );
    
    PRINT 'Successfully created dbo.orders table with all BOL columns';
END
ELSE
BEGIN
    PRINT 'dbo.orders table already exists - checking for missing columns...';
    
    -- Add BOL columns if they don't exist
    DECLARE @columns_added INT = 0;
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'bol_number')
    BEGIN
        ALTER TABLE dbo.orders ADD bol_number NVARCHAR(100);
        PRINT '  + Added bol_number column';
        SET @columns_added = @columns_added + 1;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'shipper_name')
    BEGIN
        ALTER TABLE dbo.orders ADD shipper_name NVARCHAR(255);
        PRINT '  + Added shipper_name column';
        SET @columns_added = @columns_added + 1;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'shipper_address')
    BEGIN
        ALTER TABLE dbo.orders ADD shipper_address NVARCHAR(500);
        PRINT '  + Added shipper_address column';
        SET @columns_added = @columns_added + 1;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'consignee_name')
    BEGIN
        ALTER TABLE dbo.orders ADD consignee_name NVARCHAR(255);
        PRINT '  + Added consignee_name column';
        SET @columns_added = @columns_added + 1;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'consignee_address')
    BEGIN
        ALTER TABLE dbo.orders ADD consignee_address NVARCHAR(500);
        PRINT '  + Added consignee_address column';
        SET @columns_added = @columns_added + 1;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'carrier_name')
    BEGIN
        ALTER TABLE dbo.orders ADD carrier_name NVARCHAR(255);
        PRINT '  + Added carrier_name column';
        SET @columns_added = @columns_added + 1;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'shipment_date')
    BEGIN
        ALTER TABLE dbo.orders ADD shipment_date NVARCHAR(50);
        PRINT '  + Added shipment_date column';
        SET @columns_added = @columns_added + 1;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'delivery_date')
    BEGIN
        ALTER TABLE dbo.orders ADD delivery_date NVARCHAR(50);
        PRINT '  + Added delivery_date column';
        SET @columns_added = @columns_added + 1;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'origin_city')
    BEGIN
        ALTER TABLE dbo.orders ADD origin_city NVARCHAR(255);
        PRINT '  + Added origin_city column';
        SET @columns_added = @columns_added + 1;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'destination_city')
    BEGIN
        ALTER TABLE dbo.orders ADD destination_city NVARCHAR(255);
        PRINT '  + Added destination_city column';
        SET @columns_added = @columns_added + 1;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'total_weight')
    BEGIN
        ALTER TABLE dbo.orders ADD total_weight FLOAT;
        PRINT '  + Added total_weight column';
        SET @columns_added = @columns_added + 1;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'total_pieces')
    BEGIN
        ALTER TABLE dbo.orders ADD total_pieces INT;
        PRINT '  + Added total_pieces column';
        SET @columns_added = @columns_added + 1;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'freight_charges')
    BEGIN
        ALTER TABLE dbo.orders ADD freight_charges FLOAT;
        PRINT '  + Added freight_charges column';
        SET @columns_added = @columns_added + 1;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'commodity_description')
    BEGIN
        ALTER TABLE dbo.orders ADD commodity_description NVARCHAR(500);
        PRINT '  + Added commodity_description column';
        SET @columns_added = @columns_added + 1;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'reference_number')
    BEGIN
        ALTER TABLE dbo.orders ADD reference_number NVARCHAR(100);
        PRINT '  + Added reference_number column';
        SET @columns_added = @columns_added + 1;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'raw_text')
    BEGIN
        ALTER TABLE dbo.orders ADD raw_text NVARCHAR(MAX);
        PRINT '  + Added raw_text column';
        SET @columns_added = @columns_added + 1;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'created_date')
    BEGIN
        ALTER TABLE dbo.orders ADD created_date DATETIME2 DEFAULT GETDATE();
        PRINT '  + Added created_date column';
        SET @columns_added = @columns_added + 1;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'updated_date')
    BEGIN
        ALTER TABLE dbo.orders ADD updated_date DATETIME2 DEFAULT GETDATE();
        PRINT '  + Added updated_date column';
        SET @columns_added = @columns_added + 1;
    END
    
    IF @columns_added = 0
    BEGIN
        PRINT '  ✓ All BOL columns already exist in dbo.orders table';
    END
    ELSE
    BEGIN
        PRINT '  ✓ Added ' + CAST(@columns_added AS NVARCHAR(10)) + ' missing columns to dbo.orders table';
    END
END

-- ====================================================================
-- 2. CREATE OR MODIFY dbo.order_log TABLE
-- ====================================================================

-- Create the order_log table if it doesn't exist
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='order_log' AND xtype='U')
BEGIN
    PRINT 'Creating new dbo.order_log table...';
    
    CREATE TABLE dbo.order_log (
        id INT IDENTITY(1,1) PRIMARY KEY,
        email_from NVARCHAR(255),
        email_subject NVARCHAR(500),
        attachment_name NVARCHAR(255),
        status NVARCHAR(50),                 -- 'processed' or 'rejected'
        log_timestamp DATETIME2 DEFAULT GETDATE(),
        error_message NVARCHAR(MAX),
        extracted_fields INT DEFAULT 0       -- Count of successfully extracted fields
    );
    
    PRINT 'Successfully created dbo.order_log table';
END
ELSE
BEGIN
    PRINT 'dbo.order_log table already exists - checking for missing columns...';
    
    -- Add extracted_fields column if it doesn't exist
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.order_log') AND name = 'extracted_fields')
    BEGIN
        ALTER TABLE dbo.order_log ADD extracted_fields INT DEFAULT 0;
        PRINT '  + Added extracted_fields column to order_log table';
    END
    ELSE
    BEGIN
        PRINT '  ✓ order_log table already has all required columns';
    END
END

-- ====================================================================
-- 3. CREATE INDEXES FOR PERFORMANCE (Optional but recommended)
-- ====================================================================

PRINT 'Creating performance indexes...';

-- Index on bol_number for quick lookups
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'IX_orders_bol_number')
BEGIN
    CREATE INDEX IX_orders_bol_number ON dbo.orders(bol_number);
    PRINT '  + Created index on dbo.orders.bol_number';
END

-- Index on created_date for date-based queries
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'IX_orders_created_date')
BEGIN
    CREATE INDEX IX_orders_created_date ON dbo.orders(created_date);
    PRINT '  + Created index on dbo.orders.created_date';
END

-- Index on order_log timestamp for monitoring queries
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID('dbo.order_log') AND name = 'IX_order_log_timestamp')
BEGIN
    CREATE INDEX IX_order_log_timestamp ON dbo.order_log(log_timestamp);
    PRINT '  + Created index on dbo.order_log.log_timestamp';
END

-- ====================================================================
-- 4. VERIFICATION AND SUMMARY
-- ====================================================================

PRINT '====================================================================';
PRINT 'Database Setup Complete - Verification Summary:';
PRINT '====================================================================';

-- Check orders table
DECLARE @orders_columns INT;
SELECT @orders_columns = COUNT(*) 
FROM sys.columns 
WHERE object_id = OBJECT_ID('dbo.orders') 
AND name IN ('bol_number', 'shipper_name', 'consignee_name', 'carrier_name', 
             'shipment_date', 'delivery_date', 'total_weight', 'total_pieces',
             'freight_charges', 'commodity_description', 'reference_number', 'raw_text');

PRINT 'dbo.orders table: ' + CAST(@orders_columns AS NVARCHAR(10)) + '/12 BOL columns present';

-- Check order_log table
IF EXISTS (SELECT * FROM sysobjects WHERE name='order_log' AND xtype='U')
BEGIN
    PRINT 'dbo.order_log table: ✓ Present and ready for logging';
END

-- Show table row counts (if any data exists)
DECLARE @orders_count INT, @log_count INT;
SELECT @orders_count = COUNT(*) FROM dbo.orders;
SELECT @log_count = COUNT(*) FROM dbo.order_log;

PRINT 'Current data: ' + CAST(@orders_count AS NVARCHAR(10)) + ' orders, ' + CAST(@log_count AS NVARCHAR(10)) + ' log entries';

PRINT '====================================================================';
PRINT 'Setup complete! The database is ready for BOL automation.';
PRINT 'You can now run the extract_and_insert.py script.';
PRINT '====================================================================';

GO
