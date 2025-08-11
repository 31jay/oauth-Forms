import streamlit as st
from httpx_oauth.clients.google import GoogleOAuth2
import toml

st.title("Google Sign-In Protected Form")

# Load secrets
secrets = toml.load(".streamlit/secrets.toml")
client_id = secrets["auth"]["client_id"]
client_secret = secrets["auth"]["client_secret"]
redirect_uri = secrets["auth"]["redirect_uri"]  #ksc-at-khec.streamlit.app/oauth2callback

google_client = GoogleOAuth2(client_id, client_secret)

if "user_email" not in st.session_state:
    st.write("Please sign in with Google to continue.")
    if st.button("Sign in with Google"):
        import asyncio
        auth_url = asyncio.run(
            google_client.get_authorization_url(
                redirect_uri,
                scope=["openid", "email", "profile"],
                state=None
            )
        )
        st.query_params.clear()  
        st.markdown(f"<meta http-equiv='refresh' content='0;url={auth_url}'>", unsafe_allow_html=True)
        st.stop()

    # Handle callback
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"][0] if isinstance(query_params["code"], list) else query_params["code"]
        import httpx
        try:
            import asyncio
            token = asyncio.run(google_client.get_access_token(code, redirect_uri))
            st.write(f"DEBUG: Token exchange succeeded: {token}")
            access_token = token["access_token"]
            userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            response = httpx.get(userinfo_url, headers={"Authorization": f"Bearer {access_token}"})
            if response.status_code == 200:
                user_info = response.json()
                st.write(f"DEBUG: User info: {user_info}")
                st.session_state["user_email"] = user_info["email"]
                st.query_params.clear()  # Clear code after success
                st.rerun()
            else:
                st.error(f"Failed to fetch user info from Google. Response: {response.text}")
        except Exception as e:
            st.write(f"DEBUG: Token exchange error: {e}")
            st.error(f"Google OAuth failed: {e}")
            st.query_params.clear()
else:
    st.write(f"Signed in as: {st.session_state['user_email']}")
    with st.form("protected_form"):
        name = st.text_input("Name")
        message = st.text_area("Message")
        if st.form_submit_button("Submit"):
            st.success("Form submitted!")
    if st.button("Log out"):
        del st.session_state["user_email"]
        st.rerun()
