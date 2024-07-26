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

def get_historical_data(symbol):
    # Fetch the historical data for a stock
    ticker = yf.Ticker(symbol)
    history = ticker.history(period="max")
    
    # Display the ticker symbol, earliest and latest available dates
    st.write(f"Ticker symbol: {ticker.info['symbol']}")
    st.write(f"History Data available from: {history.index[0]} to: {history.index[-1]}")
    #st.write(f"History Data available to: {history.index[-1]}")
    
    return history

def get_stock_data(symbol, start_date, end_date):
    # Download the historical data
    data = yf.download(symbol, start=start_date, end=end_date)
    # Reset the index to have 'Date' as a column
    data.reset_index(inplace=True)
    return data

def calculate_profit_loss(data):
    # Calculate the profit/loss for each day
    data['Profit-Loss'] = data['Close'] - data['Open']
    return data

def format_data(data):
    # Format date to remove time
    data['Date'] = data['Date'].dt.date
    # Round all float columns to 2 decimal places
    float_columns = ['Open', 'High', 'Low', 'Close', 'Profit-Loss']
    data[float_columns] = data[float_columns].round(2)
    
    # Color formatting based on profit/loss
    def color_profit_loss(val):
        if val >= 0:
            return 'background-color: #7FFF7F'  # light green for profit
        else:
            return 'background-color: #FF7F7F'  # light red for loss
    
    # Apply color formatting to entire DataFrame
    formatted_data = data.style.applymap(color_profit_loss, subset=['Profit-Loss'])
    
    return formatted_data

def create_candlestick_chart(data, symbol):
    fig = go.Figure(data=[go.Candlestick(
        x=data['Date'],
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close']
    )])
    fig.update_layout(title=f'{symbol} Stock Price',
                      xaxis_title='Date',
                      yaxis_title='Price',
                      xaxis_rangeslider_visible=False)
    st.plotly_chart(fig)

def main():
    st.title('Stock Data Analysis')

    # User inputs
    symbols_input = st.text_input('Enter stock symbols (comma-separated)', 'AAPL,GOOGL,MSFT')
    symbols = [symbol.strip() for symbol in symbols_input.split(',')]
    start_date = st.date_input('Start Date', value=pd.to_datetime('2024-01-01'))
    end_date = st.date_input('End Date', value=pd.to_datetime('2024-07-11'))

    if st.button('Show Results'):
        show_results_clicked = True
        for symbol in symbols:
            # Get the historical data and display info
            history = get_historical_data(symbol)            
            # Get the stock data
            stock_data = get_stock_data(symbol, start_date, end_date)

            if not stock_data.empty:
                # Calculate profit/loss
                stock_data_with_profit_loss = calculate_profit_loss(stock_data)

                # Format data with color coding
                formatted_data = format_data(stock_data_with_profit_loss)

                # Display results for each symbol
                st.subheader(f'{symbol} Stock Data')
                st.dataframe(formatted_data, width=800, height=400)

                # Create candlestick chart
                create_candlestick_chart(stock_data_with_profit_loss, symbol)

    # Show "New Analysis" button only if "Show Results" button has been clicked
    if 'show_results_clicked' in locals() and show_results_clicked:
        if st.button('New Analysis'):
            st.experimental_rerun()

if __name__ == "__main__":
    main()

