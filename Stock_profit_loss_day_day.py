import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date

st.title("Advanced Stock Data Analyzer")

# Function to fetch comprehensive stock data
def fetch_stock_data(symbols, start_date, end_date):
    try:
        data = yf.download(
            symbols.split(','),
            start=start_date,
            end=end_date,
            group_by='ticker',
            progress=False,
            threads=True
        )
        
        if data.empty:
            st.error("No data found for the given symbols and date range")
            return None
            
        return data

    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

# Function to get additional fundamental data
def get_fundamentals(symbol):
    try:
        ticker = yf.Ticker(symbol)
        return {
            'info': ticker.info,
            'financials': ticker.financials,
            'balance_sheet': ticker.balance_sheet,
            'cashflow': ticker.cashflow,
            'recommendations': ticker.recommendations,
            'institutional_holders': ticker.institutional_holders
        }
    except Exception as e:
        st.error(f"Error getting fundamentals for {symbol}: {str(e)}")
        return None

# Main form
with st.form(key='stock_form'):
    col1, col2, col3 = st.columns(3)
    with col1:
        symbols = st.text_input("Enter symbols (comma-separated)", "AAPL,MSFT,GOOG")
    with col2:
        start_date = st.date_input("Start date", date(2020, 1, 1))
    with col3:
        end_date = st.date_input("End date", date.today())
    
    analysis_type = st.selectbox("Analysis Type", [
        "Historical Prices", 
        "Fundamental Data", 
        "Institutional Holdings",
        "Analyst Recommendations"
    ])
    
    submit_button = st.form_submit_button("Run Analysis")

# Process form submission
if submit_button:
    if start_date > end_date:
        st.error("End date must be after start date")
    else:
        with st.spinner('Analyzing data...'):
            if analysis_type == "Historical Prices":
                data = fetch_stock_data(symbols, start_date, end_date)
                if data is not None:
                    st.success("Found the following datasets:")
                    
                    # Show multi-ticker selection
                    symbols_list = symbols.split(',')
                    selected_symbol = st.selectbox("Select Symbol", symbols_list)
                    
                    # Show available metrics
                    metrics = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
                    selected_metrics = st.multiselect("Select Metrics", metrics, default='Close')
                    
                    # Display selected data
                    if len(symbols_list) > 1:
                        st.dataframe(data[selected_symbol][selected_metrics])
                    else:
                        st.dataframe(data[selected_metrics])
                        
            else:
                fundamental_data = get_fundamentals(symbols.split(',')[0])
                if fundamental_data:
                    if analysis_type == "Fundamental Data":
                        st.subheader("Financial Statements")
                        st.dataframe(fundamental_data['financials'])
                        
                    elif analysis_type == "Institutional Holdings":
                        st.subheader("Top Institutional Holders")
                        st.dataframe(fundamental_data['institutional_holders'])
                        
                    elif analysis_type == "Analyst Recommendations":
                        st.subheader("Analyst Recommendations History")
                        st.dataframe(fundamental_data['recommendations'])

# Reset button
if st.button("Reset Analysis"):
    st.experimental_rerun()

# Help section
with st.expander("Usage Instructions"):
    st.markdown("""
    - **Multiple Symbols**: Enter comma-separated tickers (e.g., `AAPL,MSFT,GOOG`)
    - **Historical Prices**: View OHLC data, volume, and adjusted close
    - **Fundamental Data**: See financial statements for individual companies
    - **Institutional Holdings**: View top institutional investors
    - **Analyst Recommendations**: See recent analyst ratings
    """)
