import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(page_title="Transaction Data Quality Dashboard", layout="wide")
st.title("💡 Transaction Data Quality & Savings Explorer")

st.write(
    """
    Merchants lose money when transaction data is incomplete.
    Even **0.5% extra fees** add up fast.
    
    Explore how fixing **small missing fields** can save **real money**.
    """
)

# --------------------------------------------------
# Mock Data Generator
# --------------------------------------------------
def generate_mock_data(n=1000):
    np.random.seed(42)

    merchants = [
        "Amazon", "Walmart", "Target", "Costco", "Best Buy",
        "Apple", "Nike", "Starbucks", "Home Depot", "Uber"
    ]

    data = {
        "Transaction ID": [f"TXN-{100000+i}" for i in range(n)],
        "Merchant": np.random.choice(merchants, n),
        "Amount": np.round(np.random.uniform(5, 500, n), 2),
        "Zip Code": np.random.choice(
            ["10001", "30301", "60601", "94105", "75201", None],
            n,
            p=[0.18, 0.18, 0.18, 0.18, 0.18, 0.10]
        ),
        "Tax ID": np.random.choice(
            ["TX123", "TX456", "TX789", None],
            n,
            p=[0.3, 0.3, 0.3, 0.1]
        ),
        "Date": [
            datetime.today() - timedelta(days=int(x))
            for x in np.random.uniform(0, 365, n)
        ],
    }

    df = pd.DataFrame(data)
    return df

# --------------------------------------------------
# Data Source
# --------------------------------------------------
st.subheader("📂 Data Source")

option = st.radio(
    "Choose data source:",
    ["Use mock dataset (~1,000 rows)", "Upload my own CSV"]
)

if option == "Upload my own CSV":
    uploaded = st.file_uploader("Upload CSV", type="csv")

    if uploaded is None:
        st.info("Please upload a CSV file.")
        st.stop()

    df = pd.read_csv(uploaded)
else:
    df = generate_mock_data()
    st.success("Using generated mock dataset")

# --------------------------------------------------
# Identify Missing Data
# --------------------------------------------------
df["Missing Zip"] = df["Zip Code"].isna()
df["Missing Tax ID"] = df["Tax ID"].isna()

df["Has Missing Info"] = df["Missing Zip"] | df["Missing Tax ID"]

# Savings logic (simple + illustrative)
FEE_RATE = 0.005
df["Potential Savings ($)"] = np.where(
    df["Has Missing Info"],
    df["Amount"] * FEE_RATE,
    0.0
)

# --------------------------------------------------
# Interactive Table
# --------------------------------------------------
st.subheader("🔍 Transactions with Missing Information")

display_df = df.copy()
display_df["Fix"] = False

edited_df = st.data_editor(
    display_df[
        [
            "Transaction ID",
            "Merchant",
            "Amount",
            "Zip Code",
            "Tax ID",
            "Potential Savings ($)",
            "Fix",
        ]
    ],
    use_container_width=True,
    disabled=[
        "Transaction ID",
        "Merchant",
        "Amount",
        "Zip Code",
        "Tax ID",
        "Potential Savings ($)",
    ],
)

# --------------------------------------------------
# Savings Calculation
# --------------------------------------------------
fixed_rows = edited_df[edited_df["Fix"] == True]

total_savings = fixed_rows["Potential Savings ($)"].sum()

st.metric(
    label="💰 Total Potential Savings Unlocked",
    value=f"${total_savings:,.2f}"
)

# --------------------------------------------------
# Clickable Row Details
# --------------------------------------------------
if not fixed_rows.empty:
    st.subheader("📌 Selected Transaction Details")

    row = fixed_rows.iloc[-1]

    st.success(
        f"""
        **Transaction ID:** {row['Transaction ID']}  
        **Merchant:** {row['Merchant']}  
        **Amount:** ${row['Amount']:.2f}  
        **Savings if Fixed:** ${row['Potential Savings ($)']:.2f}
        """
    )

# --------------------------------------------------
# Top Merchants Chart
# --------------------------------------------------
st.subheader("📊 Top 5 Merchants by Savings Potential")

merchant_savings = (
    df.groupby("Merchant")["Potential Savings ($)"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)

st.bar_chart(merchant_savings)

# --------------------------------------------------