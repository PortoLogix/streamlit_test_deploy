import streamlit as st

st.set_page_config(
    page_title="QuantLogix",
    page_icon="📈",
    layout="wide"
)

st.title("QuantLogix Test")
st.write("Basic test to ensure Streamlit is working")

# Display some basic metrics
col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Sample Value",
        "$10,000",
        "+5%"
    )

with col2:
    st.metric(
        "Another Metric",
        "42",
        "-1%"
    )

# Add a simple input
symbol = st.text_input("Enter a symbol:", value="AAPL")
st.write("You entered:", symbol)

# Add a simple button
if st.button("Click me"):
    st.success("Button clicked!")
