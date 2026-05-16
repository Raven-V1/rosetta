# Rosetta Setup Guide

This guide covers **local development setup**. For cloud deployment instructions, see the **[Deployment Guide](DEPLOYMENT.md)**.

---

## Overview

Rosetta requires IBM watsonx.ai credentials to generate AI-powered database documentation. The setup process differs depending on your environment:

- **Local Development**: Use `.env` file or system environment variables
- **Streamlit Cloud**: Use Streamlit secrets management (see [Deployment Guide](DEPLOYMENT.md))

### Required Credentials

1. **`WATSONX_API_KEY`** - Your IBM Cloud API key for authentication
2. **`WATSONX_PROJECT_ID`** - Your watsonx.ai project ID

---

## Local Development Setup

### 1. Obtain IBM Cloud API Key

1. Log in to [IBM Cloud](https://cloud.ibm.com)
2. Navigate to **Manage** → **Access (IAM)** → **API keys**
3. Click **Create an IBM Cloud API key**
4. Give it a descriptive name (e.g., "Rosetta watsonx.ai")
5. Click **Create**
6. **Important**: Copy and save the API key immediately - you won't be able to see it again!

### 2. Obtain watsonx.ai Project ID

1. Log in to [IBM watsonx.ai](https://dataplatform.cloud.ibm.com/projects/?context=wx)
2. Select or create a project for Rosetta
3. In your project, click **Manage** (tab at the top)
4. Click **General** in the left sidebar
5. Find **Project ID** and copy the value

### 3. Configure Environment Variables

Choose the configuration method that best suits your development workflow:

#### Option A: Using a `.env` file (Recommended for local development)

1. In the Rosetta project root directory, create a file named `.env`
2. Copy the contents from `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and replace the placeholder values:
   ```
   WATSONX_API_KEY=your_actual_api_key_here
   WATSONX_PROJECT_ID=your_actual_project_id_here
   ```
4. Save the file

**Note**: The `.env` file is already in `.gitignore` and will not be committed to version control.

#### Option A-Alt: Using Streamlit Secrets (Local development with Streamlit)

1. In the `.streamlit/` directory, create a file named `secrets.toml`
2. Copy the template from `.streamlit/secrets.toml.example`:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
3. Edit `.streamlit/secrets.toml` and replace the placeholder values:
   ```toml
   WATSONX_API_KEY = "your_actual_api_key_here"
   WATSONX_PROJECT_ID = "your_actual_project_id_here"
   ```
4. Save the file

**Note**: The `secrets.toml` file is already in `.gitignore` and will not be committed to version control.

#### Option B: Using System Environment Variables (Windows)

1. Open **System Properties** → **Environment Variables**
2. Under **User variables**, click **New**
3. Add both variables:
   - Variable name: `WATSONX_API_KEY`
   - Variable value: Your IBM Cloud API key
   - Variable name: `WATSONX_PROJECT_ID`
   - Variable value: Your watsonx.ai project ID
4. Click **OK** to save

#### Option C: Using PowerShell (Temporary - current session only)

```powershell
$env:WATSONX_API_KEY="your_actual_api_key_here"
$env:WATSONX_PROJECT_ID="your_actual_project_id_here"
```

#### Option D: Using Streamlit Secrets (For Streamlit Cloud deployment)

**For cloud deployment**, secrets are configured through the Streamlit Cloud dashboard, not locally.

See the **[Deployment Guide](DEPLOYMENT.md)** for complete instructions on:
- Deploying to Streamlit Community Cloud
- Configuring secrets in the cloud dashboard
- Database connectivity options
- Troubleshooting deployment issues

---

## Verification

After configuring the environment variables:

1. **Restart the Streamlit application** (if it's already running)
   - Stop the current process (Ctrl+C)
   - Start it again: `streamlit run app.py`

2. **Test the configuration**:
   - Navigate to the application
   - Connect to a database
   - Try generating AI-powered documentation
   - If configured correctly, you should see generated content instead of errors

---

## Troubleshooting

### Error: "WATSONX_API_KEY environment variable is not set"

**Solution**: The API key is not configured or not accessible to the application.
- Verify the environment variable is set correctly
- If using a `.env` file, ensure it's in the project root directory
- Restart the Streamlit application after setting environment variables

### Error: "WATSONX_PROJECT_ID environment variable is not set"

**Solution**: The project ID is not configured or not accessible to the application.
- Verify the environment variable is set correctly
- Double-check you copied the correct Project ID from watsonx.ai
- Restart the Streamlit application after setting environment variables

### Error: "Invalid IBM Cloud API key"

**Solution**: The API key is incorrect or has been revoked.
- Verify you copied the entire API key correctly (no extra spaces)
- Try creating a new API key in IBM Cloud
- Ensure the API key has the necessary permissions for watsonx.ai

### Error: "Forbidden: Access denied to watsonx.ai"

**Solution**: Your API key doesn't have access to the specified project.
- Verify the Project ID is correct
- Ensure your IBM Cloud account has access to the watsonx.ai project
- Check that the project exists and is active

### Error: "Not found: Invalid watsonx.ai project ID"

**Solution**: The project ID is incorrect or the project doesn't exist.
- Double-check the Project ID from watsonx.ai
- Ensure you're using the Project ID, not the project name
- Verify the project hasn't been deleted

---

## Security Best Practices

1. **Never commit credentials to version control**
   - The `.env` file is already in `.gitignore`
   - Never hardcode API keys in source code

2. **Rotate API keys regularly**
   - Create new API keys periodically
   - Delete old/unused API keys from IBM Cloud

3. **Use separate credentials for different environments**
   - Development: Personal API key
   - Production: Service account API key with minimal permissions

4. **Protect your `.env` file**
   - Set appropriate file permissions
   - Don't share it via email or messaging apps

---

## Cloud Deployment

For deploying Rosetta to Streamlit Community Cloud, please refer to the comprehensive **[Deployment Guide](DEPLOYMENT.md)**.

### Key Differences: Local vs Cloud

| Aspect | Local Development | Cloud Deployment |
|--------|------------------|------------------|
| **Secrets Management** | `.env` file or `secrets.toml` | Streamlit Cloud dashboard |
| **Configuration Files** | Local files in project | Committed to Git repository |
| **Database Access** | Direct connection | Requires firewall configuration |
| **Environment** | Your local machine | Streamlit Cloud infrastructure |
| **Updates** | Manual restart | Automatic on Git push |

### Quick Cloud Setup

1. **Push code to GitHub** (ensure `.env` and `secrets.toml` are NOT committed)
2. **Deploy to Streamlit Cloud** - See [Deployment Guide](DEPLOYMENT.md)
3. **Configure secrets** in Streamlit Cloud dashboard using `.streamlit/secrets.toml.example` as template
4. **Test the deployment** - Verify watsonx.ai integration works

### Important Notes for Cloud Deployment

- ✅ **DO commit**: `requirements.txt`, `packages.txt`, `.streamlit/config.toml`, `.streamlit/secrets.toml.example`
- ❌ **DO NOT commit**: `.env`, `.streamlit/secrets.toml`, any files with actual credentials
- 🔒 **Security**: Always use the Streamlit Cloud secrets dashboard for credentials
- 📖 **Full Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md) for complete step-by-step instructions

---

## Additional Resources

- [IBM Cloud API Keys Documentation](https://cloud.ibm.com/docs/account?topic=account-userapikey)
- [IBM watsonx.ai Documentation](https://dataplatform.cloud.ibm.com/docs/content/wsj/getting-started/welcome-main.html)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

---

## Need Help?

If you continue to experience issues:
1. Check the application logs for detailed error messages
2. Verify your IBM Cloud account has active watsonx.ai access
3. Ensure you're using the correct region (US-South is default)
4. Contact IBM Cloud support for account-specific issues