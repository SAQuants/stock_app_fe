# pip list --format=freeze > requirements.txt
import streamlit as st
import time
from navigation import menu, algo_header

# streamlit run stock_app_main.py
# https://carpedm20.github.io/emoji/
# https://raw.githubusercontent.com/omnidan/node-emoji/master/lib/emoji.json
st.set_page_config(page_title=algo_header, page_icon=':bank:', initial_sidebar_state='collapsed')
st.subheader('Landing Page')

# Initialize st.session_state.logged_in to None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = None

menu() # Render the dynamic menu!


def authenticate(username, password):
    # Replace with your authentication logic
    if username == "admin" and password == "password":
        return True
    else:
        return False


def show_login():
    # Login Section
    st.subheader(algo_header)
    st.write("Please log in to continue.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login", type="primary")

    if login_button:
        if authenticate(username, password):
            st.success("Logged in as {}".format(username))
            st.session_state.logged_in = True
            st.success("Logged in!")
            time.sleep(0.5)
            st.switch_page("pages/01_info.py")
        else:
            st.session_state.logged_in = False
            st.error("Incorrect username or password")


if __name__ == "__main__":

    show_login()
