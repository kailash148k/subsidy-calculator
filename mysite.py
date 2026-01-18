import streamlit as st
import pandas as pd
from fpdf import FPDF

# ... [Keep your previous logic for PMEGP, PMFME, and RIPS] ...

# --- ADVANCED FINANCIAL PROJECTION LOGIC ---
st.subheader("📈 5-Year Financial Projection")
annual_growth = 0.10 # Assuming 10% growth per year

# Generate 5-Year P&L Table
years = ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
revenue = [cost * 1.2] # Initial revenue estimate
for i in range(1, 5):
    revenue.append(revenue[-1] * (1 + annual_growth))

expenses = [r * 0.75 for r in revenue] # Assuming 75% expense ratio
profits = [r - e for r, e in zip(revenue, expenses)]

financial_df = pd.DataFrame({
    "Year": years,
    "Projected Revenue": revenue,
    "Projected Expenses": expenses,
    "Net Profit": profits
})

st.table(financial_df.style.format("₹{:,.0f}"))

# --- UPDATE PDF GENERATOR TO INCLUDE P&L ---
def create_full_dpr(name, cost, scheme_name, value, fin_df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "DETAILED PROJECT REPORT (DPR)", ln=True, align='C')
    pdf.ln(10)
    
    # Financial Projections Table in PDF
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, "Year", border=1)
    pdf.cell(70, 10, "Revenue", border=1)
    pdf.cell(70, 10, "Net Profit", border=1, ln=True)
    
    pdf.set_font("Arial", size=10)
    for index, row in fin_df.iterrows():
        pdf.cell(50, 10, str(row['Year']), border=1)
        pdf.cell(70, 10, f"INR {row['Projected Revenue']:,.0f}", border=1)
        pdf.cell(70, 10, f"INR {row['Net Profit']:,.0f}", border=1, ln=True)
        
    return pdf.output(dest='S').encode('latin-1')

# ... [Keep your download button logic] ...
