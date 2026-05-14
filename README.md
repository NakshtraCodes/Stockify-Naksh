# StockSense

A modern, real-time stock market tracking application built with Streamlit and Yahoo Finance.

## Features
- Real-time stock tracking with OHLCV data
- Interactive charts via Plotly (Candlestick, Volume)
- Technical Indicators (RSI, MACD)
- Multi-stock performance comparison
- Dynamic Watchlist saved to session state
- Latest news feed
- Data export (CSV)

## Setup Instructions

1. **Clone the repository**
2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application**
   ```bash
   streamlit run app.py
   ```

## Technologies
- Streamlit
- yfinance
- Plotly
- Pandas
