import streamlit as st
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
import requests

def display_login_button(auth_url):
    """Display a styled Google login button"""
    st.markdown("""
    <style>
    .google-login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 2rem 0;
        padding: 1rem;
    }
    
    .google-login-btn {
        display: inline-flex;
        align-items: center;
        background-color: #ffffff;
        color: #4285f4;
        text-decoration: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 500;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        box-shadow: 0 2px 4px 0 rgba(0,0,0,.25);
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
        min-width: 240px;
        justify-content: center;
    }
    
    .google-login-btn:hover {
        background-color: #357ae8;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,.3);
        transform: translateY(-1px);
        text-decoration: none;
        color: white;
    }
    
    .google-login-btn:active {
        transform: translateY(0);
        box-shadow: 0 2px 4px 0 rgba(0,0,0,.25);
    }
    
    .google-icon {
        width: 20px;
        height: 20px;
        margin-right: 12px;
        background: white;
        border-radius: 2px;
        padding: 2px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="google-login-container">
        <div style="text-align: center; width: 100%;">
            <a href="{}" class="google-login-btn">
                <div class="google-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path fill="#4285f4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                        <path fill="#34a853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                        <path fill="#fbbc05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                        <path fill="#ea4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                    </svg>
                </div>
                Sign in with Google
            </a>
        </div>
    </div>
    """.format(auth_url), unsafe_allow_html=True)

def initialize_auth():
    # Initialize session state for credentials
    if "credentials" not in st.session_state:
        st.session_state.credentials = None

    # Config
    CLIENT_ID = st.secrets["gcp_oauth"]["client_id"]
    CLIENT_SECRET = st.secrets["gcp_oauth"]["client_secret"]
    REDIRECT_URI = st.secrets["gcp_oauth"]["redirect_uri"]

    SCOPES = [
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ]

    if not st.session_state.credentials:
        # Construct Flow
        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [REDIRECT_URI]
                }
            },
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )

        auth_url, _ = flow.authorization_url(prompt="consent")
        
        # Display the styled login button
        display_login_button(auth_url)

        # Get code as string
        code = st.query_params.get("code")
        if code:
            try:
                flow.fetch_token(code=code)
                st.session_state.credentials = flow.credentials
                st.query_params.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {e}")
                st.query_params.clear()
                st.rerun()

def get_user_info():
    if st.session_state.credentials:
        creds = st.session_state.credentials
        request_session = requests.Session()
        token_request = google.auth.transport.requests.Request(session=request_session)

        if creds.expired and creds.refresh_token:
            creds.refresh(token_request)

        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            params={"alt": "json"},
            headers={"Authorization": f"Bearer {creds.token}"}
        ).json()

        return {
            "name": user_info.get("name", ""),
            "email": user_info.get("email", ""),
            "picture": user_info.get("picture", "")
        }
    return None