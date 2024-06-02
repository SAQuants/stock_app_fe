# pip list --format=freeze > requirements.txt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import requests
import io
import streamlit as st
from navigation import menu, algo_header, backend_url

st.set_page_config(page_title=algo_header, page_icon=':bar_chart:')
st.subheader("Backtesting page")


def extract_backtest_results(response_dict):
    df_order_plot = pd.read_json(io.StringIO(response_dict['df_order_plot']))
    # print(df_order_plot.columns)
    df_order_plot.set_index('Time', inplace=True)

    df_analytics = pd.read_json(io.StringIO(response_dict['df_analytics']))
    # print(df_analytics.columns)
    df_analytics.set_index('Time', inplace=True)

    return df_order_plot, df_analytics


def request_data(symbol, params):
    # stock_data = yf.download(ticker, start=start_date, end=end_date)
    # stock_data = pd.read_json(io.StringIO(json_str))
    res = requests.get(f"{backend_url}/symbol/{symbol}", params=params)
    # print(f'res: {res}, res.json(): {res.json()}')
    if res.status_code != 200:
        print(res, res.text)
        return res.text

    response_dict = res.json()
    if 'backtest' in params:
        df_order_plot, df_analytics = extract_backtest_results(response_dict)
        return df_order_plot, df_analytics


def plot_trades(df_res):
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

    ticker = df_res["trade_symbol"].iloc[0]
    # enable the events trace to show collective information and display line on hover
    # https://stackoverflow.com/questions/73082731/plotly-adding-custom-markers-and-events-to-xaxis-points
    fig.update_layout(hovermode="x unified", title=f"{ticker} Backtest Results")
    # st.plotly_chart(fig)
    return fig


def plot_pnl(df_res):
    # plotly setup
    # https://plotly.com/python/multiple-axes/
    # Create figure with secondary y-axis
    fig_pnl = make_subplots(specs=[[{"secondary_y": True}]])

    fig_pnl.add_trace(go.Scatter(x=df_res.index, y=df_res['total_pnl'],
                             mode='lines', line=dict(color='#3366CC'), name='P&L'),
                  secondary_y=False)
    df_res['total_pnl_perc'] = df_res['total_pnl_perc'].mul(100).round(2)
    fig_pnl.add_trace(go.Scatter(x=df_res.index, y=df_res['total_pnl_perc'],
                             mode='lines', line=dict(color='rgb(241,226,204)'), name='P&L Percentage'),
                  secondary_y=True)

    # Set x-axis title
    fig_pnl.update_xaxes(title_text="Time")

    # Set y-axes titles
    fig_pnl.update_yaxes(title_text="<b>P&L</b>", secondary_y=False)
    fig_pnl.update_yaxes(title_text="<b>P&L Percentage</b>", secondary_y=True)

    fig_pnl.update_layout(hovermode="x unified", title=f"Trade P&L")
    fig_pnl.update_layout(yaxis2={"tickformat": ", .0 %"})
    # st.plotly_chart(fig)
    return fig_pnl


def plot_drawdown(df_res):
    # plotly setup
    # https://plotly.com/python/multiple-axes/
    fig_dd = make_subplots(specs=[[{"secondary_y": True}]])

    fig_dd.add_trace(go.Scatter(x=df_res.index, y=df_res['drawdown'],
                             mode='lines', line=dict(color='#3366CC'), name='Drawdown'),
                  secondary_y=False)
    df_res['drawdown_perc'] = df_res['drawdown_perc'].mul(100).round(2)
    fig_dd.add_trace(go.Scatter(x=df_res.index, y=df_res['drawdown_perc'],
                             mode='lines', line=dict(color='rgb(241,226,204)'), name='Drawdown Percentage'),
                  secondary_y=True)

    # Set x-axis title
    fig_dd.update_xaxes(title_text="Time")

    # Set y-axes titles
    fig_dd.update_yaxes(title_text="<b>Drawdown</b>", secondary_y=False)
    fig_dd.update_yaxes(title_text="<b>Drawdown Percentage</b>", secondary_y=True)

    fig_dd.update_layout(hovermode="x unified", title=f"Drawdown")
    fig_dd.update_layout(yaxis2={"tickformat": ", .0 %"})
    # st.plotly_chart(fig)
    return fig_dd

def backtest_main():
    # st.subheader('Backtest run results')

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
                                    datetime.strptime("2020-01-01", date_format),
                                    min_value=datetime.strptime("1998-01-02", date_format),
                                    max_value=datetime.strptime("2023-12-31", date_format))
    with col3:
        ib_end_dt = st.date_input("End Date",
                                  datetime.strptime("2023-12-31", date_format),
                                  min_value=datetime.strptime("1998-01-02", date_format),
                                  max_value=datetime.strptime("2023-12-31", date_format))
    with col4:
        ib_backtest = st.selectbox("Select Backtest", df_backtests['backtest'])

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        btn_bt = st.button('Perform BackTest')

    if btn_bt:
        with st.spinner(f"Performing backtest for {ib_ticker}..."):
            params = {
                'start_date': ib_start_dt,
                'end_date': ib_end_dt,
                'backtest': ib_backtest
            }
            df_order_plot, df_analytics = request_data(ib_ticker, params)
            df_order_plot['trade_symbol'] = ib_ticker
            # Display the data
            tab1, tab2, tab3 = st.tabs(["Trades", "Trade PnL", "Trade Drawdown"])

            with tab1:
                fig_orders = plot_trades(df_order_plot)
                st.plotly_chart(fig_orders)
                st.write("**Order Table**")
                st.dataframe(df_order_plot[df_order_plot['FillQuantity'].notnull()],
                             use_container_width=True,
                             column_config={
                                 "Price": st.column_config.NumberColumn(format='%.2f')
                                 , "bb-MiddleBand": st.column_config.NumberColumn(format='%.2f')
                                 , "bb-UpperBand": st.column_config.NumberColumn(format='%.2f')
                                 , "bb-LowerBand": st.column_config.NumberColumn(format='%.2f')
                                 , "Benchmark": st.column_config.NumberColumn(format='%.2f')
                             }
                             )

            with tab2:
                fig_pnl = plot_pnl(df_analytics)
                st.plotly_chart(fig_pnl)
                st.write("**PnL Table**")
                st.dataframe(df_analytics[['total_portfolio_value', 'total_pnl', 'total_pnl_perc']],
                             use_container_width=True,
                             column_config={
                                 "total_portfolio_value": st.column_config.NumberColumn(step=0)
                                 , "total_pnl": st.column_config.NumberColumn(step=0)
                                 , "total_pnl_perc": st.column_config.NumberColumn(format='%.2f%%')
                             }
                             )
            with tab3:
                fig_dd = plot_drawdown(df_analytics)
                st.plotly_chart(fig_dd)
                st.write("**Drawdown Table**")
                st.dataframe(df_analytics[['total_portfolio_value', 'drawdown', 'drawdown_perc']],
                             use_container_width=True,
                             column_config={
                                 "total_portfolio_value": st.column_config.NumberColumn(step=0)
                                 , "drawdown": st.column_config.NumberColumn(step=0)
                                 , "drawdown_perc": st.column_config.NumberColumn(format='%.2f%%')
                             }
                             )


menu()
backtest_main()

# # if __name__ == "__main__":
# #    backtest_main()
