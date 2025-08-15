import streamlit as st 
from streamlit_oauth import OAuth2Component



#Feature google oauth sign in so that only valid users can fill the form and valid form is collected
CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID"
CLIENT_SECRET = "YOUR_GOOGLE_CLIENT_SECRET"
REDIRECT_URI = "YOUR_REDIRECT_URI"
AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = "openid email profile"

oauth2 = OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_url=AUTHORIZATION_URL,
    token_url=TOKEN_URL,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
)

if "user_email" not in st.session_state:
    result = oauth2.authorize_button("Login with Google")
    if result and "email" in result:
        st.session_state.user_email = result["email"]
    else:
        st.stop()
else:
    st.write(f"Logged in as: {st.session_state.user_email}")

