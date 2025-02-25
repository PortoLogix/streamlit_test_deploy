import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go

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
    
    # Generate sample data
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    np.random.seed(42)  # For reproducible results
    
    # Generate realistic looking portfolio values
    initial_value = 100000
    daily_returns = np.random.normal(loc=0.0001, scale=0.02, size=len(dates))
    portfolio_values = initial_value * (1 + daily_returns).cumprod()
    
    # Calculate P&L metrics
    current_value = portfolio_values[-1]
    daily_change = portfolio_values[-1] - portfolio_values[-2]
    daily_change_pct = (daily_change / portfolio_values[-2]) * 100
    total_change = portfolio_values[-1] - initial_value
    total_change_pct = (total_change / initial_value) * 100
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Portfolio Value",
            f"${current_value:,.2f}",
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
            f"${total_change:,.2f}",
            f"{total_change_pct:+.2f}%"
        )
    
    with col4:
        # Calculate 30-day volatility
        returns = np.diff(portfolio_values) / portfolio_values[:-1]
        volatility = np.std(returns) * np.sqrt(252) * 100  # Annualized
        st.metric(
            "Volatility (Ann.)",
            f"{volatility:.2f}%",
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
    
    fig = go.Figure()
    
    # Add portfolio value line
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=portfolio_values,
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#00ff00', width=2)
        )
    )
    
    # Add area for positive returns
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=portfolio_values,
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
    
    # Add range selector
    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Sample positions table
    st.subheader("Active Positions")
    
    # Generate sample positions data
    positions_data = {
        'Symbol': ['AAPL', 'GOOGL', 'TSLA', 'MSFT', 'AMZN'],
        'Quantity': [100, 50, 200, 150, 75],
        'Entry Price': [150.25, 2800.50, 750.75, 300.50, 3500.25],
        'Current Price': [155.50, 2850.25, 760.00, 310.75, 3550.50],
        'Market Value': [15550.00, 142512.50, 152000.00, 46612.50, 266287.50],
        'P&L': [525.00, 2487.50, 1850.00, 1537.50, 3768.75],
        'P&L %': [3.49, 1.78, 1.23, 3.41, 1.44]
    }
    
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
    
    # System status in sidebar
    st.sidebar.success("✅ System Status: Operational")
    
    # Add filters in sidebar
    st.sidebar.header("Filters")
    st.sidebar.multiselect(
        "Symbols",
        positions_df['Symbol'].tolist(),
        default=positions_df['Symbol'].tolist()
    )
    
    min_value = 0
    max_value = 500000
    st.sidebar.slider(
        "Market Value Range",
        min_value=min_value,
        max_value=max_value,
        value=(min_value, max_value)
    )
