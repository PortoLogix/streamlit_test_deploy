import streamlit as st

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
    page_icon="📈"
)

if check_password():
    st.title("Welcome to QuantLogix")
    st.write("Your trusted platform for algorithmic trading and portfolio management.")
    
    # Display key features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("📊 Real-time Portfolio Tracking")
    
    with col2:
        st.info("🤖 Automated Trading")
    
    with col3:
        st.info("📈 Market Analytics")
    
    # Add a getting started section
    st.subheader("Getting Started")
    st.write("""
    1. Connect your Alpaca trading account
    2. Set up your trading preferences
    3. Monitor your portfolio performance
    4. Start automated trading
    """)
    
    # Add a status indicator
    st.sidebar.success("✅ System Status: Operational")
