# import streamlit as st 
# import json 

# FILE = "team_guidelines.json"
# # st.session_state.selectedTeam = None



# #A form that will feature Name, CRN, and Team Selection (individual or group).
# def createForm():
#     st.header("Team Selection Form")
#     with open(FILE, "r") as f:
#         data = json.load(f)
#     col1, col2 = st.columns([1, 1])
#     if "selectedTeam" not in st.session_state:
#         st.session_state.selectedTeam = None

    

#     name = st.text_input("Name")
#     crn = st.text_input("CRN")
#     team = st.selectbox("Select Team", list(data.keys()))
#     submit = st.button("Submit")

#     if submit:
#         st.success(f"Form submitted successfully!\nName: {name}\nCRN: {crn}\nTeam: {team}")




# if __name__ == "__main__":
#     createForm()



