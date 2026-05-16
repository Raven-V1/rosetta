# Streamlit Cloud Secrets Setup

This guide explains how to configure the GROQ_API_KEY for deployment on Streamlit Cloud.

## Overview

The Rosetta application uses the Groq API for AI-powered database documentation generation. When deploying to Streamlit Cloud, you need to configure the API key through the Streamlit Cloud dashboard rather than using a local `.env` file.

## Setup Instructions

### 1. Get Your Groq API Key

1. Visit [Groq Console](https://console.groq.com/keys)
2. Sign in or create an account
3. Generate a new API key
4. Copy the API key (you won't be able to see it again)

### 2. Configure Streamlit Cloud Secrets

1. Go to your app on [Streamlit Cloud](https://share.streamlit.io/)
2. Click on your app to open its dashboard
3. Click the **Settings** button (gear icon)
4. Navigate to the **Secrets** section
5. Add your secret in TOML format:

```toml
GROQ_API_KEY = "your_actual_groq_api_key_here"
```

6. Click **Save**
7. Your app will automatically restart with the new configuration

## Local Development

For local development, create a `.env` file in the project root:

```bash
GROQ_API_KEY=your_actual_groq_api_key_here
```

**Important:** Never commit your `.env` file to version control. It's already included in `.gitignore`.

## Verification

After configuring the secret:

1. Your app should restart automatically
2. Navigate to the **Spotlight** or **Recommended Queries** pages
3. The LLM features should work without errors
4. If you see "LLM features require GROQ_API_KEY to be configured", double-check your secret configuration

## Troubleshooting

### Error: "LLM features require GROQ_API_KEY to be configured"

**Solution:** Verify that:
- The secret is named exactly `GROQ_API_KEY` (case-sensitive)
- The secret value is your actual API key (not "placeholder")
- You saved the secret and the app restarted

### Error: "Unauthorized: Invalid GROQ_API_KEY"

**Solution:** 
- Your API key may be incorrect or expired
- Generate a new API key from the Groq Console
- Update the secret in Streamlit Cloud

### Error: "Rate limit exceeded"

**Solution:**
- You've exceeded Groq's rate limits
- Wait a few minutes before trying again
- Consider upgrading your Groq plan if this happens frequently

## Security Notes

- Never share your API key publicly
- Never commit API keys to version control
- Rotate your API keys periodically
- Use Streamlit Cloud secrets for production deployments
- Use `.env` files only for local development

## Additional Resources

- [Streamlit Cloud Secrets Documentation](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Groq API Documentation](https://console.groq.com/docs)
- [Groq Console](https://console.groq.com/)