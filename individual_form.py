import streamlit as st
import json
import re 
import os 


def save_response(name, crn, contact, email, team):
    filename = "individual_responses.json"

    # Load existing data or start with empty dict
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    # Determine next SN (max key + 1)
    if data:
        max_sn = max(map(int, data.keys()))
        next_sn = max_sn + 1
    else:
        next_sn = 1

    # Add new record
    data[str(next_sn)] = {
        "name": name,
        "crn": crn,
        "contact": contact,
        "email": email,
        "team": team
    }

    # Save back to file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Record saved with SN: {next_sn}")



def individual_form(mail, data):
    with st.form("form"):
        name = st.text_input("Name")
        name_error = st.empty()
        crn = st.text_input("CRN")
        crn_error = st.empty()
        contact = st.text_input("Contact Number")
        contact_error = st.empty()
        email = mail 
        st.text_input("Email", placeholder=mail, disabled=True)
        email_error = st.empty()
        team = st.selectbox("Select Team", list(data.keys()))
        submit_button = st.form_submit_button("Submit")
        form_placeholder = st.empty()   

        errors = 0

        # Name validation: Full Name (at least two words)
        if submit_button:
            if not re.match(r"^[A-Za-z]+(?: [A-Za-z]+)+$", name.strip()):
                errors += 1
                name_error.error("Please enter your full name (first and last name).")

            # CRN validation
            if not re.match(r"^(?:77(?=01(0[1-9]|[1-3][0-9]|4[0-9]))|(?:78|79|80|81)(?:01(0[1-9]|[1-3][0-9]|4[0-9])|02(0[1-9]|[1-8][0-9]|9[0-7])|0[34](0[1-9]|[1-3][0-9]|4[0-9])))$", crn):
                errors += 1
                crn_error.error("Please enter a valid CRN.")

            # Contact validation: 10 digits, starts with 97 or 98
            if not re.match(r"^(97|98)\d{8}$", contact):
                errors += 1
                contact_error.error("Please enter a valid contact number.")

            # Email validation
            if not re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email):
                errors += 1
                email_error.error("Please enter a valid email address.")

            if errors:
                st.error(f"Please fix the {errors} errors above.")
            else:
                st.session_state.selectedTeam = team
                save_response(name, crn, contact, email, team)
                form_placeholder.success("Form submitted successfully!")


if __name__ == "__main__":
    st.title("Individual Form")
    
    with open("team_guidelines.json") as f:
        data = json.load(f)
    st.session_state.user_email = 'jay@gmail.com'
    # Check if user is logged in
    if "user_email" in st.session_state:
        individual_form(st.session_state["user_email"], data)
    else:
        st.error("You must be logged in to fill this form.")