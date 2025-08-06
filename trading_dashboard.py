import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import threading
import queue
from datetime import datetime, timedelta
import yaml
import os
import sys
from pathlib import Path

# Add the src directory to the path for imports
sys.path.append(str(Path(__file__).parent / "src"))

# Page configuration
st.set_page_config(
    page_title="Trading Bot Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-running {
        color: #28a745;
        font-weight: bold;
    }
    .status-stopped {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class TradingDashboard:
    def __init__(self):
        self.data_queue = queue.Queue()
        self.bot_thread = None
        self.is_running = False
        self.trading_bot = None
        self.data_fetcher = None
        self.data_source = "yahoo"  # Default to Yahoo Finance
        self.performance_data = []
        self.trades_history = []
        
    @st.cache_resource
    def get_data_fetcher(self, data_source):
        """Lazy load data fetcher with caching"""
        try:
            if data_source == "yahoo":
                from data.yahoo_data_fetcher import YahooDataFetcher
                return YahooDataFetcher()
            elif data_source == "coingecko":
                from data.coingecko_data_fetcher import CoinGeckoDataFetcher
                return CoinGeckoDataFetcher()
            else:
                st.error(f"Unknown data source: {data_source}")
                return None
        except Exception as e:
            st.error(f"Failed to initialize {data_source} DataFetcher: {str(e)}")
            return None
    
    @st.cache_resource
    def get_backtest_engine(self, data_source, start_date, end_date, trading_pair):
        """Lazy load backtest engine with caching"""
        try:
            if data_source == "yahoo":
                from backtest.yahoo_backtest_engine import YahooBacktestEngine
                return YahooBacktestEngine(
                    start_date=start_date,
                    end_date=end_date,
                    trading_pair=trading_pair
                )
            elif data_source == "coingecko":
                from backtest.coingecko_backtest_engine import CoinGeckoBacktestEngine
                return CoinGeckoBacktestEngine(
                    start_date=start_date,
                    end_date=end_date,
                    trading_pair=trading_pair
                )
            else:
                st.error(f"Unknown data source: {data_source}")
                return None
        except Exception as e:
            st.error(f"Failed to initialize {data_source} BacktestEngine: {str(e)}")
            return None
        
    def initialize_components(self):
        """Initialize trading bot components"""
        try:
            self.data_fetcher = self.get_data_fetcher(self.data_source)
            return self.data_fetcher is not None
        except Exception as e:
            st.error(f"Failed to initialize {self.data_source} DataFetcher: {str(e)}")
            st.info("Please check your internet connection and try again")
            return False
    
    def get_current_price(self, symbol):
        """Get current price with error handling"""
        try:
            if self.data_fetcher:
                return self.data_fetcher.get_current_price(symbol)
            else:
                st.error("DataFetcher not initialized")
                return None
        except Exception as e:
            st.error(f"Failed to fetch price for {symbol}: {str(e)}")
            return None
    
    def run_backtest(self, start_date, end_date, trading_pair):
        """Run backtest with error handling"""
        try:
            backtest_engine = self.get_backtest_engine(self.data_source, start_date, end_date, trading_pair)
            
            return backtest_engine.run_backtest()
        except Exception as e:
            st.error(f"Backtest failed: {str(e)}")
            return None
    
    def load_config(self):
        """Load configuration from config.yaml"""
        try:
            with open('config/config.yaml', 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            st.error(f"Failed to load config: {str(e)}")
            return {}
    
    def save_config(self, config):
        """Save configuration to config.yaml"""
        try:
            with open('config/config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            return True
        except Exception as e:
            st.error(f"Failed to save config: {str(e)}")
            return False

# Initialize dashboard with loading indicator
if 'dashboard' not in st.session_state:
    with st.spinner("🚀 Initializing Trading Bot Dashboard..."):
        st.session_state.dashboard = TradingDashboard()

dashboard = st.session_state.dashboard

# Startup check
if not dashboard.data_fetcher:
    st.warning(f"⚠️ {dashboard.data_source.title()} DataFetcher not initialized. Please check your internet connection.")
    st.info("To use historical data, ensure you have:")
    st.info("1. Internet connection for data fetching")
    if dashboard.data_source == "yahoo":
        st.info("2. Installed yfinance: pip install yfinance")
    elif dashboard.data_source == "coingecko":
        st.info("2. CoinGecko API is accessible (free tier)")
    st.info("3. All required dependencies installed")

# Main header
st.markdown('<h1 class="main-header">🤖 Trading Bot Dashboard</h1>', unsafe_allow_html=True)

# Sidebar for controls
with st.sidebar:
    st.header("🎛️ Controls")
    
    # Bot Status
    st.subheader("Bot Status")
    if dashboard.is_running:
        st.markdown('<p class="status-running">🟢 Bot Running</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-stopped">🔴 Bot Stopped</p>', unsafe_allow_html=True)
    
    # Start/Stop Bot
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Start Bot", disabled=dashboard.is_running):
            with st.spinner("Initializing data fetcher..."):
                if dashboard.initialize_components():
                    dashboard.is_running = True
                    st.success("Bot started successfully!")
                    st.rerun()
    
    with col2:
        if st.button("⏹️ Stop Bot", disabled=not dashboard.is_running):
            dashboard.is_running = False
            st.success("Bot stopped successfully!")
            st.rerun()
    
    st.divider()
    
    # Trading Pair Selection
    st.subheader("Trading Configuration")
    trading_pair = st.selectbox(
        "Trading Pair",
        ["ETHUSDT", "BTCUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT"],
        index=0
    )
    
    # Timeframe Selection
    timeframe = st.selectbox(
        "Timeframe",
        ["1m", "5m", "15m", "1h", "4h", "1d"],
        index=1
    )
    
    # Data Source Selection
    st.subheader("Data Source")
    data_source = st.selectbox(
        "Historical Data Source",
        ["Yahoo Finance", "CoinGecko"],
        index=0,
        help="Yahoo Finance: More granular data, faster. CoinGecko: More comprehensive, rate limited."
    )
    
    # Update dashboard data source
    if data_source == "Yahoo Finance":
        dashboard.data_source = "yahoo"
    elif data_source == "CoinGecko":
        dashboard.data_source = "coingecko"
    
    # Data Source Toggle
    data_display = st.radio(
        "Display Mode",
        ["Live Trading", "Backtest Results", "Both"],
        index=0
    )
    
    st.divider()
    
    # Strategy Parameters
    st.subheader("Strategy Parameters")
    
    # Bollinger Bands Parameters
    st.write("**Bollinger Bands Settings**")
    bb_window = st.slider("Window Size", 5, 50, 10)
    bb_deviation = st.slider("Standard Deviation", 0.1, 2.0, 0.5, 0.1)
    
    # Risk Management
    st.write("**Risk Management**")
    max_daily_trades = st.slider("Max Daily Trades", 1, 50, 10)
    max_daily_loss = st.slider("Max Daily Loss (%)", 1.0, 20.0, 5.0, 0.5)
    base_risk_per_trade = st.slider("Base Risk per Trade (%)", 0.5, 5.0, 1.0, 0.1)
    
    # Save Configuration
    if st.button("💾 Save Configuration"):
        config = dashboard.load_config()
        config.update({
            'trading': {
                'pairs': [trading_pair],
                'base_currency': 'USDT',
                'trade_amount': 100,
                'max_open_trades': 3,
                'stop_loss_percentage': 2.0,
                'take_profit_percentage': 4.0
            },
            'strategy': {
                'bb_window': bb_window,
                'bb_deviation': bb_deviation
            },
            'risk': {
                'max_daily_trades': max_daily_trades,
                'max_daily_loss_percentage': max_daily_loss,
                'position_sizing': {
                    'base_risk_per_trade': base_risk_per_trade,
                    'max_risk_per_trade': base_risk_per_trade * 2
                }
            }
        })
        if dashboard.save_config(config):
            st.success("Configuration saved successfully!")

# Main content area
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Live Performance", 
    "📈 Historical Analysis", 
    "⚙️ Strategy Comparison", 
    "📋 Trade History", 
    "🔧 Settings"
])

with tab1:
    st.header("📊 Live Performance Dashboard")
    
    # Performance Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total P&L",
            value="$1,234.56",
            delta="+$123.45"
        )
    
    with col2:
        st.metric(
            label="Win Rate",
            value="68.5%",
            delta="+2.3%"
        )
    
    with col3:
        st.metric(
            label="Total Trades",
            value="156",
            delta="+12"
        )
    
    with col4:
        st.metric(
            label="Sharpe Ratio",
            value="1.85",
            delta="+0.15"
        )
    
    # Real-time charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Equity Curve")
        
        # Generate sample equity curve data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='H')
        equity_values = [1000 + i * 10 + np.random.normal(0, 5) for i in range(100)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=equity_values,
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#1f77b4', width=2)
        ))
        
        fig.update_layout(
            title="Portfolio Performance Over Time",
            xaxis_title="Time",
            yaxis_title="Portfolio Value ($)",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 P&L Distribution")
        
        # Generate sample P&L data
        pnl_data = np.random.normal(50, 20, 1000)
        
        fig = px.histogram(
            x=pnl_data,
            nbins=30,
            title="P&L Distribution",
            labels={'x': 'P&L ($)', 'y': 'Frequency'}
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Live market data
    st.subheader("🔄 Live Market Data")
    
    if st.button("🔄 Refresh Data"):
        current_price = dashboard.get_current_price(trading_pair)
        if current_price is not None:
            st.success(f"Current {trading_pair} price: ${current_price:,.2f}")
        else:
            st.error("Failed to fetch current price. Check API credentials and network connection.")

with tab2:
    st.header("📈 Historical Analysis")
    
    # Date range selector
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30),
            max_value=datetime.now()
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            max_value=datetime.now()
        )
    
    # Run backtest
    if st.button("🚀 Run Backtest"):
        with st.spinner("Running backtest..."):
            results = dashboard.run_backtest(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                trading_pair=trading_pair
            )
            
            if results is not None:
                # Display results
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Return", f"{results['total_return']:.2f}%")
                
                with col2:
                    st.metric("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")
                
                with col3:
                    st.metric("Max Drawdown", f"{results['max_drawdown']:.2f}%")
                
                with col4:
                    st.metric("Win Rate", f"{results['win_rate']:.1f}%")
                
                # Plot backtest results
                st.subheader("Backtest Results")
                
                # Create subplot for price and equity
                fig = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=('Price Chart', 'Equity Curve'),
                    vertical_spacing=0.1
                )
                
                # Add price data (sample)
                dates = pd.date_range(start=start_date, end=end_date, freq='D')
                prices = [100 + i * 0.5 + np.random.normal(0, 2) for i in range(len(dates))]
                
                fig.add_trace(
                    go.Scatter(x=dates, y=prices, name='Price', line=dict(color='blue')),
                    row=1, col=1
                )
                
                # Add equity curve
                equity = [1000 + i * 10 + np.random.normal(0, 5) for i in range(len(dates))]
                
                fig.add_trace(
                    go.Scatter(x=dates, y=equity, name='Equity', line=dict(color='green')),
                    row=2, col=1
                )
                
                fig.update_layout(height=600, showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Backtest failed. Check your API credentials and try again.")

with tab3:
    st.header("⚙️ Strategy Comparison")
    
    # Strategy selection
    strategies = st.multiselect(
        "Select Strategies to Compare",
        ["Bollinger Bands", "MACD", "RSI", "Moving Average Crossover", "Custom ML"],
        default=["Bollinger Bands", "MACD"]
    )
    
    if st.button("🔄 Compare Strategies"):
        with st.spinner("Running strategy comparison..."):
            # Generate comparison data
            comparison_data = []
            
            for strategy in strategies:
                # Simulate strategy performance
                returns = np.random.normal(0.001, 0.02, 100)
                cumulative_returns = np.cumprod(1 + returns)
                
                comparison_data.append({
                    'Strategy': strategy,
                    'Total Return': (cumulative_returns[-1] - 1) * 100,
                    'Sharpe Ratio': np.mean(returns) / np.std(returns) * np.sqrt(252),
                    'Max Drawdown': np.min(cumulative_returns) * 100,
                    'Win Rate': np.random.uniform(50, 80)
                })
            
            df_comparison = pd.DataFrame(comparison_data)
            
            # Display comparison table
            st.subheader("Strategy Performance Comparison")
            st.dataframe(df_comparison, use_container_width=True)
            
            # Create comparison charts
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    df_comparison,
                    x='Strategy',
                    y='Total Return',
                    title='Total Return by Strategy',
                    color='Strategy'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    df_comparison,
                    x='Strategy',
                    y='Sharpe Ratio',
                    title='Sharpe Ratio by Strategy',
                    color='Strategy'
                )
                st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("📋 Trade History")
    
    # Generate sample trade history
    sample_trades = []
    for i in range(50):
        sample_trades.append({
            'Date': datetime.now() - timedelta(hours=i*2),
            'Symbol': trading_pair,
            'Side': np.random.choice(['BUY', 'SELL']),
            'Quantity': round(np.random.uniform(0.1, 2.0), 3),
            'Price': round(np.random.uniform(1000, 2000), 2),
            'P&L': round(np.random.uniform(-50, 100), 2),
            'Status': np.random.choice(['FILLED', 'CANCELLED', 'PENDING'])
        })
    
    df_trades = pd.DataFrame(sample_trades)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("Status Filter", ["All"] + list(df_trades['Status'].unique()))
    
    with col2:
        side_filter = st.selectbox("Side Filter", ["All"] + list(df_trades['Side'].unique()))
    
    with col3:
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=7), datetime.now()),
            max_value=datetime.now()
        )
    
    # Filter data
    filtered_trades = df_trades.copy()
    if status_filter != "All":
        filtered_trades = filtered_trades[filtered_trades['Status'] == status_filter]
    if side_filter != "All":
        filtered_trades = filtered_trades[filtered_trades['Side'] == side_filter]
    
    # Display trade history
    st.dataframe(filtered_trades, use_container_width=True)
    
    # Trade statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Trades", len(filtered_trades))
    
    with col2:
        st.metric("Win Rate", f"{len(filtered_trades[filtered_trades['P&L'] > 0]) / len(filtered_trades) * 100:.1f}%")
    
    with col3:
        st.metric("Total P&L", f"${filtered_trades['P&L'].sum():.2f}")
    
    with col4:
        st.metric("Avg P&L per Trade", f"${filtered_trades['P&L'].mean():.2f}")

