import streamlit as st
from httpx_oauth.clients.google import GoogleOAuth2
import toml
import streamlit.components.v1 as components  # Added missing import for persistent login cookies

st.title("Google Sign-In Protected Form")

# Replace with your Google OAuth credentials
secrets = toml.load(".streamlit/secrets.toml")
client_id = secrets["auth"]["client_id"]
client_secret = secrets["auth"]["client_secret"]
# Force redirect_uri to match Google Cloud Console
redirect_uri = "http://localhost:8501/oauth2callback"

google_client = GoogleOAuth2(client_id, client_secret)

# Debug: Show all query parameters after redirect
print(f"DEBUG: All query params: {st.query_params}")

if "user_email" not in st.session_state:
    st.write("If you are already signed in with Google in your browser, you may not need to sign in again. Otherwise, please sign in with Google to continue.")


    import asyncio
    # if st.button("Sign in with Google"):
    auth_url = asyncio.run(
        google_client.get_authorization_url(
            redirect_uri,
            scope=["openid", "email", "profile"],
            state=None
        )
    )
    st.session_state["auth_url"] = auth_url

    if "auth_url" in st.session_state:
        st.markdown(f"<a href='{st.session_state['auth_url']}'>Click here to sign in with Google</a>", unsafe_allow_html=True)

    # Handle callback
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"][0] if isinstance(query_params["code"], list) else query_params["code"]
        print(f"DEBUG: Received auth code: {code}")
        import httpx
        try:
            token = asyncio.run(google_client.get_access_token(code, redirect_uri))
            print(f"DEBUG: Token exchange succeeded: {token}")
            access_token = token["access_token"]
            userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            response = httpx.get(userinfo_url, headers={"Authorization": f"Bearer {access_token}"})
            print(f"DEBUG: Userinfo response status: {response.status_code}")
            if response.status_code == 200:
                user_info = response.json()
                print(f"DEBUG: User info: {user_info}")
                st.session_state["user_email"] = user_info["email"]
                # Set cookie for persistent login
                components.html(f"<script>document.cookie = 'user_email={user_info['email']}; path=/';</script>", height=0)
                # Instead of rerun, use stop() to view debug logs
                st.experimental_set_query_params()
                print("DEBUG: Token exchange complete. Please check the debug output.")
                st.stop()
            else:
                st.error(f"Failed to fetch user info from Google. Response: {response.text}")
                st.experimental_set_query_params()
                st.stop()
        except Exception as e:
            print(f"DEBUG: Token exchange error: {e}")
            st.error(f"Google OAuth failed: {e}")
            # Clear the query params so that an expired code is not reused
            st.experimental_set_query_params()
            st.stop()

    # If user is already logged in in the browser, use their cookies to skip OAuth
    if "user_email" not in st.session_state and "email" in query_params:
        st.session_state["user_email"] = query_params["email"]
        st.rerun()
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
