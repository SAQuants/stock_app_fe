# pip list --format=freeze > requirements.txt
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
import io

backend_url = 'http://vm4lean.northeurope.cloudapp.azure.com:8080' # 'http://127.0.0.1:8000'
# streamlit run front_end/frontend_streamlit.py


def extract_timeseries(response_dict):
    df_stock_ts = pd.read_json(io.StringIO(response_dict))  # pd.read_json(res.json())#
    df_stock_ts['Date'] = df_stock_ts['Date'].dt.date
    df_stock_ts.set_index('Date', inplace=True)
    return df_stock_ts


def extract_backtest_results(response_dict):
    # stock_data = pd.read_json(response_dict['df_op'])
    order_plot_path = response_dict['output_dir'] + '/df_order_plot.csv'
    df_op = pd.read_csv(order_plot_path)
    df_op.set_index('Time', inplace=True)
    timeseries_path = response_dict['output_dir'] + '/df_timeseries.csv'
    df_ts = pd.read_csv(timeseries_path)
    df_ts.set_index('Time', inplace=True)
    df_res = df_ts.merge(df_op, left_index=True, right_index=True)
    df_res = pd.concat([df_ts,df_op], axis=1)
    df_res.drop(columns=['OrderID', 'Status', 'Quantity', 'OrderFee', 'FillPrice'], inplace=True)
    return df_res


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
    else:
        df_res = extract_backtest_results(response_dict)

    return df_res


def plot_ts(df_ts):
    # Plot the closing price using Plotly
    ticker = df_ts["ticker"].iloc[0]
    fig = px.line(df_ts, x=df_ts.index, y='Close', title=f'{ticker} Stock Price')
    st.plotly_chart(fig)


def plot_backtest(df_res):
    # plotly setup
    # https://stackoverflow.com/questions/69901909/how-to-add-datapoints-to-a-time-series-line-plot-to-highlight-events
    fig = go.Figure()
    # colors https://plotly.com/python/discrete-color/
    fig.add_trace(go.Scatter(x=df_res.index, y=df_res['Price'],
                             mode='lines', line=dict(color='#3366CC'), name='Price'))
    fig.add_trace(go.Scatter(x=df_res.index, y=df_res['bb-MiddleBand'],
                             mode='lines', line=dict(color='rgb(203,213,232)'), name='MiddleBand'))
    fig.add_trace(go.Scatter(x=df_res.index, y=df_res['bb-UpperBand'],
                             mode='lines', line=dict(color='rgb(179,226,205)'), name='UpperBand'))
    fig.add_trace(go.Scatter(x=df_res.index, y=df_res['bb-LowerBand'],
                             mode='lines', line=dict(color='rgb(241,226,204)'), name='LowerBand'))
    sell_filter = (df_res['FillQuantity'] < 0)
    fig.add_trace(go.Scatter(x=df_res.loc[sell_filter].index, y=df_res.loc[sell_filter]['Price'],
                             mode='markers', marker=dict(symbol='triangle-down', color='red', size=18),
                             name='Sell'))

    buy_filter = (df_res['FillQuantity'] > 0)
    fig.add_trace(go.Scatter(x=df_res.loc[buy_filter].index, y=df_res.loc[buy_filter]['Price'],
                             mode='markers', marker=dict(symbol='triangle-up', color='green', size=18),
                             name='Buy'))

    ticker = df_res["ticker"].iloc[0]
    # enable the events trace to show collective information and display line on hover
    # https://stackoverflow.com/questions/73082731/plotly-adding-custom-markers-and-events-to-xaxis-points
    fig.update_layout(hovermode="x unified", title=f"{ticker} Backtest Results")
    st.plotly_chart(fig)


def main():
    st.title("Algo Trading Interface v0.1")

    # User input for stock ticker
    resp_symbols = requests.get(backend_url+'/symbols')
    if resp_symbols.status_code != 200:
        print(resp_symbols, resp_symbols.text)
        return
    # print(resp_symbols.json())
    df_symbol = pd.DataFrame(resp_symbols.json())

    resp_backtests = requests.get(backend_url+'/backtests')
    if resp_backtests.status_code != 200:
        print(resp_backtests, resp_backtests.text)
        return
    df_backtests = pd.DataFrame(resp_backtests.json())
    # print(df_backtests['backtest'].values)

    date_format = "%Y-%m-%d"
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        ib_ticker = st.selectbox("Select Stock Ticker", df_symbol['symbol'])
    with col2:
        ib_start_dt = st.date_input("Start Date",
                                    datetime.strptime("2018-01-01", date_format),
                                    min_value=datetime.strptime("1998-01-02", date_format),
                                    max_value=datetime.strptime("2021-03-31", date_format))
    with col3:
        ib_end_dt = st.date_input("End Date",
                                  datetime.strptime("2021-01-31", date_format),
                                  min_value=datetime.strptime("1998-01-02", date_format),
                                  max_value=datetime.strptime("2021-03-31", date_format))
    with col4:
        ib_backtest = st.selectbox("Select Backtest", df_backtests['backtest'])

    col1, col2, col3, col4 = st.columns([1, 1, 1,1])
    with col1:
        btn_ts = st.button('Get Time Series Data')
    with col4:
        btn_bt = st.button('Perform BackTest')

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

    if btn_bt:
        with st.spinner(f"Performing backtest for {ib_ticker}..."):
            params = {
                'start_date': ib_start_dt,
                'end_date': ib_end_dt,
                'backtest': ib_backtest
            }
            df_res = request_data(ib_ticker, params)
            df_res['ticker'] = ib_ticker
            # Display the data
            plot_backtest(df_res)


if __name__ == "__main__":
    main()