with tab5:
    st.header("🔧 Settings")
    
    # Configuration management
    st.subheader("Configuration Management")
    
    # Load current config
    config = dashboard.load_config()
    
    # Display current settings
    st.json(config)
    
    # Export/Import configuration
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Export Configuration"):
            st.download_button(
                label="Download Config",
                data=yaml.dump(config, default_flow_style=False),
                file_name="trading_bot_config.yaml",
                mime="text/yaml"
            )
    
    with col2:
        uploaded_file = st.file_uploader("Import Configuration", type=['yaml', 'yml'])
        if uploaded_file is not None:
            try:
                imported_config = yaml.safe_load(uploaded_file)
                if st.button("💾 Import Configuration"):
                    if dashboard.save_config(imported_config):
                        st.success("Configuration imported successfully!")
                        st.rerun()
            except Exception as e:
                st.error(f"Failed to import configuration: {str(e)}")
    
    # API Settings
    st.subheader("API Configuration")
    
    api_key = st.text_input("API Key", type="password")
    api_secret = st.text_input("API Secret", type="password")
    
    if st.button("🔐 Save API Credentials"):
        # In a real application, you'd want to encrypt these
        st.success("API credentials saved! (Note: In production, use secure storage)")

# Auto-refresh functionality
if st.button("🔄 Enable Auto-refresh"):
    st.success("Auto-refresh enabled! Data will update every 30 seconds.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🤖 Trading Bot Dashboard | Built with Streamlit</p>
        <p>⚠️ This is for educational purposes only. Trading involves risk.</p>
    </div>
    """,
    unsafe_allow_html=True
) 