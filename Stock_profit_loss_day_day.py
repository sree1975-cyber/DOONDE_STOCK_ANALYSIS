"""
This Stock Data Analysis tool retrieves historical stock data from Yahoo Finance,
calculates daily profit/loss for selected stocks, and visualizes the data with
color-coded formatting. It also provides interactive candlestick charts using Plotly
to help users analyze stock price movements over specified time periods.
"""
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Helper function to color the profit/loss and end_result columns
def color_profit_loss(val):
    color = 'green' if val > 0 else 'red' if val < 0 else 'black'
    return f'color: {color}'

def get_historical_data(symbol):
    ticker = yf.Ticker(symbol)
    history = ticker.history(period="max")
    
    st.write(f"**Ticker symbol**: {ticker.info['symbol']}")
    st.write(f"**History Data available from**: {history.index[0].strftime('%Y-%m-%d')} to {history.index[-1].strftime('%Y-%m-%d')}")
    
    return history

def get_stock_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    data.reset_index(inplace=True)
    return data

def calculate_profit_loss(data):
    data['Profit-Loss'] = data['Close'] - data['Open']
    return data

def calculate_adj_open(data):
    # Ensure 'Adj Close' and 'Open' columns exist
    if 'Adj Close' not in data.columns:
        raise ValueError("'Adj Close' column is missing in the DataFrame")
    if 'Open' not in data.columns:
        raise ValueError("'Open' column is missing in the DataFrame")

    # Calculate Adj/Open as the difference between the previous day's Adj Close and the current day's Open
    data['Adj/Open'] = data['Open'] - data['Adj Close'].shift(1)
    
    return data


def add_end_result(data):
    data['End_Result'] = data['Adj/Open'] + data['Profit-Loss']
    return data

def format_data(data):
    # Ensure 'Date' is in date format (remove time part if present)
    data['Date'] = pd.to_datetime(data['Date']).dt.date
    
    # Define columns to be rounded
    float_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Profit-Loss', 'Adj/Open', 'End_Result']
    
    # Convert columns to numeric types if they aren't already
    for col in float_columns:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')  # Ensure the column is numeric
    
    # Round numerical columns to 3 decimal places
    data[float_columns] = data[float_columns].applymap(lambda x: round(x, 3) if pd.notnull(x) else x)

     # Apply color formatting to the 'Profit-Loss' 'Adj/Open' and 'End_Result' columns
    styled_data = data.style.applymap(color_profit_loss, subset=['Profit-Loss', 'Adj/Open','End_Result'])

     # Ensure that the formatted table displays values with 3 decimal places
    styled_data = styled_data.format(subset=float_columns, formatter="{:.3f}")
    
    return styled_data

def create_candlestick_chart(data, symbol):
    # Calculate moving averages
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    data['EMA20'] = data['Close'].ewm(span=20, adjust=False).mean()

    # Create the candlestick chart
    fig = go.Figure()

    # Add candlestick trace
    fig.add_trace(go.Candlestick(
        x=data['Date'],
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Candlestick'
    ))

    # Add SMA trace
    fig.add_trace(go.Scatter(
        x=data['Date'],
        y=data['SMA20'],
        mode='lines',
        name='SMA 20',
        line=dict(color='blue')
    ))

    # Add EMA trace
    fig.add_trace(go.Scatter(
        x=data['Date'],
        y=data['EMA20'],
        mode='lines',
        name='EMA 20',
        line=dict(color='red')
    ))

    fig.update_layout(
        title=f'{symbol} Stock Price with Moving Averages',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        ),
        yaxis=dict(
            fixedrange=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Add hover text to traces
    fig.update_traces(
        hovertext=data.apply(lambda row: f"Date: {row['Date']}<br>Open: {row['Open']:.3f}<br>High: {row['High']:.3f}<br>Low: {row['Low']:.3f}<br>Close: {row['Close']:.3f}<br>Profit-Loss: {row['Profit-Loss']:.3f}<br>Adj/Open: {row['Adj/Open']:.3f}<br>End_Result: {row['End_Result']:.3f}<br>SMA20: {row['SMA20']:.3f}<br>EMA20: {row['EMA20']:.3f}", axis=1),
        hoverinfo="text"
    )

    return fig


def main():
    st.title('Stock Data Analysis')

    st.sidebar.header('User Input')
    symbols_input = st.sidebar.text_input('Enter stock symbols (comma-separated)', 'AAPL,GOOGL,MSFT')
    symbols = [symbol.strip() for symbol in symbols_input.split(',')]
    start_date = st.sidebar.date_input('Start Date', value=pd.to_datetime('2024-01-01'))
    #end_date = st.sidebar.date_input('End Date', value=pd.to_datetime('2024-07-11'))
    #end_date = st.sidebar.date_input('End Date', value=datetime.now().date())
    end_date = st.sidebar.date_input('End Date', value=datetime.now().date() + timedelta(days=1))
    
    # Initialize the variable
    show_results_clicked = False

    if st.sidebar.button('Show Results'):
        show_results_clicked = True

    if show_results_clicked:
        for symbol in symbols:
            history = get_historical_data(symbol)
            stock_data = get_stock_data(symbol, start_date, end_date)

            if not stock_data.empty:
                stock_data = calculate_profit_loss(stock_data)
                stock_data = calculate_adj_open(stock_data)
                stock_data = add_end_result(stock_data)

                formatted_data = format_data(stock_data)

                st.subheader(f'{symbol} Stock Data')
                #st.dataframe(formatted_data, width=1200, height=400)
                st.dataframe(formatted_data, use_container_width=True)  # Ensure the table uses available width
                      
                fig = create_candlestick_chart(stock_data, symbol)
                st.plotly_chart(fig)

                                  
    if st.sidebar.button('New Analysis'):
        # Show "New Analysis" button only if "Show Results" button has been clicked
        if show_results_clicked:
            # Clear the session state and refresh the app
            st.session_state.clear()
            st.experimental_rerun()  # Ensure this line is compatible with your Streamlit version

if __name__ == "__main__":
    main()


