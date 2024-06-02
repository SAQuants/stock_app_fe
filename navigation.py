import streamlit as st
import time

algo_header = "Algo Trading Interface v0.3"
backend_url = 'http://vm4lean.northeurope.cloudapp.azure.com:8080' # 'http://127.0.0.1:8000'


def authenticated_menu():
    # Show a navigation menu for authenticated users
    if st.session_state.get("logged_in", False):
        st.sidebar.page_link("pages/01_info.py", label="Landing Page")
        st.sidebar.page_link("pages/02_historical_charts.py", label="Historical Charts")
        st.sidebar.page_link("pages/03_backtest.py", label="Backtesting Page")
        st.sidebar.page_link("pages/04_liverun.py", label="Live run Page")
        # st.sidebar.page_link("stock_app_main.py", label="Login Page", disabled=True)
        st.sidebar.write("")
        st.sidebar.write("")
        if st.sidebar.button("Log out"):
            logout()


def unauthenticated_menu():
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("stock_app_main.py", label="Login Page", disabled=False)


def logout():
    st.session_state.logged_in = False
    st.sidebar.info("Logged out successfully!")
    time.sleep(0.5)
    st.switch_page("stock_app_main.py")


def menu():
    # Determine if a user is logged in or not, then show the correct
    # navigation menu
    if "logged_in" not in st.session_state or st.session_state.logged_in is None:
        unauthenticated_menu()
        return
    authenticated_menu()


def menu_with_redirect():
    # Redirect users to the main page if not logged in, otherwise continue to
    # render the navigation menu
    if "logged_in" not in st.session_state or st.logged_in.role is None:
        st.switch_page("stock_app_main.py")
    menu()
