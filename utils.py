import streamlit as st
import re
import json

def initialize_session_state():
    """Initialize session state variables"""
    if "num_tabs" not in st.session_state:
        st.session_state.num_tabs = 1
    if "selectedTeams" not in st.session_state:  # Changed from selectedTeam to selectedTeams
        st.session_state.selectedTeams = []
    if "show_exec_modal" not in st.session_state:
        st.session_state.show_exec_modal = False  # Changed to False so it's collapsed initially after login
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False
    if "allow_additional_registration" not in st.session_state:
        st.session_state.allow_additional_registration = False
    if "existing_teams" not in st.session_state:
        st.session_state.existing_teams = []
    if "data" not in st.session_state:
        try:
            with open("team_guidelines.json") as f:
                st.session_state.data = json.load(f)
        except FileNotFoundError:
            st.error("⚠️ team_guidelines.json not found. Please ensure the file exists.")
            st.session_state.data = {}
        except Exception as e:
            st.error(f"⚠️ Error loading team_guidelines.json: {str(e)}")
            st.session_state.data = {}
    if "circle_data" not in st.session_state:
        try:
            with open("circle_info.json") as f:
                st.session_state.circle_data = json.load(f)
        except FileNotFoundError:
            st.error("⚠️ circle_info.json not found. Please ensure the file exists.")
            st.session_state.circle_data = {}
        except Exception as e:
            st.error(f"⚠️ Error loading circle_info.json: {str(e)}")
            st.session_state.circle_data = {}

def validate_form_data(name, crn, contact, email):
    """Validate form inputs and return errors"""
    errors = []
    
    if not name.strip():
        errors.append("Name is required")
    elif not re.match(r"^[A-Za-z]+(?: [A-Za-z]+)+$", name.strip()):
        errors.append("Please enter your full name (first and last name)")
    
    if not crn.strip():
        errors.append("CRN is required")
    
    if not contact.strip():
        errors.append("Contact number is required")
    elif not re.match(r"^(97|98)\d{8}$", contact):
        errors.append("Please enter a valid contact number")
    
    if not email.strip():
        errors.append("Email is required")
    elif not re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email):
        errors.append("Please enter a valid email address")
    
    return errors

def has_any_field_filled(member_data):
    """Check if any field in member data is filled"""
    return any([
        member_data.get("name", "").strip(),
        member_data.get("crn", "").strip(),
        member_data.get("contact", "").strip(),
        member_data.get("email", "").strip()
    ])

def add_tab():
    """Add a new team member tab"""
    if st.session_state.num_tabs < 5:
        st.session_state.num_tabs += 1

def remove_tab():
    """Remove the last team member tab"""
    if st.session_state.num_tabs > 1:
        st.session_state.num_tabs -= 1