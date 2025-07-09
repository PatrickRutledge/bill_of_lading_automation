# Azure Deployment Guide

This guide will help you deploy the Bill of Lading automation to Azure Functions.

## Prerequisites

1. **Azure Subscription** with access to:
   - Azure Functions
   - Azure SQL Database (must be set up first)
   - App Service plan (Consumption or Premium)

2. **Azure CLI** installed on your local machine
   - Download from: https://aka.ms/installazurecliwindows

3. **Azure Functions Core Tools** installed
   ```powershell
   npm install -g azure-functions-core-tools@4 --unsafe-perm true
   ```

4. **Database Setup** - Run the database setup script first:
   - Connect to your Azure SQL Database using Azure Data Studio or SQL Server Management Studio
   - Run `database_setup_complete.sql` (this replaces all the individual SQL files)
   - This script is safe to run multiple times and will create all necessary tables and columns

## Step 1: Install Azure CLI and Login

```powershell
# Install Azure CLI (if not already installed)
# Download from: https://aka.ms/installazurecliwindows

# Login to Azure
az login

# Set your subscription (if you have multiple)
az account set --subscription "Your Subscription Name"
```

## Step 2: Create Azure Resources

```powershell
# Set variables (replace with your values)
$resourceGroup = "bill-of-lading-rg"
$functionAppName = "bol-processor-app"  # Must be globally unique
$storageAccount = "bolprocessorstorage"  # Must be globally unique
$location = "eastus"

# Create resource group (if it doesn't exist)
az group create --name $resourceGroup --location $location

# Create storage account for the function app
az storage account create --name $storageAccount --location $location --resource-group $resourceGroup --sku Standard_LRS

# Create the function app
az functionapp create --resource-group $resourceGroup --consumption-plan-location $location --runtime python --runtime-version 3.9 --functions-version 4 --name $functionAppName --storage-account $storageAccount
```

## Step 3: Configure Application Settings

Set up environment variables in Azure that will replace your local `config.py`:

```powershell
# Set the function app name variable
$functionAppName = "bol-processor-app"  # Replace with your actual function app name
$resourceGroup = "bill-of-lading-rg"   # Replace with your resource group

# Configure Gmail settings
az functionapp config appsettings set --name $functionAppName --resource-group $resourceGroup --settings "EMAIL_USER=your_email@gmail.com"
az functionapp config appsettings set --name $functionAppName --resource-group $resourceGroup --settings "EMAIL_PASS=your_gmail_app_password"
az functionapp config appsettings set --name $functionAppName --resource-group $resourceGroup --settings "REJECTION_EMAIL=your_fallback@email.com"

# Configure Azure SQL settings
az functionapp config appsettings set --name $functionAppName --resource-group $resourceGroup --settings "AZURE_SERVER=your_server.database.windows.net"
az functionapp config appsettings set --name $functionAppName --resource-group $resourceGroup --settings "AZURE_DATABASE=OrderEntry"
az functionapp config appsettings set --name $functionAppName --resource-group $resourceGroup --settings "AZURE_USERNAME=your_username@your_server.database.windows.net"
az functionapp config appsettings set --name $functionAppName --resource-group $resourceGroup --settings "AZURE_PASSWORD=your_database_password"

# Configure other settings
az functionapp config appsettings set --name $functionAppName --resource-group $resourceGroup --settings "AZURE_DRIVER={ODBC Driver 18 for SQL Server}"
```

## Step 4: Deploy the Function

```powershell
# Navigate to your project directory
cd c:\Users\PatRutledge\bill_of_lading_automation

# Deploy the function
func azure functionapp publish $functionAppName
```

## Step 5: Configure Function Schedule

The function is configured to run daily at 9:00 AM UTC. You can modify this in `BolProcessor/function.json`:

```json
{
  "schedule": "0 0 9 * * *"  // Daily at 9:00 AM UTC
}
```

Common cron expressions:
- `"0 */30 * * * *"` - Every 30 minutes
- `"0 0 */2 * * *"` - Every 2 hours
- `"0 0 6,12,18 * * *"` - At 6 AM, 12 PM, and 6 PM UTC

## Step 6: Monitor and Test

### View Logs
```powershell
# Stream logs in real-time
func azure functionapp logstream $functionAppName

# Or view logs in Azure Portal:
# 1. Go to your Function App in Azure Portal
# 2. Navigate to Functions > BolProcessor
# 3. Click on "Monitor" tab
```

### Test the Function
```powershell
# Trigger the function manually for testing
az functionapp function invoke --resource-group $resourceGroup --name $functionAppName --function-name BolProcessor
```

### Check Application Settings
```powershell
# List all application settings
az functionapp config appsettings list --name $functionAppName --resource-group $resourceGroup --output table
```

## Security Best Practices

1. **Enable Authentication** (if needed for webhook access)
2. **Use Key Vault** for sensitive secrets (optional upgrade)
3. **Enable Application Insights** for better monitoring
4. **Set up alerts** for function failures

## Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure all dependencies are in `requirements_azure.txt`
2. **Connection Errors**: Verify SQL Server firewall allows Azure services
3. **Authentication Errors**: Check Gmail App Password and Azure SQL credentials
4. **Timeout Errors**: Consider upgrading to Premium plan for longer execution time

### Debug Commands:
```powershell
# Check function status
az functionapp show --name $functionAppName --resource-group $resourceGroup --query "state"

# View recent function executions
az functionapp logs tail --name $functionAppName --resource-group $resourceGroup
```

## Local Testing with Azure Configuration

To test the Azure version locally:

```powershell
# Set environment variables for local testing
$env:EMAIL_USER="your_email@gmail.com"
$env:EMAIL_PASS="your_app_password"
$env:REJECTION_EMAIL="your_fallback@email.com"
$env:AZURE_SERVER="your_server.database.windows.net"
$env:AZURE_DATABASE="OrderEntry"
$env:AZURE_USERNAME="your_username@your_server.database.windows.net"
$env:AZURE_PASSWORD="your_password"

# Run the Azure version locally
python extract_and_insert_azure.py
```

## Next Steps

After successful deployment:

1. **Monitor** the function for a few days
2. **Set up alerts** for failures
3. **Consider** setting up a backup local scheduler
4. **Review** and optimize the cron schedule based on your email patterns
