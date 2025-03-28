import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date

st.title("Stock Data Fetcher")

# Function to fetch stock data
def fetch_stock_data(symbols, start_date, end_date):
    try:
        data = yf.download(symbols.split(','), start=start_date, end=end_date)
        st.write("Available columns:", data.columns)  # Debug info
        if 'Adj Close' in data.columns:
            return data['Adj Close']
        elif 'Close' in data.columns:
            return data['Close']
        else:
            st.error("Neither 'Adj Close' nor 'Close' columns found in the data.")
            return None
    except Exception as e:
        st.error(f"An error occurred while fetching data: {str(e)}")
        return None

# Create a form for user input
with st.form(key='stock_form'):
    symbols = st.text_input("Enter stock symbols (comma-separated)", "AAPL,GOOGL,MSFT")
    start_date = st.date_input("Start date", date(2020, 1, 1))
    end_date = st.date_input("End date", date.today())
    submit_button = st.form_submit_button(label='Fetch Data')

# Display data when form is submitted
if submit_button:
    with st.spinner('Fetching data...'):
        df = fetch_stock_data(symbols, start_date, end_date)
    if df is not None and not df.empty:
        st.success('Data fetched successfully!')
        st.dataframe(df)
    else:
        st.warning('No data available for the given symbols and date range.')

# Button for new analysis
if st.button('New Analysis'):
    st.experimental_rerun()

# Display some information about using the app
st.markdown("""
## How to use this app:
1. Enter stock symbols separated by commas (e.g., AAPL,GOOGL,MSFT)
2. Select a start date and end date for the data range
3. Click 'Fetch Data' to retrieve the stock information
4. Use 'New Analysis' to clear the form and start over
""")
