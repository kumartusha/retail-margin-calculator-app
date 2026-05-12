# Retail Margin Calculator

A secure Streamlit web application that fetches vehicle data from Google Sheets based on registration number.

## Features

- 🔒 Secure authentication using Google Service Account
- 🔍 Search by Registration Number
- 📊 Display key vehicle information:
  - Concat Rank & Vehicle Number
  - Final MMVF
  - Expected Selling Price To Customer
  - Margin %
  - Seller Name
  - Ageing1

## Local Development

1. Install dependencies:
```bash
pip install -r requirement.txt
```

2. Set up environment variables in `.env`:
```
SPREADSHEET_ID="your-google-sheet-id"
```

3. Place your `service_account.json` file in the project root (this file is in .gitignore)

4. Run the app:
```bash
streamlit run app.py
```

## Deployment to Streamlit Cloud

### Step 1: Prepare your GitHub repository

1. Make sure `.gitignore` includes:
```
.env
service_account.json
.streamlit/secrets.toml
```

2. Push your code to GitHub (excluding sensitive files)

### Step 2: Set up Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. Set the main file path to `app.py`

### Step 3: Configure Secrets

In Streamlit Cloud, go to your app settings → Secrets and add:

```toml
[google_credentials]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = """-----BEGIN PRIVATE KEY-----
YOUR_PRIVATE_KEY_HERE
-----END PRIVATE KEY-----"""
client_email = "your-client-email@project-id.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-client-email@project-id.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

Also add:
```
SPREADSHEET_ID="your-google-sheet-id"
```

### Step 4: Deploy

Click "Deploy" and your app will be live!

## Security Notes

- ✅ Service account credentials are stored in Streamlit Cloud secrets, not in code
- ✅ `.env` and `service_account.json` are in `.gitignore` and never committed
- ✅ Google Sheet link is never exposed - only the spreadsheet ID is used
- ✅ Read-only access to Google Sheets

## Google Sheets Setup

Make sure your Google Service Account has:
1. Access to the Google Sheet (share with the service account email)
2. The worksheet is named exactly "Procurment_Backup"
3. The service account has at least "Viewer" permissions
