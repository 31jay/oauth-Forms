import streamlit as st
import json 
import re

FILE = "team_guidelines.json"
forms_col, side_col = st.columns([3, 1])
with open(FILE) as f:
    data = json.load(f)

if "num_tabs" not in st.session_state:
    st.session_state.num_tabs = 1

def add_tab():
    st.session_state.num_tabs += 1

def form_fields(x):
    with st.form(f"team_form_{x}"):
        name = st.text_input("Name")
        name_error = st.empty()
        crn = st.text_input("CRN")
        crn_error = st.empty()
        contact = st.text_input("Contact Number")
        contact_error = st.empty()
        email = st.text_input("Email")
        email_error = st.empty()
        team = st.selectbox("Select Team", list(data.keys()))
        submit_button = st.form_submit_button("Submit")
        form_placeholder = st.empty()   

        errors = []

        # Name validation: Full Name (at least two words)
        if submit_button:
            if not re.match(r"^[A-Za-z]+(?: [A-Za-z]+)+$", name.strip()):
                errors.append("Please enter your full name (first and last name).")
                name_error.error("Please enter your full name (first and last name).")

            # CRN validation
            if not re.match(r"^(?:77(?=01(0[1-9]|[1-3][0-9]|4[0-9]))|(?:78|79|80|81)(?:01(0[1-9]|[1-3][0-9]|4[0-9])|02(0[1-9]|[1-8][0-9]|9[0-7])|0[34](0[1-9]|[1-3][0-9]|4[0-9])))$", crn):
                errors.append("Please enter a valid CRN.")
                crn_error.error("Please enter a valid CRN.")

            # Contact validation: 10 digits, starts with 97 or 98
            if not re.match(r"^(97|98)\d{8}$", contact):
                errors.append("Please enter a valid contact number.")
                contact_error.error("Please enter a valid contact number.")

            # Email validation
            if not re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email):
                errors.append("Please enter a valid email address.")
                email_error.error("Please enter a valid email address.")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                st.session_state.selectedTeam = team
                form_placeholder.success("Form submitted successfully!")


def members_form():
    with forms_col:
        selected = st.radio('Fill as:', options=['Individual', 'Team'],horizontal=True)
        if selected == 'Individual':
            form_fields(1)
        else:
            tab_labels = [f"Member {i+1}" for i in range(st.session_state.num_tabs)]

            tab_labels.append("+ Add Member")

            tabs = st.tabs(tab_labels)

            for i, tab in enumerate(tabs):
                with tab:
                    if i < st.session_state.num_tabs:
                        st.write(f"Fill the details for **Member {i+1}**")
                        form_fields(i)
                    else:
                        st.button("Add Team Member", on_click=add_tab)



if __name__ == "__main__":
    st.set_page_config(layout="wide")
    st.header("Team Selection Form")
    if "selectedTeam" not in st.session_state:
        st.session_state.selectedTeam = None

    members_form()

    with side_col:
        st.subheader("Team Guidelines")
        for team, guidelines in data.items():
            st.write(f"**{team}**: {guidelines}")