'''import streamlit as st
from google_auth_oauthlib.flow import Flow
import requests

# Config
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]
REDIRECT_URI = "http://localhost:8501"  # Must match Google Cloud Console exactly

# OAuth start
def login_with_google():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt="consent")
    # Instant redirect
    st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)

# Fetch user info
def fetch_user_info(auth_code):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(code=auth_code)
    credentials = flow.credentials

    resp = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        params={"alt": "json"},
        headers={"Authorization": f"Bearer {credentials.token}"}
    )
    return resp.json()
'''

import streamlit as st
from google_auth_oauthlib.flow import Flow
import requests
import json

# Use secrets from Streamlit Cloud
CLIENT_ID = st.secrets["auth"]["client_id"]
CLIENT_SECRET = st.secrets["auth"]["client_secret"]

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

# Redirect URI must match your deployed app URL exactly
REDIRECT_URI = "https://ksc-at-khec.streamlit.app"  

# Construct client config dynamically
CLIENT_SECRETS = {
    "web": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [REDIRECT_URI],
        "javascript_origins": [REDIRECT_URI],
    }
}

def login_with_google():
    flow = Flow.from_client_config(
        CLIENT_SECRETS,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt="consent")
    st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)

def fetch_user_info(auth_code):
    flow = Flow.from_client_config(
        CLIENT_SECRETS,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(code=auth_code)
    credentials = flow.credentials
    resp = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        params={"alt": "json"},
        headers={"Authorization": f"Bearer {credentials.token}"}
    )
    return resp.json()



st.title("Google Login Demo")

# Handle OAuth callback only once
if "user_info" not in st.session_state:
    if "code" in st.query_params:
        code = st.query_params["code"]
        try:
            st.session_state["user_info"] = fetch_user_info(code)
            st.query_params.clear()
        except Exception as e:
            st.error(f"Login failed: {e}")
            st.query_params.clear()

# If logged in, show info
if "user_info" in st.session_state:
    st.success("✅ You are logged in")
    st.image(st.session_state["user_info"]["picture"], width=100)
    st.write(f"**Name:** {st.session_state['user_info']['name']}")
    st.write(f"**Email:** {st.session_state['user_info']['email']}")
else:
    st.button("Login with Google", type="primary", on_click=login_with_google)
