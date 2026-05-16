# Rosetta Deployment Guide

Complete guide for deploying Rosetta to Streamlit Community Cloud.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Step-by-Step Deployment](#step-by-step-deployment)
- [Secrets Configuration](#secrets-configuration)
- [Database Connectivity](#database-connectivity)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)
- [Cost Information](#cost-information)
- [Maintenance and Updates](#maintenance-and-updates)

---

## Prerequisites

Before deploying Rosetta to Streamlit Community Cloud, ensure you have:

### Required Accounts
- **GitHub Account** - Your code must be in a GitHub repository
- **Streamlit Community Cloud Account** - Free account at [share.streamlit.io](https://share.streamlit.io)
- **IBM Cloud Account** - For watsonx.ai API access

### Required Credentials
- **IBM Cloud API Key** - For watsonx.ai authentication
- **watsonx.ai Project ID** - Your watsonx.ai project identifier

### Repository Requirements
- All code pushed to a GitHub repository (public or private)
- Configuration files in place:
  - `requirements.txt` - Python dependencies
  - `packages.txt` - System packages (ODBC drivers)
  - `.streamlit/config.toml` - Streamlit configuration
  - `.streamlit/secrets.toml.example` - Secrets template

---

## Quick Start

For experienced users, here's the condensed deployment process:

1. Push your code to GitHub
2. Sign in to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app" → Select your repository
4. Configure secrets in App Settings → Secrets
5. Deploy!

For detailed instructions, continue reading below.

---

## Step-by-Step Deployment

### Step 1: Prepare Your GitHub Repository

1. **Ensure all files are committed**:
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Verify required files exist**:
   - ✅ `app.py` - Main application file
   - ✅ `requirements.txt` - Python dependencies
   - ✅ `packages.txt` - System packages
   - ✅ `.streamlit/config.toml` - Streamlit configuration
   - ✅ `.streamlit/secrets.toml.example` - Secrets template (not the actual secrets!)

3. **Important**: Do NOT commit `.streamlit/secrets.toml` or `.env` files containing actual credentials!

### Step 2: Create Streamlit Community Cloud Account

1. Navigate to [share.streamlit.io](https://share.streamlit.io)
2. Click **Sign up** or **Sign in with GitHub**
3. Authorize Streamlit to access your GitHub account
4. Complete the account setup process

### Step 3: Deploy Your Application

1. **From the Streamlit Cloud dashboard**:
   - Click the **"New app"** button in the top-right corner

2. **Configure deployment settings**:
   - **Repository**: Select your GitHub repository (e.g., `username/rosetta`)
   - **Branch**: Choose your deployment branch (typically `main` or `master`)
   - **Main file path**: Enter `app.py`
   - **App URL**: Choose a custom subdomain (e.g., `rosetta-yourname`)

3. **Advanced settings** (optional):
   - **Python version**: Leave as default (3.9+) unless you need a specific version
   - **Secrets**: We'll configure this in the next step

4. Click **"Deploy!"**

   The initial deployment will fail because secrets are not configured yet. This is expected!

### Step 4: Configure Application Secrets

This is the most critical step for Rosetta to function properly.

1. **Access the app settings**:
   - From your app's page, click the **"⋮"** menu (three dots) in the bottom-right
   - Select **"Settings"**

2. **Navigate to Secrets**:
   - In the settings modal, click the **"Secrets"** tab

3. **Add your secrets**:
   Copy the template from `.streamlit/secrets.toml.example` and fill in your actual values:

   ```toml
   # IBM WatsonX AI Configuration
   WATSONX_API_KEY = "your-actual-watsonx-api-key-here"
   WATSONX_PROJECT_ID = "your-actual-watsonx-project-id-here"
   ```

4. **Optional: Add database configuration** (if using SQL Server):
   ```toml
   [connections.sqlserver]
   server = "your-server.database.windows.net"
   database = "your-database-name"
   username = "your-username"
   password = "your-password"
   driver = "ODBC Driver 17 for SQL Server"
   ```

5. **Save the secrets**:
   - Click **"Save"**
   - The app will automatically restart with the new configuration

### Step 5: Verify Deployment

1. **Wait for the app to restart** (usually 30-60 seconds)

2. **Test the application**:
   - Navigate to your app URL (e.g., `https://rosetta-yourname.streamlit.app`)
   - Verify the app loads without errors
   - Test database connection (demo mode should work immediately)
   - Test AI-powered features to confirm watsonx.ai integration

3. **Check the logs** (if issues occur):
   - Click **"Manage app"** → **"Logs"**
   - Look for error messages related to missing secrets or configuration

---

## Secrets Configuration

### Required Secrets

#### IBM watsonx.ai Credentials

**WATSONX_API_KEY**
- **Purpose**: Authenticates your application with IBM Cloud
- **How to obtain**: 
  1. Log in to [IBM Cloud](https://cloud.ibm.com)
  2. Navigate to **Manage** → **Access (IAM)** → **API keys**
  3. Click **Create an IBM Cloud API key**
  4. Copy the key immediately (you won't see it again!)
- **Format**: String (typically 40+ characters)
- **Example**: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0`

**WATSONX_PROJECT_ID**
- **Purpose**: Identifies your watsonx.ai project
- **How to obtain**:
  1. Log in to [IBM watsonx.ai](https://dataplatform.cloud.ibm.com/projects/?context=wx)
  2. Select your project
  3. Click **Manage** → **General**
  4. Copy the **Project ID**
- **Format**: UUID string
- **Example**: `12345678-1234-1234-1234-123456789abc`

### Optional Secrets

#### SQL Server Database Connection

Only required if you want to connect to a live SQL Server database instead of using demo mode.

```toml
[connections.sqlserver]
server = "your-server.database.windows.net"
database = "your-database-name"
username = "your-username"
password = "your-password"
driver = "ODBC Driver 17 for SQL Server"
```

**Security Note**: For production deployments, use SQL Server authentication with a dedicated read-only account that has minimal permissions.

### Secrets Management Best Practices

1. **Never commit secrets to Git**:
   - The `.gitignore` file already excludes `.streamlit/secrets.toml`
   - Double-check before committing: `git status`

2. **Use strong, unique credentials**:
   - Generate separate API keys for different environments
   - Rotate credentials regularly

3. **Limit permissions**:
   - Use read-only database accounts when possible
   - Grant minimal necessary permissions to API keys

4. **Monitor usage**:
   - Regularly check IBM Cloud usage dashboard
   - Set up billing alerts to avoid unexpected charges

---

## Database Connectivity

Rosetta supports two database modes:

### Demo Mode (Default)

- **No configuration required**
- Uses an in-memory SQLite database with sample data
- Perfect for testing and demonstrations
- Automatically activated when no SQL Server connection is configured

### SQL Server Mode

- **Requires database credentials** in secrets configuration
- Connects to a live SQL Server database
- Supports both Azure SQL Database and on-premises SQL Server
- Requires network connectivity from Streamlit Cloud to your database

#### Enabling SQL Server Connectivity

1. **Ensure your database is accessible**:
   - For Azure SQL Database: Add Streamlit Cloud IP ranges to firewall rules
   - For on-premises: Ensure public accessibility or use a VPN/tunnel

2. **Configure secrets** (see [Secrets Configuration](#secrets-configuration))

3. **Test the connection**:
   - Deploy the app
   - Navigate to the database connection page
   - Verify successful connection

#### Firewall Configuration for Azure SQL Database

Streamlit Cloud uses dynamic IP addresses. To allow connections:

1. In Azure Portal, navigate to your SQL Server
2. Go to **Security** → **Networking**
3. Under **Firewall rules**, add a rule:
   - **Rule name**: `Streamlit-Cloud`
   - **Start IP**: `0.0.0.0`
   - **End IP**: `255.255.255.255`
   
   ⚠️ **Security Warning**: This allows connections from any IP. For production, use:
   - Azure Private Link
   - VPN Gateway
   - Service endpoints
   - Or restrict to known Streamlit Cloud IP ranges (contact Streamlit support)

4. Enable **"Allow Azure services and resources to access this server"**

---

## Troubleshooting

### Common Deployment Issues

#### Issue: "App failed to load"

**Symptoms**: White screen or error message on app load

**Solutions**:
1. Check the app logs: **Manage app** → **Logs**
2. Verify all required files are in the repository
3. Ensure `requirements.txt` lists all dependencies
4. Check for syntax errors in `app.py`

#### Issue: "WATSONX_API_KEY environment variable is not set"

**Symptoms**: Error message when trying to use AI features

**Solutions**:
1. Verify secrets are configured in Streamlit Cloud dashboard
2. Check for typos in secret names (must match exactly)
3. Ensure secrets were saved (click "Save" button)
4. Restart the app: **Manage app** → **Reboot app**

#### Issue: "Module not found" errors

**Symptoms**: Import errors in logs

**Solutions**:
1. Verify the module is listed in `requirements.txt`
2. Check for typos in package names
3. Ensure version compatibility (try removing version pins)
4. For system packages, add to `packages.txt`

#### Issue: "ODBC Driver not found"

**Symptoms**: Database connection fails with driver error

**Solutions**:
1. Verify `packages.txt` includes `unixodbc-dev`
2. Ensure `requirements.txt` includes `pyodbc`
3. Check driver name in connection string matches installed driver
4. Restart the app after adding packages

#### Issue: Database connection timeout

**Symptoms**: Connection attempts hang or timeout

**Solutions**:
1. Verify database server is accessible from the internet
2. Check firewall rules allow Streamlit Cloud IPs
3. Ensure connection string is correct
4. Test with demo mode first to isolate the issue

#### Issue: "Resource limits exceeded"

**Symptoms**: App crashes or becomes unresponsive

**Solutions**:
1. Streamlit Community Cloud has resource limits:
   - 1 GB RAM per app
   - 1 CPU core
   - 50 GB bandwidth per month
2. Optimize your code for memory efficiency
3. Consider upgrading to Streamlit for Teams for higher limits

### Getting Help

If you continue to experience issues:

1. **Check the logs**: Most errors are explained in the application logs
2. **Review documentation**: 
   - [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
   - [IBM watsonx.ai Documentation](https://dataplatform.cloud.ibm.com/docs/content/wsj/getting-started/welcome-main.html)
3. **Community support**:
   - [Streamlit Community Forum](https://discuss.streamlit.io/)
   - [IBM Community](https://community.ibm.com/)
4. **GitHub Issues**: Report bugs in the Rosetta repository

---

## Security Best Practices

### Credential Management

1. **Never commit secrets to version control**:
   - Use `.gitignore` to exclude sensitive files
   - Review commits before pushing: `git diff`
   - Use `git log -p` to check history for accidentally committed secrets

2. **Rotate credentials regularly**:
   - Change API keys every 90 days
   - Update database passwords quarterly
   - Revoke unused API keys immediately

3. **Use separate credentials per environment**:
   - Development: Personal API keys
   - Staging: Dedicated staging keys
   - Production: Service account keys with minimal permissions

### Database Security

1. **Use read-only accounts**:
   - Grant only SELECT permissions
   - Restrict access to necessary tables/schemas
   - Never use admin accounts for application access

2. **Implement network security**:
   - Use Azure Private Link for Azure SQL Database
   - Enable SSL/TLS for all database connections
   - Restrict firewall rules to minimum necessary IPs

3. **Monitor access**:
   - Enable database auditing
   - Review access logs regularly
   - Set up alerts for suspicious activity

### Application Security

1. **Keep dependencies updated**:
   - Regularly update `requirements.txt`
   - Monitor security advisories
   - Use `pip-audit` to check for vulnerabilities

2. **Validate user input**:
   - Sanitize all user-provided data
   - Use parameterized queries (already implemented in Rosetta)
   - Implement rate limiting for API calls

3. **Protect sensitive data**:
   - Don't log credentials or API keys
   - Mask sensitive information in UI
   - Use HTTPS for all connections (automatic with Streamlit Cloud)

---

## Cost Information

### Streamlit Community Cloud

**Free Tier Includes**:
- Unlimited public apps
- 1 private app
- 1 GB RAM per app
- 1 CPU core per app
- 50 GB bandwidth per month
- Community support

**Limitations**:
- Apps sleep after 7 days of inactivity
- Resource limits may cause performance issues for large datasets
- No SLA or guaranteed uptime

**Upgrade Options**:
- **Streamlit for Teams**: Starting at $250/month
  - More resources per app
  - Private apps
  - Priority support
  - Custom domains

### IBM watsonx.ai

**Pricing Model**: Pay-as-you-go based on usage

**Typical Costs for Rosetta**:
- **Lite Plan**: Free tier available with limited tokens
- **Standard Plan**: ~$0.002 per 1,000 tokens
- **Estimated monthly cost**: $5-20 for moderate usage (depends on query frequency and complexity)

**Cost Optimization Tips**:
1. Cache AI-generated content when possible
2. Use smaller models for simple tasks
3. Implement rate limiting to prevent abuse
4. Monitor usage in IBM Cloud dashboard
5. Set up billing alerts

### Total Cost Estimate

For a typical deployment:
- **Streamlit Cloud**: $0/month (free tier)
- **IBM watsonx.ai**: $5-20/month (depending on usage)
- **Total**: $5-20/month

**Note**: Costs may vary based on usage patterns. Monitor your IBM Cloud billing dashboard regularly.

---

## Maintenance and Updates

### Updating Your Deployment

1. **Make changes locally**:
   ```bash
   # Edit your code
   git add .
   git commit -m "Description of changes"
   ```

2. **Push to GitHub**:
   ```bash
   git push origin main
   ```

3. **Automatic deployment**:
   - Streamlit Cloud automatically detects changes
   - App redeploys within 1-2 minutes
   - No manual intervention required

### Monitoring Your Application

1. **Check app status**:
   - Visit your Streamlit Cloud dashboard
   - Green indicator = app is running
   - Red indicator = app has errors

2. **Review logs**:
   - Click **"Manage app"** → **"Logs"**
   - Monitor for errors or warnings
   - Check performance metrics

3. **Usage analytics**:
   - Streamlit Cloud provides basic analytics
   - Track number of visitors
   - Monitor resource usage

### Updating Dependencies

1. **Update `requirements.txt`**:
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   pip freeze > requirements.txt
   ```

2. **Test locally**:
   ```bash
   streamlit run app.py
   ```

3. **Deploy updates**:
   ```bash
   git add requirements.txt
   git commit -m "Update dependencies"
   git push origin main
   ```

### Backup and Recovery

1. **Code backup**:
   - GitHub serves as your primary backup
   - Consider enabling GitHub Actions for automated backups
   - Tag releases for easy rollback: `git tag v1.0.0`

2. **Secrets backup**:
   - Keep a secure copy of your secrets configuration
   - Use a password manager or encrypted file
   - Document where credentials are stored

3. **Rollback procedure**:
   ```bash
   # Revert to previous commit
   git revert HEAD
   git push origin main
   
   # Or rollback to specific version
   git checkout v1.0.0
   git push origin main --force
   ```

### Scaling Considerations

If your app outgrows Streamlit Community Cloud:

1. **Upgrade to Streamlit for Teams**:
   - More resources per app
   - Better performance
   - Priority support

2. **Self-host on cloud infrastructure**:
   - AWS, Azure, or Google Cloud
   - Full control over resources
   - More complex setup and maintenance

3. **Optimize your application**:
   - Implement caching strategies
   - Reduce database queries
   - Optimize AI model calls
   - Use session state efficiently

---

## Additional Resources

### Documentation
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Community Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [IBM watsonx.ai Documentation](https://dataplatform.cloud.ibm.com/docs/content/wsj/getting-started/welcome-main.html)
- [Rosetta Setup Guide](./SETUP.md)

### Community
- [Streamlit Community Forum](https://discuss.streamlit.io/)
- [Streamlit GitHub](https://github.com/streamlit/streamlit)
- [IBM Community](https://community.ibm.com/)

### Support
- [Streamlit Support](https://streamlit.io/support)
- [IBM Cloud Support](https://cloud.ibm.com/unifiedsupport/supportcenter)

---

## Quick Reference

### Essential Commands

```bash
# Clone repository
git clone https://github.com/username/rosetta.git
cd rosetta

# Install dependencies locally
pip install -r requirements.txt

# Run locally
streamlit run app.py

# Deploy updates
git add .
git commit -m "Update message"
git push origin main
```

### Important URLs

- **Streamlit Cloud Dashboard**: https://share.streamlit.io
- **IBM Cloud Console**: https://cloud.ibm.com
- **IBM watsonx.ai**: https://dataplatform.cloud.ibm.com/projects/?context=wx
- **Your App URL**: `https://[your-app-name].streamlit.app`

### Configuration Files

- `app.py` - Main application
- `requirements.txt` - Python dependencies
- `packages.txt` - System packages
- `.streamlit/config.toml` - Streamlit configuration
- `.streamlit/secrets.toml` - Secrets (not committed)
- `.streamlit/secrets.toml.example` - Secrets template

---

**Last Updated**: May 2026  
**Version**: 1.0  
**Maintainer**: Rosetta Development Team