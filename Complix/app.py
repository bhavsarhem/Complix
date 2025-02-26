import streamlit as st
import pandas as pd
from datetime import datetime
import json
from groq import Groq
import re

# Initialize Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Configure Streamlit page
st.set_page_config(
    page_title="GST Simplify AI",
    page_icon="logo.jpg",
    layout="wide"
)

# CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .upload-box {
        border: 2px dashed #4CAF50;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

class GSTCalculator:
    def __init__(self):
        self.gst_rates = {
            "0%": 0.00,
            "5%": 0.05,
            "12%": 0.12,
            "18%": 0.18,
            "28%": 0.28
        }

    def calculate_gst(self, base_amount, rate):
        gst_amount = base_amount * self.gst_rates[rate]
        total_amount = base_amount + gst_amount
        return {
            "base_amount": base_amount,
            "gst_amount": gst_amount,
            "total_amount": total_amount
        }

class InvoiceManager:
    def __init__(self):
        self.invoices = []

    def add_invoice(self, invoice_data):
        invoice_data['invoice_id'] = f"INV-{len(self.invoices) + 1}"
        invoice_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.invoices.append(invoice_data)

    def get_all_invoices(self):
        return self.invoices

def get_ai_insights(invoice_data):
    prompt = f"""
    Analyze the following GST invoice data and provide insights:
    {json.dumps(invoice_data, indent=2)}
    
    Please provide:
    1. Tax compliance recommendations
    2. Potential tax saving opportunities
    3. Risk analysis
    4. Best practices for future transactions
    """
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mixtral-8x7b-32768",
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting AI insights: {str(e)}"

def main():
    st.sidebar.image("sidebarlogo.jpg", use_container_width=True)
    st.title("GST Simplify AI")
    
    # Initialize session state
    if 'calculator' not in st.session_state:
        st.session_state.calculator = GSTCalculator()
    if 'invoice_manager' not in st.session_state:
        st.session_state.invoice_manager = InvoiceManager()

    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Select Function",
        ["GST Calculator", "Invoice Management", "Reports & Analytics", "AI Insights"]
    )

    if page == "GST Calculator":
        st.header("GST Calculator")
        col1, col2 = st.columns(2)
        
        with col1:
            base_amount = st.number_input("Enter Base Amount (₹)", min_value=0.0, value=1000.0)
            gst_rate = st.selectbox("Select GST Rate", list(st.session_state.calculator.gst_rates.keys()))
            
            if st.button("Calculate GST"):
                result = st.session_state.calculator.calculate_gst(base_amount, gst_rate)
                
                st.success("GST Calculation Results")
                st.write(f"Base Amount: ₹{result['base_amount']:,.2f}")
                st.write(f"GST Amount: ₹{result['gst_amount']:,.2f}")
                st.write(f"Total Amount: ₹{result['total_amount']:,.2f}")

    elif page == "Invoice Management":
        st.header("Invoice Management")
        
        with st.expander("Add New Invoice"):
            col1, col2 = st.columns(2)
            
            with col1:
                invoice_number = st.text_input("Invoice Number")
                customer_name = st.text_input("Customer Name")
                invoice_date = st.date_input("Invoice Date")
                
            with col2:
                base_amount = st.number_input("Base Amount (₹)", min_value=0.0)
                gst_rate = st.selectbox("GST Rate", list(st.session_state.calculator.gst_rates.keys()))
                
            if st.button("Add Invoice"):
                invoice_data = {
                    "invoice_number": invoice_number,
                    "customer_name": customer_name,
                    "invoice_date": invoice_date.strftime("%Y-%m-%d"),
                    "base_amount": base_amount,
                    "gst_rate": gst_rate
                }
                
                st.session_state.invoice_manager.add_invoice(invoice_data)
                st.success("Invoice added successfully!")
        
        # Display invoices
        st.subheader("Recent Invoices")
        invoices_df = pd.DataFrame(st.session_state.invoice_manager.get_all_invoices())
        if not invoices_df.empty:
            st.dataframe(invoices_df)
        else:
            st.info("No invoices added yet.")

    elif page == "Reports & Analytics":
        st.header("Reports & Analytics")
        
        invoices = st.session_state.invoice_manager.get_all_invoices()
        if invoices:
            df = pd.DataFrame(invoices)
            
            # Summary statistics
            st.subheader("Summary Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Invoices", len(df))
            with col2:
                total_amount = df['base_amount'].sum()
                st.metric("Total Amount (₹)", f"{total_amount:,.2f}")
            with col3:
                avg_amount = df['base_amount'].mean()
                st.metric("Average Amount (₹)", f"{avg_amount:,.2f}")
            
            # GST Rate Distribution
            st.subheader("GST Rate Distribution")
            gst_dist = df['gst_rate'].value_counts()
            st.bar_chart(gst_dist)
            
        else:
            st.info("No data available for analysis. Please add some invoices first.")

    elif page == "AI Insights":
        st.header("AI Insights")
        
        invoices = st.session_state.invoice_manager.get_all_invoices()
        if invoices:
            if st.button("Generate AI Insights"):
                with st.spinner("Generating insights..."):
                    insights = get_ai_insights(invoices)
                    st.markdown(insights)
        else:
            st.info("Please add some invoices to get AI insights.")

if __name__ == "__main__":
    main()
