import streamlit as st
from utils import validate_form_data
from email_service import send_confirmation_email
from sheets_service import save_individual_response
from datetime import datetime

def individual_form(user_email):
    with st.form("individual_form"):
        st.markdown("### 👤 Individual Registration")

        col1, col2 = st.columns([1, 1])

        with col1:
            name = st.text_input("👤 Full Name*", placeholder="Enter your full name")
            crn = st.text_input("🆔 CRN*", placeholder="Enter your CRN")

        with col2:
            contact = st.text_input("📱 Contact*", placeholder="97xxxxxxxx or 98xxxxxxxx")
            email = st.text_input("📧 Email*", value=user_email, disabled=True)

        comments = st.text_area(
            "💬 Comments / Feedback / Suggestions (Optional)", 
            placeholder="Share any thoughts, suggestions, or feedback you'd like us to know...",
            help="This field is optional. Feel free to share any thoughts or suggestions!"
        )

        submit_button = st.form_submit_button("🚀 Submit Individual Application", use_container_width=True)

        if submit_button:
            if not st.session_state.selectedTeams:
                st.error("⚠️ Please select at least one team first!")
                return

            errors = validate_form_data(name, crn, contact, user_email)

            if errors:
                for error in errors:
                    st.error(f"⚠️ {error}")
            else:
                response_data = {
                    "submission_type": "individual",
                    "timestamp": datetime.now().isoformat(),
                    "name": name.strip(),
                    "crn": crn,
                    "contact": contact,
                    "email": user_email.lower(),
                    "selected_teams": st.session_state.selectedTeams,  # Multiple teams
                    "comments": comments.strip() if comments else ""
                }

                sheets_success = save_individual_response(response_data)

                if sheets_success:
                    try:
                        # Send email with all selected teams
                        email_sent = send_confirmation_email(
                            recipient_email=user_email.lower(),
                            recipient_name=name.strip(),
                            team_name=", ".join(st.session_state.selectedTeams),  # Join multiple teams
                            submission_type="Individual"
                        )
                        st.session_state.form_submitted = True
                        st.session_state.submission_type = "individual"
                        st.session_state.selected_teams = st.session_state.selectedTeams
                        st.session_state.email_sent = email_sent
                        st.rerun()
                    except Exception as e:
                        st.session_state.form_submitted = True
                        st.session_state.submission_type = "individual"
                        st.session_state.selected_teams = st.session_state.selectedTeams
                        st.session_state.email_sent = False
                        st.rerun()
                else:
                    st.error("❌ Failed to save application. Please try again.")