import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

def get_stock_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    data.reset_index(inplace=True)
    return data

def format_data(data):
    # Ensure 'Date' is in date format (remove time part if present)
    data['Date'] = pd.to_datetime(data['Date']).dt.date
    
    # Define columns to be displayed and rounded
    display_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    float_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close']
    
    # Round numerical columns to 3 decimal places
    data[float_columns] = data[float_columns].round(3)
    
    # Format Volume as integer
    data['Volume'] = data['Volume'].astype(int)
    
    return data[display_columns]

def create_candlestick_chart(data, symbol):
    fig = go.Figure(data=[go.Candlestick(
        x=data['Date'],
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Candlestick'
    )])

    fig.update_layout(
        title=f'{symbol} Stock Price',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False
    )

    return fig

def main():
    st.title('Stock Data Analysis')

    st.sidebar.header('User Input')
    symbols_input = st.sidebar.text_input('Enter stock symbols (comma-separated)', 'AAPL,GOOGL,MSFT')
    symbols = [symbol.strip() for symbol in symbols_input.split(',')]
    start_date = st.sidebar.date_input('Start Date', value=pd.to_datetime('2024-01-01'))
    end_date = st.sidebar.date_input('End Date', value=datetime.now().date() + timedelta(days=1))

    if st.sidebar.button('Show Results'):
        for symbol in symbols:
            stock_data = get_stock_data(symbol, start_date, end_date)

            if not stock_data.empty:
                formatted_data = format_data(stock_data)

                st.subheader(f'{symbol} Stock Data')
                st.dataframe(formatted_data, use_container_width=True)

                fig = create_candlestick_chart(stock_data, symbol)
                st.plotly_chart(fig)

    if st.sidebar.button('New Analysis'):
        st.experimental_rerun()

if __name__ == "__main__":
    main()
