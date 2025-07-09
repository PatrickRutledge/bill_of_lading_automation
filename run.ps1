# Bill of Lading Automation Setup and Run Script
# This PowerShell script helps set up and run the BOL automation system

param(
    [string]$Action = "menu"
)

function Show-Menu {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Bill of Lading Automation System" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Install Python dependencies" -ForegroundColor Yellow
    Write-Host "2. Test BOL parsing (all PDFs)" -ForegroundColor Yellow
    Write-Host "3. Test BOL parsing (specific PDF)" -ForegroundColor Yellow
    Write-Host "4. Run the main automation script" -ForegroundColor Yellow
    Write-Host "5. View recent log entries" -ForegroundColor Yellow
    Write-Host "6. Open attachments folder" -ForegroundColor Yellow
    Write-Host "7. Exit" -ForegroundColor Yellow
    Write-Host ""
}

function Install-Dependencies {
    Write-Host "Installing Python dependencies..." -ForegroundColor Green
    if (Test-Path "requirements.txt") {
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt
        Write-Host "Dependencies installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Error: requirements.txt not found!" -ForegroundColor Red
    }
}

function Test-AllPDFs {
    Write-Host "Testing BOL parsing with all PDFs..." -ForegroundColor Green
    if (Test-Path "test_bol_parsing.py") {
        python test_bol_parsing.py
    } else {
        Write-Host "Error: test_bol_parsing.py not found!" -ForegroundColor Red
    }
}

function Test-SpecificPDF {
    $pdfPath = Read-Host "Enter the path to the PDF file"
    if (Test-Path $pdfPath) {
        Write-Host "Testing BOL parsing with $pdfPath..." -ForegroundColor Green
        python test_bol_parsing.py $pdfPath
    } else {
        Write-Host "Error: PDF file not found: $pdfPath" -ForegroundColor Red
    }
}

function Run-MainScript {
    Write-Host "Running the main automation script..." -ForegroundColor Green
    if (Test-Path "extract_and_insert.py") {
        python extract_and_insert.py
    } else {
        Write-Host "Error: extract_and_insert.py not found!" -ForegroundColor Red
    }
}

function Show-RecentLogs {
    Write-Host "Recent log entries:" -ForegroundColor Green
    if (Test-Path "order_log.csv") {
        $logs = Get-Content "order_log.csv" | Select-Object -Last 10
        $logs | ForEach-Object { Write-Host $_ }
    } else {
        Write-Host "No log file found. Run the automation script first." -ForegroundColor Yellow
    }
}

function Open-AttachmentsFolder {
    $attachmentsPath = "attachments"
    if (Test-Path $attachmentsPath) {
        Invoke-Item $attachmentsPath
        Write-Host "Opened attachments folder." -ForegroundColor Green
    } else {
        Write-Host "Attachments folder doesn't exist yet. It will be created when the script runs." -ForegroundColor Yellow
    }
}

# Main script logic
switch ($Action.ToLower()) {
    "install" { Install-Dependencies; return }
    "test" { Test-AllPDFs; return }
    "run" { Run-MainScript; return }
    "logs" { Show-RecentLogs; return }
    "menu" { 
        # Interactive menu
        do {
            Show-Menu
            $choice = Read-Host "Enter your choice (1-7)"
            
            switch ($choice) {
                "1" { Install-Dependencies }
                "2" { Test-AllPDFs }
                "3" { Test-SpecificPDF }
                "4" { Run-MainScript }
                "5" { Show-RecentLogs }
                "6" { Open-AttachmentsFolder }
                "7" { 
                    Write-Host "Goodbye!" -ForegroundColor Cyan
                    return 
                }
                default { 
                    Write-Host "Invalid choice. Please enter 1-7." -ForegroundColor Red 
                }
            }
            
            if ($choice -ne "7") {
                Write-Host ""
                Read-Host "Press Enter to continue"
                Clear-Host
            }
        } while ($choice -ne "7")
    }
    default {
        Write-Host "Usage:" -ForegroundColor Yellow
        Write-Host "  .\run.ps1                 # Interactive menu" -ForegroundColor White
        Write-Host "  .\run.ps1 -Action install # Install dependencies" -ForegroundColor White
        Write-Host "  .\run.ps1 -Action test    # Test BOL parsing" -ForegroundColor White
        Write-Host "  .\run.ps1 -Action run     # Run automation" -ForegroundColor White
        Write-Host "  .\run.ps1 -Action logs    # Show recent logs" -ForegroundColor White
    }
}
