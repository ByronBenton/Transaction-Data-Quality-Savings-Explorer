# 💡 Transaction Data Quality & Savings Explorer

A Streamlit dashboard that demonstrates how **missing transaction data**
(e.g. Zip Code or Tax ID) can lead to **avoidable processing fees** —
and how fixing small data gaps can unlock **real cost savings**.

---

## 🚀 Features

- 📂 Use a generated mock dataset (~1,000 transactions) or upload your own CSV
- 🔍 Automatically detects missing Zip Codes and Tax IDs
- 💰 Estimates potential savings from fixing incomplete transactions
- ✅ Interactive table to mark transactions as “fixed”
- 📊 Visualizes top merchants by savings potential

---

## 🧮 Savings Logic (Illustrative)

- Transactions with missing Zip Code or Tax ID incur an assumed **0.5% extra fee**
- Fixing those fields removes the fee
- Savings are calculated as:

