import streamlit as st
from navigation import menu, algo_header

st.set_page_config(page_title=algo_header, page_icon=':scroll:')
st.subheader("Information about the app")
menu()

st.write("**Tab Information**")
st.write("**Historical Charts:** See the price history in chart and tabular form")
st.write("**Backtesting Page:** Run backtest and view performance")
st.write("**Live run Page:** Set a live run")
