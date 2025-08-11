import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import requests
import os

# Load from Streamlit secrets
client_id = st.secrets["auth"]["client_id"]
client_secret = st.secrets["auth"]["client_secret"]
server_metadata_url = st.secrets["auth"]["server_metadata_url"]

# Detect environment
IS_LOCAL = os.environ.get("LOCAL_DEV", "false").lower() == "true"

if IS_LOCAL:
    redirect_uri = "http://localhost:8501/oauth2callback"
else:
    redirect_uri = "https://ksc-at-khec.streamlit.app/oauth2callback"

# Get the OpenID Connect server metadata
server_metadata = requests.get(server_metadata_url).json()

# Initialize OAuth session
oauth = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri)

# Store user info in session state
if "user" not in st.session_state:
    st.session_state["user"] = None

# Get query params
params = st.query_params

if "code" in params:
    token = oauth.fetch_token(
        server_metadata["token_endpoint"],
        authorization_response=st.experimental_get_query_params(),
        client_secret=client_secret
    )
    userinfo = oauth.get(
        server_metadata["userinfo_endpoint"],
        token=token
    ).json()
    st.session_state["user"] = userinfo
    st.query_params.clear()  # clean URL

# UI
st.title("Google OAuth Login Demo")

if st.session_state["user"]:
    st.success(f"✅ Logged in as {st.session_state['user']['email']}")
    st.json(st.session_state["user"])
else:
    if st.button("Login with Google"):
        auth_url, _ = oauth.create_authorization_url(
            server_metadata["authorization_endpoint"],
            scope="openid email profile"
        )
        st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)
