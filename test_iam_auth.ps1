# Test IBM Cloud IAM Authentication
# This script tests the IAM token generation for watsonx.ai

# Set your API key (replace with actual key)
$env:WATSONX_API_KEY = "YOUR_API_KEY_HERE"

# Create the request body as a hashtable (PowerShell will properly encode it)
$body = @{
    grant_type = "urn:ibm:params:oauth:grant-type:apikey"
    apikey = $env:WATSONX_API_KEY
}

try {
    Write-Host "Requesting IAM token..." -ForegroundColor Cyan
    
    # Make the API call
    $response = Invoke-RestMethod `
        -Uri "https://iam.cloud.ibm.com/identity/token" `
        -Method POST `
        -ContentType "application/x-www-form-urlencoded" `
        -Body $body
    
    Write-Host "✓ Token obtained successfully!" -ForegroundColor Green
    Write-Host "Token preview: $($response.access_token.Substring(0, 20))..." -ForegroundColor Green
    Write-Host "Token type: $($response.token_type)" -ForegroundColor Gray
    Write-Host "Expires in: $($response.expires_in) seconds" -ForegroundColor Gray
}
catch {
    Write-Host "✗ Failed to obtain IAM token" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    # Try to parse and display the error response
    if ($_.ErrorDetails.Message) {
        $errorJson = $_.ErrorDetails.Message | ConvertFrom-Json
        Write-Host ("Error Code: " + $errorJson.errorCode) -ForegroundColor Yellow
        Write-Host ("Error Message: " + $errorJson.errorMessage) -ForegroundColor Yellow
        Write-Host ("Error Details: " + $errorJson.errorDetails) -ForegroundColor Yellow
    }
}

# Made with Bob
