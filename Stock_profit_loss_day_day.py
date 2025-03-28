import streamlit as st
import yfinance as yf
import pandas as pd

# Function to fetch stock data for given symbols and date range
def get_stock_data(symbols, start_date, end_date):
    stock_data = {}
    for symbol in symbols:
        stock_data[symbol] = yf.download(symbol, start=start_date, end=end_date)
    return stock_data

# Streamlit app
def main():
    # Title of the Streamlit app
    st.title("Stock Data Analysis")

    # Input fields for the stock symbols, start date, and end date
    with st.form("stock_form", clear_on_submit=True):
        st.subheader("Enter Stock Details")

        # Input for multiple stock symbols (comma-separated)
        symbols_input = st.text_input("Enter Stock Symbols (comma-separated)", "AAPL, MSFT, TSLA")
        symbols = [symbol.strip() for symbol in symbols_input.split(",")]

        # Input for start date and end date
        start_date = st.date_input("Start Date", pd.to_datetime("2020-01-01"))
        end_date = st.date_input("End Date", pd.to_datetime("2021-01-01"))

        # Submit button
        submit_button = st.form_submit_button("Fetch Data")

        if submit_button:
            if symbols_input:
                st.write(f"Fetching data for symbols: {', '.join(symbols)} from {start_date} to {end_date}")
                stock_data = get_stock_data(symbols, start_date, end_date)
                
                # Display the fetched stock data
                for symbol, data in stock_data.items():
                    st.write(f"### {symbol} Stock Data")
                    st.dataframe(data)
            else:
                st.warning("Please enter valid stock symbols.")

    # New Analysis button to refresh the screen
    if st.button("New Analysis"):
        st.experimental_rerun()

# Run the app
if __name__ == "__main__":
    main()
