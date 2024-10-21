import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px

# Function to fetch stock data
def fetch_stock_data(tickers):
    data = {}
    
    for ticker in tickers:
        if not ticker:  # Skip empty tickers
            continue

        try:
            # Fetch historical data for the last year
            df = yf.download(ticker, period="1y")
            if df.empty:
                st.warning(f"No data returned for {ticker}. Please check the ticker symbol.")
                continue

            # Calculate daily returns
            df['Daily Return'] = df['Close'].pct_change()
            # Calculate total return
            total_return = (df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]
            # Calculate volatility (standard deviation of daily returns)
            volatility = df['Daily Return'].std() * np.sqrt(252)  # Annualized volatility
            # Get the last date and today's date
            last_date = df.index[-1].date()
            today = pd.Timestamp.today().date()

            if last_date == today:
                # Use today's open price if available
                today_open_price = df['Open'].iloc[-1]
            elif last_date < today:
                # If today's data is not available, use yesterday's adjusted close price
                today_open_price = df['Adj Close'].iloc[-1] if len(df) > 0 else None
            else:
                today_open_price = None
                
            data[ticker] = {
                'Total Return': total_return,
                'Volatility': volatility,
                'Last Performance': df['Daily Return'].iloc[-1],
                'Today Open Price': today_open_price  # Store the relevant price
            }
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")
    
    return data

# Investment evaluation logic
def evaluate_investment(performance):
    total_return = performance['Total Return']
    volatility = performance['Volatility']
    sharpe_ratio = total_return / volatility if volatility != 0 else np.nan

    if total_return > 0.2:  # Example threshold: 20% return
        decision = "Strong Buy"
    elif total_return > 0.1:  # 10% to 20% return
        decision = "Buy"
    elif total_return > 0:  # Positive return
        decision = "Hold"
    else:
        decision = "Sell"

    return decision, sharpe_ratio

st.title("Stock Performance Evaluation")

tickers_input = st.text_input("Enter stock tickers (comma-separated)", "AAPL, MSFT, GOOGL, NVDA, MU, TSLA")
tickers = [ticker.strip() for ticker in tickers_input.split(',')]

if st.button("Analyze"):
    performance_data = fetch_stock_data(tickers)
    
    # Check if any valid performance data was fetched
    if performance_data:
        # Create a DataFrame for the performance data
        performance_df = pd.DataFrame.from_dict(performance_data, orient='index')

        # Ensure the Total Return column is numeric
        performance_df['Total Return'] = pd.to_numeric(performance_df['Total Return'], errors='coerce')

        # Drop rows with NaN values in Total Return
        performance_df.dropna(subset=['Total Return'], inplace=True)

        performance_df['Investment Decision'], performance_df['Sharpe Ratio'] = zip(*performance_df.apply(evaluate_investment, axis=1))

        # Create a collapsible table for performance data
        with st.expander("View Performance Data", expanded=True):
            st.write(performance_df)

        # Create a bar chart for total return
        if not performance_df.empty:
            bar_fig = px.bar(
                performance_df,
                x=performance_df.index,
                y='Total Return',
                title="Stock Total Return (Last 1 Year)",
                labels={"Total Return": "Total Return"},
                color='Total Return',
                color_continuous_scale=px.colors.sequential.Viridis
            )
            st.plotly_chart(bar_fig)

            # Sunburst Chart
            sunburst_fig = px.sunburst(
                performance_df.reset_index(),
                path=['index'],  # Use the index (tickers) for the path
                values='Total Return',
                title="Stock Total Return Distribution",
                color='Total Return',
                color_continuous_scale=px.colors.sequential.Viridis
            )
            st.plotly_chart(sunburst_fig)
        else:
            st.warning("No valid performance data to display.")
    else:
        st.warning("No performance data available.")

