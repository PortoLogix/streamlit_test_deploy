import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            base_url="https://paper-api.alpaca.markets",
            api_version='v2'  # Explicitly set API version
        )
        
        # Test API connection
        try:
            account = api.get_account()
            st.sidebar.success("✅ Connected to Alpaca Paper Trading")
        except Exception as e:
            st.error(f"Failed to connect to Alpaca API: {str(e)}")
            st.error("Python version: " + sys.version)
            st.error("Alpaca API version: " + tradeapi.__version__)
            st.stop()
        
        # Basic account info
        st.write("Account Status:", account.status)
        st.write("Account Currency:", account.currency)
        
        # Display metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Portfolio Value",
                f"${float(account.portfolio_value):,.2f}",
                None
            )
        
        with col2:
            st.metric(
                "Buying Power",
                f"${float(account.buying_power):,.2f}",
                None
            )
        
        # Display positions if any
        st.subheader("Active Positions")
        try:
            positions = api.list_positions()
            if positions:
                positions_data = []
                for position in positions:
                    positions_data.append({
                        'Symbol': position.symbol,
                        'Quantity': int(float(position.qty)),
                        'Current Price': f"${float(position.current_price):,.2f}",
                        'Market Value': f"${float(position.market_value):,.2f}"
                    })
                
                st.dataframe(
                    pd.DataFrame(positions_data),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No active positions")
        except Exception as e:
            st.warning(f"Could not load positions: {str(e)}")
    
    except Exception as e:
        st.error("An error occurred while running the dashboard:")
        st.error(str(e))
        st.error("Python version: " + sys.version)
        st.error("Alpaca API version: " + tradeapi.__version__)
        logger.exception("Error in app:")
