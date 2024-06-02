import streamlit as st
from navigation import menu, algo_header

st.set_page_config(page_title=algo_header, page_icon=':sparkles:')
st.subheader("Live run page")
menu()