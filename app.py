import streamlit as st
from display_utils import add_custom_css, display_header, display_executive_modal, display_exec_toggle_button, display_team_guidelines, display_circle_info
from individual_form import individual_form
from team_form import team_form
from auth_service import initialize_auth, get_user_info
from utils import initialize_session_state
from sheets_service import check_existing_registrations

def main():
    # Initialize session state
    initialize_session_state()

    # Page configuration
    st.set_page_config(
        page_title="Knowledge Sharing Circle - Team Selection",
        page_icon="🌟",
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={
            'About': "Knowledge Sharing Circle - Building communities through shared learning",
            'Report a bug': None,
            'Get Help': 'mailto:knowledgesharingcirclekhec@gmail.com'
        }
    )

    # Initialize authentication
    initialize_auth()

    # Add custom CSS
    add_custom_css()

    # Get user info
    user_info = get_user_info()

    # Check if form is submitted
    if st.session_state.get("form_submitted", False):
        if st.session_state.get("submission_type") == "individual":
            st.success("🎉 Individual application submitted successfully!")
            selected_teams = st.session_state.get("selected_teams", [])
            st.success(f"Selected Teams: **{', '.join(selected_teams)}**")
            if st.session_state.get("email_sent", False):
                st.success("📧 Confirmation email sent to your registered email address!")
            else:
                st.warning("⚠️ Application saved but confirmation email could not be sent.")
        else:
            team_name = st.session_state.get("team_name", "Your Team")
            member_count = st.session_state.get("member_count", 1)
            selected_teams = st.session_state.get("selected_teams", [])
            st.success(f"🎉 Team application submitted successfully!")
            st.success(f"Team: **{team_name}** with **{member_count} members**")
            st.success(f"Selected Teams: **{', '.join(selected_teams)}**")
            successful_emails = st.session_state.get("successful_emails", 0)
            total_members = st.session_state.get("member_count", 1)
            if successful_emails == total_members:
                st.success("📧 Confirmation emails sent to all team members!")
            elif successful_emails > 0:
                st.success(f"📧 Confirmation emails sent to {successful_emails} out of {total_members} team members!")
                st.warning("⚠️ Some confirmation emails could not be sent.")
            else:
                st.warning("⚠️ Team application saved but confirmation emails could not be sent.")
        st.balloons()
        return

    # Display header
    display_header()

    # If not logged in, show login screen with executive poster and circle info
    if not user_info:
        # st.info("Please log in with Google to continue with your registration.")
        
        # Create columns for layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            display_executive_modal(force_show=True)
        
        with col2:
            display_circle_info()
        
        return

    # User is logged in - check existing registrations
    existing_registrations = check_existing_registrations(user_info["email"])
    
    if existing_registrations["found"]:
        st.success(f"Welcome back! You are already registered for {len(existing_registrations['teams'])} team(s).")
        
        # Display existing registrations
        st.markdown("### 📋 Your Current Registrations")
        for reg in existing_registrations["registrations"]:
            with st.expander(f"Registration #{reg['id']} - {reg['type'].title()}", expanded=True):
                st.write(f"**Teams:** {', '.join(reg['teams'])}")
                st.write(f"**Submitted:** {reg['timestamp']}")
                if reg['type'] == 'team':
                    st.write(f"**Team Name:** {reg['team_name']}")
                    st.write(f"**Team Members:** {reg['member_count']}")
                if reg['comments']:
                    st.write(f"**Comments:** {reg['comments']}")
        
        # Check if user can register for more teams (max 3 total)
        total_teams = len(existing_registrations['teams'])
        if total_teams < 3:
            remaining_slots = 3 - total_teams
            st.info(f"You can register for {remaining_slots} more team(s). Would you like to add more teams?")
            
            if st.button("➕ Register for Additional Teams"):
                st.session_state.allow_additional_registration = True
                st.session_state.existing_teams = existing_registrations['teams']
                st.rerun()
        else:
            st.success("🎉 You have registered for the maximum number of teams (3). Thank you!")
            return
    
    # Show registration form if user hasn't registered or wants to add more teams
    if not existing_registrations["found"] or st.session_state.get("allow_additional_registration", False):
        
        # Executive toggle button (collapsed after login)
        display_exec_toggle_button()

        # Executive modal
        display_executive_modal()

        # Important note
        if not st.session_state.show_exec_modal:
            st.info("""
            📢 **Important Note:** Students currently in exams are also encouraged to fill this form. 
            We can schedule meetings later as per your convenience and availability.
            """)

            # Team selection (now multiple)
            st.markdown("### 🎯 Select Your Teams")
            
            # Get available teams (exclude already registered teams if applicable)
            available_teams = list(st.session_state.data.keys())
            if st.session_state.get("existing_teams"):
                available_teams = [team for team in available_teams if team not in st.session_state.existing_teams]
            
            max_selections = 3
            if st.session_state.get("existing_teams"):
                max_selections = 3 - len(st.session_state.existing_teams)
            
            selected_teams = st.multiselect(
                f"Choose your preferred teams (Select up to {max_selections})*", 
                available_teams,
                max_selections=max_selections,
                key="team_multiselect",
                help=f"Select up to {max_selections} teams you want to join. Guidelines will appear below."
            )

            if selected_teams != st.session_state.get("selectedTeams", []):
                st.session_state.selectedTeams = selected_teams

            if st.session_state.selectedTeams:
                st.success(f"Please review the guidelines for: **{', '.join(st.session_state.selectedTeams)}**")
            else:
                st.warning(f"⚠️ Please select at least 1 team (up to {max_selections}) to continue")

            st.markdown("---")

            # Create responsive columns - Guidelines LEFT, Forms RIGHT
            if st.session_state.selectedTeams:  # Only show forms if teams are selected
                col1, col2 = st.columns([1, 2])

                with col1:
                    display_team_guidelines()

                with col2:
                    selected = st.radio(
                        '📝 Registration Type:', 
                        options=['Individual', 'Team'], 
                        horizontal=True,
                        help="Individual: Solo application | Team: Group application (max 5 members)"
                    )

                    if selected == 'Individual':
                        individual_form(user_info["email"])
                    else:
                        team_form(user_info["email"])

            else:
                display_team_guidelines()

if __name__ == "__main__":
    main()