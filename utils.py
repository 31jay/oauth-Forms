import streamlit as st
import re

def initialize_session_state():
    """Initialize session state variables"""
    if "num_tabs" not in st.session_state:
        st.session_state.num_tabs = 1
    if "selectedTeam" not in st.session_state:
        st.session_state.selectedTeam = None
    if "show_exec_modal" not in st.session_state:
        st.session_state.show_exec_modal = True
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False

def validate_form_data(name, crn, contact, email):
    """Validate form inputs and return errors"""
    errors = []
    
    if not name.strip():
        errors.append("Name is required")
    elif not re.match(r"^[A-Za-z]+(?: [A-Za-z]+)+$", name.strip()):
        errors.append("Please enter your full name (first and last name)")
    
    if not crn.strip():
        errors.append("CRN is required")
    elif not re.match(r"^(?:77(?=01(0[1-9]|[1-3][0-9]|4[0-9]))|(?:78|79|80|81)(?:01(0[1-9]|[1-3][0-9]|4[0-9])|02(0[1-9]|[1-8][0-9]|9[0-7])|0[34](0[1-9]|[1-3][0-9]|4[0-9])))$", crn):
        errors.append("Please enter a valid CRN")
    
    if not contact.strip():
        errors.append("Contact number is required")
    elif not re.match(r"^(97|98)\d{8}$", contact):
        errors.append("Please enter a valid contact number (10 digits starting with 97 or 98)")
    
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