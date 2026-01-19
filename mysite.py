import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64

# --- DATA: RAJASTHAN ODOP (From your PDF) ---
rajasthan_odop = {
    "Ajmer": "Granite and Marble Products", "Alwar": "Automobiles Parts", 
    "Jaipur": "Gems & Jewellery", "Jodhpur": "Wooden Furniture Products",
    "Udaipur": "Marble and Granite Products", "Kota": "Kota Doria"
}

# --- PDF GENERATOR FUNCTION ---
def generate_subsidy_pdf(name, district, results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Rajasthan MSME Subsidy Comparison Report", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, f"Client Name: {name}")
    pdf.ln(8)
    pdf.cell(100, 10, f"District: {district}")
    pdf.ln(15)
    
    # Table Header
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(60, 10, "Scheme Name", 1)
    pdf.cell(80, 10, "Benefit Type", 1)
    pdf.cell(50, 10, "Est. Value (INR)", 1)
    pdf.ln()
    
    # Table Rows
    pdf.set_font("Arial", size=10)
    for res in results:
        pdf.cell(60, 10, str(res['Scheme']), 1)
        pdf.cell(80, 10, str(res['Benefit']), 1)
        pdf.cell(50, 10, f"{res['Value']:,.0f}", 1)
        pdf.ln()
    
    return pdf.output(dest='S').encode('latin-1')

# --- MAIN APP ---
st.title("⚖️ Rajasthan MSME Subsidy Pro + PDF Export")

with st.sidebar:
    st.header("🔍 Eligibility Profile")
    name = st.text_input("Entrepreneur Name", "Kailash")
    state = st.selectbox("A. State", ["Rajasthan", "Other"])
    district = st.selectbox("B. District", list(rajasthan_odop.keys()))
    
    # Added Education Check for MYUVY
    edu = st.selectbox("Education Level", ["Below 10th", "10th Pass", "Graduate & Above"])
    
    # Financials
    capex = st.number_input("CAPEX", value=2000000)
    wc = st.number_input("Working Capital", value=500000)
    total_cost = capex + wc
    loan_amt = total_cost * 0.75
    age = st.number_input("Age", value=25)
    social_cat = st.selectbox("Category", ["General", "OBC", "SC", "ST"])

# --- ENGINE LOGIC ---
results = []
# MYUVY Logic (Class 10 Pass Required)
if state == "Rajasthan" and 18 <= age <= 45 and edu != "Below 10th":
    myuvy_int = min(loan_amt, 2500000) * 0.09 * 7
    results.append({"Scheme": "MYUVY", "Benefit": "9% Int. Subvention (10th Pass)", "Value": myuvy_int})

# Ambedkar Scheme
if state == "Rajasthan" and social_cat in ["SC", "ST"]:
    amb_val = min(total_cost * 0.25, 625000) + (min(loan_amt, 2500000) * 0.09 * 7)
    results.append({"Scheme": "Ambedkar Scheme", "Benefit": "25% Sub + 9% Int Save", "Value": amb_val})

# PMEGP
results.append({"Scheme": "PMEGP", "Benefit": "Margin Money Subsidy", "Value": total_cost * 0.25})

# --- DISPLAY & DOWNLOAD ---
st.subheader("🏁 Comparative Analysis")
if results:
    df = pd.DataFrame(results).sort_values(by="Value", ascending=False)
    st.table(df.style.format({"Value": "₹{:,.0f}"}))
    
    if st.button("Generate & Download PDF Report"):
        pdf_data = generate_subsidy_pdf(name, district, results)
        b64 = base64.b64encode(pdf_data).decode('latin-1')
        href = f'<a href="data:application/pdf;base64,{b64}" download="Subsidy_Report.pdf">Click here to download PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
