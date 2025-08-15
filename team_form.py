import streamlit as st 
import json
import re 
import os 


if "num_tabs" not in st.session_state:
    st.session_state.num_tabs = 1

def add_tab():
    st.session_state.num_tabs += 1


def team_form():
    tab_labels = [f"Member {i+1}" for i in range(st.session_state.num_tabs)]

    tab_labels.append("+ Add Member")

    tabs = st.tabs(tab_labels)

    for i, tab in enumerate(tabs):
        with tab:
            if i < st.session_state.num_tabs:
                st.write(f"Fill the details for **Member {i+1}**")
                with st.form(f"form_{i}"):
                    name = st.text_input("Name")
                    crn = st.text_input("CRN")
                    contact = st.text_input("Contact Number")
                    email = st.text_input("Email")
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

                        if errors:
                            st.error(f"Please fix the {errors} errors above.")
                        else:
                            st.session_state.selectedTeam = team
                            save_response(name, crn, contact, email, team)
                            form_placeholder.success("Form submitted successfully!")

            else:
                st.button("Add Team Member", on_click=add_tab)


