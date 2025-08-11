import streamlit as st
from httpx_oauth.clients.google import GoogleOAuth2
import toml
import os
import asyncio
import httpx

st.title("Google Sign-In Protected Form")

# Load secrets from .streamlit/secrets.toml
secrets = toml.load(".streamlit/secrets.toml")
client_id = secrets["auth"]["client_id"]
client_secret = secrets["auth"]["client_secret"]

# Detect if running locally or on Streamlit Cloud by environment variable or hostname
IS_LOCAL = st.runtime.exists() and st.runtime.get_app_url().startswith("http://localhost")

# Dynamically set redirect URI depending on environment
if IS_LOCAL:
    redirect_uri = "http://localhost:8501/oauth2callback"
else:
    # Your deployed Streamlit app URL
    redirect_uri = "https://ksc-at-khec.streamlit.app/oauth2callback"

google_client = GoogleOAuth2(client_id, client_secret)

def clear_query_params_and_rerun():
    st.experimental_set_query_params()
    st.experimental_rerun()

if "user_email" not in st.session_state:
    st.write("Please sign in with Google to continue.")

    query_params = st.experimental_get_query_params()

    # Handle callback when code is present in query params
    if "code" in query_params:
        code = query_params["code"][0] if isinstance(query_params["code"], list) else query_params["code"]
        try:
            token = asyncio.run(google_client.get_access_token(code, redirect_uri))
            access_token = token["access_token"]
            userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            response = httpx.get(userinfo_url, headers={"Authorization": f"Bearer {access_token}"})
            if response.status_code == 200:
                user_info = response.json()
                st.session_state["user_email"] = user_info["email"]
                clear_query_params_and_rerun()
            else:
                st.error(f"Failed to fetch user info from Google. Response: {response.text}")
        except Exception as e:
            st.error(f"Google OAuth failed: {e}")
            clear_query_params_and_rerun()

    else:
        if st.button("Sign in with Google"):
            auth_url = asyncio.run(
                google_client.get_authorization_url(
                    redirect_uri,
                    scope=["openid", "email", "profile"],
                    state=None
                )
            )
            st.markdown(f"<meta http-equiv='refresh' content='0;url={auth_url}'>", unsafe_allow_html=True)
            st.stop()

else:
    st.write(f"Signed in as: {st.session_state['user_email']}")
    with st.form("protected_form"):
        name = st.text_input("Name")
        message = st.text_area("Message")
        if st.form_submit_button("Submit"):
            st.success("Form submitted!")
    if st.button("Log out"):
        del st.session_state["user_email"]
        clear_query_params_and_rerun()
        st.success("Logged out successfully!")