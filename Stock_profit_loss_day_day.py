import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date

st.title("Stock Data Fetcher")

# Create a form for user input
with st.form(key='stock_form'):
    symbols = st.text_input("Enter stock symbols (comma-separated)", "AAPL,GOOGL,MSFT")
    start_date = st.date_input("Start date", date(2025, 1, 1))
    end_date = st.date_input("End date", date.today())
    submit_button = st.form_submit_button(label='Fetch Data')

# Function to fetch stock data
def fetch_stock_data(symbols, start_date, end_date):
    data = yf.download(symbols.split(','), start=start_date, end=end_date)
    return data['Adj Close']

# Display data when form is submitted
if submit_button:
    with st.spinner('Fetching data...'):
        df = fetch_stock_data(symbols, start_date, end_date)
    st.success('Data fetched successfully!')
    st.dataframe(df)

# Button for new analysis
if st.button('New Analysis'):
    st.experimental_rerun()
