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
    required_cols = ["Transaction ID", "Merchant", "Amount", "Zip Code", "Tax ID"]
    if not all(col in df.columns for col in required_cols):
        st.error(f"CSV must contain columns: {required_cols}")
        st.stop()
else:
    df = generate_mock_data()
    st.success("Using generated mock dataset")

# --------------------------------------------------
# Identify Missing Data
# --------------------------------------------------
df["Missing Zip"] = df["Zip Code"].isna()
df["Missing Tax ID"] = df["Tax ID"].isna()
df["Has Missing Info"] = df["Missing Zip"] | df["Missing Tax ID"]

# Savings logic
FEE_RATE = 0.005
df["Potential Savings ($)"] = np.where(
    df["Has Missing Info"],
    df["Amount"] * FEE_RATE,
    0.0
)

# --------------------------------------------------
# Progress Bar for Data Completion
# --------------------------------------------------
st.subheader("📈 Data Completion Progress")
total_txn = len(df)
completed_txn = len(df[~df["Has Missing Info"]])
completion_pct = completed_txn / total_txn
st.progress(completion_pct)
st.caption(f"{completion_pct*100:.0f}% of transaction data optimized – Unlock {100 - completion_pct*100:.0f}% more savings!")

# --------------------------------------------------
# Filters
# --------------------------------------------------
st.subheader("🔎 Filters")
missing_filter = st.multiselect(
    "Show transactions with:",
    ["Missing Zip", "Missing Tax ID", "Complete"],
    default=["Missing Zip", "Missing Tax ID"]
)

filter_mask = pd.Series(False, index=df.index)
if "Missing Zip" in missing_filter:
    filter_mask |= df["Missing Zip"]
if "Missing Tax ID" in missing_filter:
    filter_mask |= df["Missing Tax ID"]
if "Complete" in missing_filter:
    filter_mask |= ~df["Has Missing Info"]

filtered_df = df[filter_mask]

# --------------------------------------------------
# Interactive Table
# --------------------------------------------------
st.subheader("🔍 Transactions with Missing Information")

display_df = filtered_df.copy()

# ✅ All rows unchecked by default
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
# Real-Time Savings Calculation
# --------------------------------------------------
fixed_rows = edited_df[edited_df["Fix"] == True]
total_savings = fixed_rows["Potential Savings ($)"].sum()
st.metric(
    label="💰 Total Potential Savings Unlocked",
    value=f"${total_savings:,.2f}"
)

# Display details of all fixed rows
if not fixed_rows.empty:
    st.subheader("📌 Selected Transaction Details")
    for _, row in fixed_rows.iterrows():
        st.success(
            f"""
            **Transaction ID:** {row['Transaction ID']}  
            **Merchant:** {row['Merchant']}  
            **Amount:** ${row['Amount']:.2f}  
            **Savings if Fixed:** ${row['Potential Savings ($)']:.2f}
            """
        )

# --------------------------------------------------
# Collapsible Merchant List
# --------------------------------------------------
st.subheader("📊 Merchant Savings Overview")

merchant_savings = (
    df.groupby("Merchant")["Potential Savings ($)"]
    .sum()
    .sort_values(ascending=False)
)

# Top 5 by default
st.bar_chart(merchant_savings.head(5))

# Expandable full list
with st.expander("Show all merchants"):
    st.bar_chart(merchant_savings)

# --------------------------------------------------
# Tooltips for Key Terms
# --------------------------------------------------
st.markdown(
    """
    **Tooltips:**  
    - **Potential Savings ($)** 💰 <span title="Estimated savings if missing data is fixed, assuming 0.5% extra fees">ℹ️</span>  
    - **Missing Zip** <span title="Indicates if the Zip Code for the transaction is missing">ℹ️</span>  
    - **Missing Tax ID** <span title="Indicates if the Tax ID for the transaction is missing">ℹ️</span>  
    - **Fix** <span title="Check this box if you have corrected the missing information for this transaction">ℹ️</span>
    """,
    unsafe_allow_html=True
)
