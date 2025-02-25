import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import logging

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == "quantlogix2025":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Please enter the password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Please enter the password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="QuantLogix",
    page_icon="📈",
    layout="wide"
)

if check_password():
    st.title("QuantLogix Dashboard")
    
    try:
        # Initialize Alpaca API with direct credentials
        api = tradeapi.REST(
            key_id="PKZEZB275Q07VW6SQ08M",
            secret_key="5KjODvifXKdAGOgvUGRW9AxeOXbIjnjyNlfeZVG6",
            base_url="https://paper-api.alpaca.markets"
        )
        
        # Get account information
        account = api.get_account()
        portfolio_value = float(account.portfolio_value)
        daily_change = float(account.portfolio_value) - float(account.last_equity)
        daily_change_pct = (daily_change / float(account.last_equity)) * 100 if float(account.last_equity) > 0 else 0
        
        # Get positions
        positions = api.list_positions()
        total_pl = sum(float(p.unrealized_pl) for p in positions) if positions else 0
        total_pl_pct = sum(float(p.unrealized_plpc) * 100 for p in positions) / len(positions) if positions else 0
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Portfolio Value",
                f"${portfolio_value:,.2f}",
                f"{daily_change_pct:+.2f}% today"
            )
        
        with col2:
            st.metric(
                "Daily P&L",
                f"${daily_change:,.2f}",
                f"{daily_change_pct:+.2f}%"
            )
        
        with col3:
            st.metric(
                "Total P&L",
                f"${total_pl:,.2f}",
                f"{total_pl_pct:+.2f}%"
            )
        
        with col4:
            buying_power = float(account.buying_power)
            st.metric(
                "Buying Power",
                f"${buying_power:,.2f}",
                None
            )
        
        # Create performance chart
        st.subheader("Portfolio Performance")
        
        # Time period selector
        time_period = st.selectbox(
            "Time Period",
            ["1W", "2W", "1M", "3M", "YTD", "1Y", "ALL"],
            index=2  # Default to 1M
        )
        
        # Convert time period to days
        period_days = {
            "1W": 7,
            "2W": 14,
            "1M": 30,
            "3M": 90,
            "YTD": (datetime.now() - datetime(datetime.now().year, 1, 1)).days,
            "1Y": 365,
            "ALL": 1000  # Maximum days
        }
        
        # Get historical portfolio value
        end = datetime.now()
        start = end - timedelta(days=period_days[time_period])
        
        try:
            portfolio_history = api.get_portfolio_history(
                timeframe="1D",
                start=start.strftime('%Y-%m-%d'),
                end=end.strftime('%Y-%m-%d')
            )
            
            # Create DataFrame for plotting
            df = pd.DataFrame({
                'timestamp': pd.to_datetime(portfolio_history.timestamp, unit='s'),
                'equity': portfolio_history.equity
            })
            
            fig = go.Figure()
            
            # Add portfolio value line
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['equity'],
                    mode='lines',
                    name='Portfolio Value',
                    line=dict(color='#00ff00', width=2)
                )
            )
            
            # Add area for positive returns
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['equity'],
                    fill='tonexty',
                    fillcolor='rgba(0,255,0,0.1)',
                    line=dict(width=0),
                    showlegend=False
                )
            )
            
            # Customize layout
            fig.update_layout(
                template='plotly_dark',
                xaxis_title="Date",
                yaxis_title="Portfolio Value ($)",
                height=400,
                margin=dict(l=0, r=0, t=0, b=0),
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                ),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.warning(f"Could not load portfolio history: {str(e)}")
        
        # Positions table
        st.subheader("Active Positions")
        
        if positions:
            positions_data = []
            for position in positions:
                positions_data.append({
                    'Symbol': position.symbol,
                    'Quantity': int(float(position.qty)),
                    'Entry Price': float(position.avg_entry_price),
                    'Current Price': float(position.current_price),
                    'Market Value': float(position.market_value),
                    'P&L': float(position.unrealized_pl),
                    'P&L %': float(position.unrealized_plpc) * 100
                })
            
            positions_df = pd.DataFrame(positions_data)
            
            # Format the numeric columns
            for col in ['Entry Price', 'Current Price', 'Market Value', 'P&L']:
                positions_df[col] = positions_df[col].apply(lambda x: f"${x:,.2f}")
            positions_df['P&L %'] = positions_df['P&L %'].apply(lambda x: f"{x:+.2f}%")
            
            st.dataframe(
                positions_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No active positions")
        
        # System status in sidebar
        st.sidebar.success("✅ Connected to Alpaca Paper Trading")
        
        # Add filters in sidebar
        if positions:
            st.sidebar.header("Filters")
            st.sidebar.multiselect(
                "Symbols",
                [p.symbol for p in positions],
                default=[p.symbol for p in positions]
            )
            
            market_values = [float(p.market_value) for p in positions]
            min_value = min(market_values)
            max_value = max(market_values)
            st.sidebar.slider(
                "Market Value Range",
                min_value=min_value,
                max_value=max_value,
                value=(min_value, max_value)
            )
    
    except Exception as e:
        st.error("An error occurred while running the dashboard:")
        st.code(str(e))
        logger.exception("Error in app:")
