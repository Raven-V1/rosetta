# Rosetta

Onboarding tool for new developers inheriting unfamiliar databases.

Rosetta connects to a relational database, inspects its schema, and generates an interactive onboarding experience. New developers can understand a database structure, see how tables relate, and start writing useful queries within their first hour, instead of spending their first week reverse-engineering.

Built with IBM Bob for the IBM Bob Hackathon, May 2026.

## Status

In active development. Hackathon build window: May 15-17, 2026.

## 🚀 Deployment

### Live Demo

🔗 **[Try Rosetta Live](https://rosetta-demo.streamlit.app)** *(Coming Soon)*

### Deploy Your Own

Rosetta is designed for easy deployment to Streamlit Community Cloud:

1. **Fork this repository** to your GitHub account
2. **Sign up** for [Streamlit Community Cloud](https://share.streamlit.io) (free)
3. **Deploy** with one click from your Streamlit dashboard
4. **Configure secrets** for IBM watsonx.ai integration

📖 **[Complete Deployment Guide](docs/DEPLOYMENT.md)** - Step-by-step instructions for deploying to Streamlit Cloud, including secrets configuration, database connectivity, and troubleshooting.

### Quick Deploy

[![Deploy to Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

**Requirements:**
- GitHub account
- IBM Cloud account (for watsonx.ai API access)
- 5 minutes of setup time

**Cost:** Free tier available on both Streamlit Community Cloud and IBM watsonx.ai

## 📚 Documentation

- **[Setup Guide](docs/SETUP.md)** - Local development and IBM watsonx.ai configuration
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Complete guide for Streamlit Cloud deployment

## License

MIT
