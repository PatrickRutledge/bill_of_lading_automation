-- Fix missing columns in dbo.orders table
-- Run this in Azure Data Studio to add the missing created_date column

-- Add created_date column if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'created_date')
BEGIN
    ALTER TABLE dbo.orders ADD created_date DATETIME2 DEFAULT GETDATE();
    PRINT 'Added created_date column';
END
ELSE
BEGIN
    PRINT 'created_date column already exists';
END

-- Add updated_date column if it doesn't exist (this should already exist from previous script)
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'updated_date')
BEGIN
    ALTER TABLE dbo.orders ADD updated_date DATETIME2 DEFAULT GETDATE();
    PRINT 'Added updated_date column';
END
ELSE
BEGIN
    PRINT 'updated_date column already exists';
END

-- Add raw_text column if it doesn't exist (for storing the full PDF text)
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.orders') AND name = 'raw_text')
BEGIN
    ALTER TABLE dbo.orders ADD raw_text NVARCHAR(MAX);
    PRINT 'Added raw_text column';
END
ELSE
BEGIN
    PRINT 'raw_text column already exists';
END

-- Verify all required columns exist
SELECT 
    c.name as ColumnName,
    t.name as DataType,
    c.max_length,
    c.is_nullable
FROM sys.columns c
INNER JOIN sys.types t ON c.user_type_id = t.user_type_id
WHERE c.object_id = OBJECT_ID('dbo.orders')
    AND c.name IN ('bol_number', 'shipper_name', 'shipper_address', 'consignee_name', 
                   'consignee_address', 'carrier_name', 'shipment_date', 'delivery_date',
                   'origin_city', 'destination_city', 'total_weight', 'total_pieces',
                   'freight_charges', 'commodity_description', 'reference_number', 
                   'raw_text', 'created_date', 'updated_date')
ORDER BY c.name;

PRINT 'Column verification complete!';
