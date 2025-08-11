import streamlit as st
from google_auth_oauthlib.flow import Flow
import requests

# Load from Streamlit secrets
CLIENT_ID = st.secrets["auth"]["client_id"]
CLIENT_SECRET = st.secrets["auth"]["client_secret"]

# IMPORTANT: Set your Streamlit app URL exactly here:
REDIRECT_URI = "https://ksc-at-khec.streamlit.app"

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

def get_flow():
    # Prepare OAuth flow object with client config and redirect URI
    client_config = {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI],
        }
    }
    flow = Flow.from_client_config(
        client_config=client_config,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    return flow

def start_auth():
    flow = get_flow()
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline", include_granted_scopes="true")
    # Redirect user immediately using meta refresh
    st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)

def fetch_and_store_user_info(code):
    flow = get_flow()
    flow.fetch_token(code=code)
    credentials = flow.credentials
    token = credentials.token

    # Get user info from Google
    resp = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        params={"alt": "json"},
        headers={"Authorization": f"Bearer {token}"}
    )
    user_info = resp.json()
    st.session_state["user_info"] = user_info
    st.session_state["credentials"] = credentials

def main():
    st.title("Google OAuth Login Demo - Streamlit Cloud Ready")

    # If user_info already in session_state, show it
    if "user_info" in st.session_state:
        st.success(f"✅ Logged in as {st.session_state['user_info']['name']}")
        st.image(st.session_state["user_info"]["picture"], width=100)
        st.write(f"Email: {st.session_state['user_info']['email']}")
        st.button("Logout", on_click=lambda: st.session_state.clear())
        return

    # Check if Google redirected back with code param
    if "code" in st.query_params and "user_info" not in st.session_state:
        try:
            code = st.query_params["code"]
            fetch_and_store_user_info(code)
            st.experimental_set_query_params()  # Clear URL query params
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Login failed: {e}")
            st.experimental_set_query_params()
            return

    # Show login button
    if st.button("Login with Google"):
        start_auth()

if __name__ == "__main__":
    main()
