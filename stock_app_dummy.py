# pip list --format=freeze > requirements.txt
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

# test comment

def get_stock_data(ticker, start_date, end_date):
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    return stock_data


def main():
    st.title("Stock Time Series Data App")

    # User input for stock ticker
    ticker = st.text_input("Enter Stock Ticker:", "MSFT")

    # User input for date range
    date_format = "%Y-%m-%d"
    start_date = st.date_input("Start Date", datetime.strptime("2023-01-01", date_format))
    end_date = st.date_input("End Date", datetime.strptime("2023-12-31", date_format))

    # Button to fetch data
    if st.button("Get Time Series Data"):
        st.write(f"Fetching data for {ticker}...")

        # Get stock data
        stock_data = get_stock_data(ticker, start_date, end_date)

        # Display the data
        st.write("Time Series Data:")
        st.write(stock_data)

        # Plot the closing price using Plotly
        fig = px.line(stock_data, x=stock_data.index, y='Close', title=f'{ticker} Stock Price')
        st.plotly_chart(fig)


if __name__ == "__main__":
    main()
