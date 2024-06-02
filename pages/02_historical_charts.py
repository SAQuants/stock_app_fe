import pandas as pd
import plotly.express as px
from datetime import datetime
import requests
import io
import streamlit as st
from navigation import menu, algo_header, backend_url

st.set_page_config(page_title=algo_header, page_icon=':chart_with_upwards_trend:')
st.subheader("Historical Charts")


def extract_timeseries(response_dict):
    df_stock_ts = pd.read_json(io.StringIO(response_dict))  # pd.read_json(res.json())#
    df_stock_ts['Date'] = df_stock_ts['Date'].dt.date
    df_stock_ts.set_index('Date', inplace=True)
    return df_stock_ts


def request_data(symbol, params):
    # stock_data = yf.download(ticker, start=start_date, end=end_date)
    # stock_data = pd.read_json(io.StringIO(json_str))
    res = requests.get(f"{backend_url}/symbol/{symbol}", params=params)
    # print(f'res: {res}, res.json(): {res.json()}')
    if res.status_code != 200:
        print(res, res.text)
        return res.text

    response_dict = res.json()
    if 'backtest' not in params:
        df_res = extract_timeseries(response_dict)
        return df_res


def get_chart(df_ts):
    ticker = df_ts["ticker"].iloc[0]
    fig = px.line(df_ts, x=df_ts.index, y='Close', title=f'{ticker} Stock Price')
    return fig


def plot_ts(df_ts):
    tab1, tab2 = st.tabs(["Chart", "Data"])

    with tab1:
        # ticker = df_ts["ticker"].iloc[0]
        # fig = px.line(df_ts, x=df_ts.index, y='Close', title=f'{ticker} Stock Price')
        fig = get_chart(df_ts)
        st.plotly_chart(fig)
    with tab2:
        st.write(f"**Time Series Data**")
        st.dataframe(df_ts)


def hist_chart_main():

    # User input for stock ticker
    resp_symbols = requests.get(backend_url+'/symbols')
    if resp_symbols.status_code != 200:
        print(resp_symbols, resp_symbols.text)
        return
    # print(resp_symbols.json())
    df_symbol = pd.DataFrame(resp_symbols.json())

    date_format = "%Y-%m-%d"
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        ib_ticker = st.selectbox("Select Stock Ticker", df_symbol['symbol'])
    with col2:
        ib_start_dt = st.date_input("Start Date",
                                    datetime.strptime("2020-01-01", date_format),
                                    min_value=datetime.strptime("1998-01-02", date_format),
                                    max_value=datetime.strptime("2023-12-31", date_format))
    with col3:
        ib_end_dt = st.date_input("End Date",
                                  datetime.strptime("2023-12-31", date_format),
                                  min_value=datetime.strptime("1998-01-02", date_format),
                                  max_value=datetime.strptime("2023-12-31", date_format))

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        btn_ts = st.button('Get Time Series Data')

    # Button to fetch data
    if btn_ts:
        with st.spinner(f"Fetching data for {ib_ticker}..."):

            # Get stock data
            params = {
                'start_date': ib_start_dt,
                'end_date': ib_end_dt
            }
            df_ts = request_data(ib_ticker, params)
            df_ts['ticker'] = ib_ticker
            plot_ts(df_ts)


menu()
hist_chart_main()
