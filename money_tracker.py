import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- 1. CONFIGURATION & STYLES ---
st.set_page_config(page_title="MoneyTracker", page_icon="💸", layout="wide")

def load_data():
    if os.path.exists('finances.json'):
        try:
            with open('finances.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(data):
    with open('finances.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def amount_color(value):
    if isinstance(value, (int, float)):
        if value < 0: return 'color: #ff4b4b;' # Streamlit Red
        if value > 0: return 'color: #29b09d;' # Streamlit Green
    return ''

# Initialization
if 'transactions' not in st.session_state:
    st.session_state.transactions = load_data()

# --- 2. USER INTERFACE (Header & Sidebar) ---
st.title("💸 MoneyTracker: Your Financial Management")

with st.expander("➕ Register New Transaction", expanded=False):
    with st.form("registration_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            concept = st.text_input("Concept", placeholder="e.g., Grocery Shopping")
            amount = st.number_input("Amount (€)", min_value=0.01, step=0.01)
        with col2:
            trans_type = st.selectbox("Type", ["Expense", "Income"])
            cat_options = ["Food", "Housing", "Transport", "Leisure", "Salary", "Others"]
            category = st.selectbox("Category", cat_options)
        
        date = st.date_input("Date", datetime.now(), format="DD/MM/YYYY")
        
        if st.form_submit_button("Add Transaction"):
            final_value = amount if trans_type == "Income" else -amount
            new_entry = {
                "Date": date.strftime("%d/%m/%Y"),
                "Concept": concept,
                "Type": trans_type,
                "Amount": final_value,
                "Category": category
            }
            st.session_state.transactions.append(new_entry)
            save_data(st.session_state.transactions)
            st.success("✅ Record saved")
            st.rerun()

# --- 3. BUSINESS LOGIC & DASHBOARD ---
if st.session_state.transactions:
    df = pd.DataFrame(st.session_state.transactions)
    
    # Main Metrics
    total_income = df[df["Amount"] > 0]["Amount"].sum()
    total_expenses = df[df["Amount"] < 0]["Amount"].sum()
    net_balance = total_income + total_expenses

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Income", f"{total_income:.2f} €")
    c2.metric("Total Expenses", f"{abs(total_expenses):.2f} €", delta_color="inverse")
    c3.metric("Net Balance", f"{net_balance:.2f} €")

    st.divider()

    # --- 4. VISUALIZATION ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📋 History")
        st.dataframe(
            df.style.map(amount_color, subset=["Amount"])
                    .format({"Amount": "{:.2f} €"}),
            use_container_width=True,
            hide_index=True
        )
        
        # Deletion section
        with st.popover("🗑️ Delete Records"):
            options = [f"{i}: {m['Concept']} ({m['Date']})" for i, m in enumerate(st.session_state.transactions)]
            selection = st.selectbox("Select to delete:", options)
            if st.button("Confirm Delete", type="primary"):
                idx = int(selection.split(":")[0])
                st.session_state.transactions.pop(idx)
                save_data(st.session_state.transactions)
                st.rerun()

    with col_right:
        st.subheader("📊 Expenses by Category")
        df_expenses = df[df["Amount"] < 0]
        if not df_expenses.empty:
            summary = df_expenses.groupby("Category")["Amount"].sum().abs()
            st.bar_chart(summary)
        else:
            st.info("No expenses recorded yet.")
else:
    st.info("👋 Welcome! Register your first transaction to get started.")
