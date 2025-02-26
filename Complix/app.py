import streamlit as st
from groq import Groq
import pandas as pd
from datetime import datetime
import os

# Initialize Groq client with API key from secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# App Configuration
st.set_page_config(page_title="GST Simplify AI", page_icon="💼", layout="wide")

# Sidebar for navigation
st.sidebar.title("GST Simplify AI")
menu = st.sidebar.radio("Navigate", ["Home", "Tax Calculator", "Filing Assistant", "Invoice Tracker", "Reports", "Compliance", "Regulatory Updates"])

# Store invoice data in session state
if "invoices" not in st.session_state:
    st.session_state.invoices = []

# Helper function to get AI insights from Groq
def get_groq_insights(prompt):
    try:
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error fetching insights: {str(e)}"

# Home Page
if menu == "Home":
    st.title("Welcome to GST Simplify AI")
    st.write("""
    GST Simplify AI automates your GST processes by calculating taxes, assisting with filings, tracking compliance, managing invoices, generating reports, and keeping you updated on regulations. 
    Use the sidebar to explore features!
    """)

# Tax Calculator
elif menu == "Tax Calculator":
    st.title("GST Tax Calculator")
    st.write("Enter invoice details to calculate GST.")

    with st.form("tax_form"):
        amount = st.number_input("Invoice Amount (₹)", min_value=0.0, step=100.0)
        gst_rate = st.selectbox("GST Rate (%)", [5, 12, 18, 28])
        submitted = st.form_submit_button("Calculate")

        if submitted:
            gst_amount = amount * (gst_rate / 100)
            total_amount = amount + gst_amount
            st.success(f"GST Amount: ₹{gst_amount:.2f} | Total Amount: ₹{total_amount:.2f}")

            # AI Insight
            prompt = f"Provide a brief insight on how a GST rate of {gst_rate}% affects small businesses."
            insight = get_groq_insights(prompt)
            st.write("**AI Insight**: ", insight)

# Filing Assistant
elif menu == "Filing Assistant":
    st.title("GST Filing Assistant")
    st.write("Simulate GST return filing with AI suggestions.")

    return_type = st.selectbox("Return Type", ["GSTR-1", "GSTR-3B"])
    month = st.selectbox("Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
    year = st.number_input("Year", min_value=2020, max_value=2025, value=2025)

    if st.button("Generate Filing Suggestion"):
        prompt = f"Suggest steps to file {return_type} for {month} {year} ensuring compliance."
        suggestion = get_groq_insights(prompt)
        st.write("**AI Filing Suggestion**: ", suggestion)
        st.info("Note: This is a simulation. Verify with official GST guidelines.")

# Invoice Tracker
elif menu == "Invoice Tracker":
    st.title("Invoice Tracker")
    st.write("Manage your invoices here.")

    with st.form("invoice_form"):
        invoice_id = st.text_input("Invoice ID")
        amount = st.number_input("Amount (₹)", min_value=0.0)
        gst_rate = st.selectbox("GST Rate (%)", [5, 12, 18, 28])
        date = st.date_input("Date")
        submitted = st.form_submit_button("Add Invoice")

        if submitted:
            st.session_state.invoices.append({
                "Invoice ID": invoice_id,
                "Amount": amount,
                "GST Rate": gst_rate,
                "GST Amount": amount * (gst_rate / 100),
                "Total": amount * (1 + gst_rate / 100),
                "Date": date
            })
            st.success("Invoice added successfully!")

    if st.session_state.invoices:
        df = pd.DataFrame(st.session_state.invoices)
        st.dataframe(df)

# Reports
elif menu == "Reports":
    st.title("Report Generation")
    st.write("Generate and download GST reports.")

    if st.session_state.invoices:
        df = pd.DataFrame(st.session_state.invoices)
        st.dataframe(df)

        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Report as CSV",
            data=csv,
            file_name=f"GST_Report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No invoices available. Add invoices in the Invoice Tracker first.")

# Compliance Tracking
elif menu == "Compliance":
    st.title("Compliance Tracker")
    st.write("Check your GST compliance status (Simulation).")

    if st.button("Check Compliance"):
        prompt = "Provide a brief GST compliance checklist for a small business."
        checklist = get_groq_insights(prompt)
        st.write("**AI Compliance Checklist**: ", checklist)
        st.info("This is a simulated checklist. Consult a tax professional for accuracy.")

# Regulatory Updates
elif menu == "Regulatory Updates":
    st.title("GST Regulatory Updates")
    st.write("Stay updated with the latest GST regulations.")

    if st.button("Fetch Latest Updates"):
        prompt = "Provide a summary of the latest GST regulation changes in India as of February 2025."
        updates = get_groq_insights(prompt)
        st.write("**AI-Generated Updates**: ", updates)
        st.info("This is a simulation based on AI. Check official GST portals for real updates.")

# Footer
st.sidebar.write("Developed with ❤️ by Hem Bhavik | Feb 21, 2025")
