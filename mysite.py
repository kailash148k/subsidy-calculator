import streamlit as st
from fpdf import FPDF
import pandas as pd

# Page setup
st.set_page_config(page_title="SubsidyClaim.com", page_icon="📈")

st.title("🏦 MSME Subsidy & Project Report Generator")
st.write("Official Tool for subsidyclaim.com")
st.markdown("---")

# 1. USER INPUTS
with st.sidebar:
    st.header("Project Details")
    name = st.text_input("Entrepreneur/Company Name", "Your Name")
    biz_name = st.text_input("Business Name", "New Enterprise")
    cost = st.number_input("Total Project Cost (INR)", min_value=100000, value=1000000)
    loc = st.selectbox("Location", ["Rural", "Urban"])
    cat = st.selectbox("Category", ["General", "Special (Women/SC/ST/OBC)"])

# 2. SUBSIDY LOGIC
if loc == "Rural" or cat != "General":
    rate = 0.35
    scheme_type = "Special Category"
else:
    rate = 0.25
    scheme_type = "General Category"

subsidy_amount = cost * rate

# 3. DISPLAY RESULTS ON WEBSITE
st.subheader("📊 Subsidy Calculation Results")
col1, col2 = st.columns(2)
col1.metric("Eligible Subsidy", f"₹{subsidy_amount:,.0f}")
col2.metric("Subsidy Rate", f"{rate*100}%")

st.info(f"Based on your inputs, you qualify for the **{scheme_type}** under PMEGP guidelines.")

# 4. PROJECT REPORT GENERATOR (PDF)
def generate_pdf(name, biz, cost, subsidy):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(200, 20, txt="DETAILED PROJECT REPORT", ln=True, align='C')
    pdf.ln(10)
    
    # Details Table
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, txt=f"Entrepreneur: {name}", ln=True)
    pdf.cell(100, 10, txt=f"Business Name: {biz}", ln=True)
    pdf.cell(100, 10, txt=f"Total Investment: INR {cost:,.2f}", ln=True)
    pdf.cell(100, 10, txt=f"Govt. Subsidy: INR {subsidy:,.2f}", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Financial Summary (Projected Year 1)", ln=True)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, txt=f"Promoter Contribution (10%): INR {cost*0.1:,.2f}", ln=True)
    pdf.cell(100, 10, txt=f"Bank Loan Amount: INR {cost*0.9:,.2f}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# Download Button
pdf_bytes = generate_pdf(name, biz_name, cost, subsidy_amount)
st.download_button(
    label="📩 Download Official Project Report (PDF)",
    data=pdf_bytes,
    file_name=f"Report_{biz_name}.pdf",
    mime="application/pdf"
)