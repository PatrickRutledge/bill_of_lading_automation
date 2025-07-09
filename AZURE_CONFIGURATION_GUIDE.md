# Azure Function App Configuration Guide

## Overview
This guide helps you configure the Azure Function App environment variables for the Bill of Lading automation system. These settings are already configured in the production environment but this guide serves as documentation.

## Important Security Notes

⚠️ **NEVER COMMIT ACTUAL CREDENTIALS TO GIT**

- This guide shows placeholder values only
- Actual credentials are stored securely in Azure environment variables
- Production environment variables are already configured
- For new deployments, replace placeholder values with your actual credentials

## Current Production Status

✅ **CONFIGURED AND RUNNING**

The production Azure Function App is currently configured and running:
- Function App: `bol-processor-func`
- Schedule: Daily at 9 AM UTC (`"0 0 9 * * *"`)
- All environment variables are properly set
- Database connection and processing confirmed working

## Step 1: Access Azure Portal
1. Go to https://portal.azure.com
2. Sign in with your Azure account

## Step 2: Navigate to Your Function App
1. In the search bar, type your Function App name (e.g., "bol-processor-func")
2. Click on your Function App

## Step 3: Configure Application Settings
1. In the left menu, click "Configuration"
2. Click "Application settings" tab
3. Click "New application setting" for each of the following:

### Required Application Settings:
Add these exact settings (one at a time):

**Name:** EMAIL_USER  
**Value:** [Your Gmail address]

**Name:** EMAIL_PASS  
**Value:** [Your Gmail App Password - NOT your regular Gmail password]

**Name:** REJECTION_EMAIL  
**Value:** [Fallback email address for failed processing notifications]

**Name:** AZURE_SERVER  
**Value:** [Your Azure SQL server name].database.windows.net

**Name:** AZURE_DATABASE  
**Value:** [Your Azure SQL database name]

**Name:** AZURE_USERNAME  
**Value:** [Your Azure SQL username]@[server-name]

**Name:** AZURE_PASSWORD  
**Value:** [Your Azure SQL password]

**Name:** AZURE_DRIVER  
**Value:** {ODBC Driver 18 for SQL Server}

## Step 4: Save Configuration
1. After adding all settings, click "Save" at the top
2. Click "Continue" when prompted about restarting the app

## Step 5: Test the Function
1. Go to "Functions" in the left menu
2. Click on "BolProcessor"
3. Click "Test/Run" to manually test the function
4. The function is also scheduled to run daily at 9:00 AM UTC

## Deployment Summary
✅ **Resource Group:** emailpdf-2-sql-rg  
✅ **Function App:** emailpdf-2-sql  
✅ **Storage Account:** emailpdf2sqlstorage  
✅ **Function Code:** Successfully deployed  
✅ **Schedule:** Daily at 9:00 AM UTC (0 0 9 * * *)

## Monitoring
- View logs in Azure Portal: Functions → BolProcessor → Monitor
- Check Application Insights for detailed telemetry
- Monitor database: Use Azure Data Studio to check dbo.orders and dbo.order_log tables

## Next Steps
1. Configure the application settings above
2. Test the function manually
3. Send a test email with a PDF attachment to verify end-to-end functionality
4. Monitor the logs to ensure everything is working correctly
