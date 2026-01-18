import streamlit as st
import pandas as pd
import io
from fpdf import FPDF
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="CMA & DPR Generator", layout="wide")

# --- 1. DATA CALCULATIONS (7-YEARS) ---
st.title("📊 DPR & CMA Data Generator")
total_investment = st.sidebar.number_input("Total Project Cost", value=5000000)
term_loan = st.sidebar.number_input("Term Loan", value=3500000)

# Generating 7-Year Projection Data
years = [f"FY {2025+i}-{str(2026+i)[2:]}" for i in range(7)]
revenue = [total_investment * 1.5 * (1.10**i) for i in range(7)]
net_profit = [r * 0.15 for r in revenue]
depreciation = [total_investment * 0.15 * (0.85**i) for i in range(7)]

df_cma = pd.DataFrame({
    "Financial Year": years,
    "Net Sales": revenue,
    "Depreciation": depreciation,
    "Net Profit (PAT)": net_profit
})

st.subheader("7-Year Projection Summary")
st.dataframe(df_cma.style.format("₹{:,.0f}"), use_container_width=True)

# --- 2. EXCEL DOWNLOAD LOGIC ---
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Sheet 1: CMA Data
        df.to_sheet(writer, index=False, sheet_name='CMA_Projections')
        
        # Formatting the Excel
        workbook = writer.book
        worksheet = writer.sheets['CMA_Projections']
        format_currency = workbook.add_format({'num_format': '₹#,##0'})
        worksheet.set_column('B:D', 18, format_currency)
        
    return output.getvalue()

# --- 3. PDF DOWNLOAD LOGIC ---
def create_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "DETAILED PROJECT REPORT (CMA)", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.ln(10)
    for i, row in df.iterrows():
        pdf.cell(0, 10, f"{row['Financial Year']}: Sales ₹{row['Net Sales']:,.0f} | Profit ₹{row['Net Profit (PAT)']:,.0f}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 4. DOWNLOAD BUTTONS ---
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.download_button(
        label="📥 Download Project Report (PDF)",
        data=create_pdf(df_cma),
        file_name="MSME_Project_Report.pdf",
        mime="application/pdf"
    )

with col2:
    st.download_button(
        label="Excel File 📗 Download CMA Data (Excel)",
        data=to_excel(df_cma),
        file_name="CMA_Data_Sheet.xlsx",
        mime="application/vnd.ms-excel"
    )
