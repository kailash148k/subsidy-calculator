import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="PMEGP Excel DPR Engine", layout="wide")
st.title("📂 Official PMEGP Excel Report Generator")

# --- 1. DATA INPUTS (Matching smita.xls DataSheet) ---
with st.sidebar:
    st.header("📋 Applicant Profile")
    beneficiary_name = st.text_input("Name of Beneficiary", "SMITA SINGH")
    father_husband = st.text_input("Father's/Spouse's Name", "SOURAV SINGH")
    unit_address = st.text_area("Unit Address", "F-1 GOKUL BILISS BHUWANA, UDAIPUR 313001")
    district = st.text_input("District", "UDAIPUR")
    pin = st.text_input("Pin Code", "313001")
    mobile = st.text_input("Mobile Number", "9982668727")
    
    st.markdown("---")
    agency = st.selectbox("Sponsoring Agency", ["DIC", "KVIC", "KVIB"])
    location = st.radio("Unit Location", ["Rural", "Urban"])
    social_cat = st.selectbox("Social Category", ["General", "OBC", "SC", "ST", "Minority"])
    gender = st.selectbox("Gender", ["Male", "Female"])
    
    st.markdown("---")
    activity = st.text_input("Proposed Activity", "ORTHODONTIC AND IMPLANT CENTRE")
    sector = st.radio("Sector", ["Manufacturing", "Service"])

# --- 2. FINANCIAL CALCULATIONS (Matching official PMEGP norms) ---
st.subheader("🏗️ Financial Inputs")
col1, col2 = st.columns(2)

with col1:
    pm_cost = st.number_input("Plant & Machinery", value=3200000)
    furn_cost = st.number_input("Furniture & Fixtures", value=200000)
    lb_cost = st.number_input("Workshed / Building", value=0)
    wc_margin = st.number_input("Working Capital Margin", value=190000)
    total_cost = pm_cost + furn_cost + lb_cost + wc_margin

with col2:
    # Official Contribution %
    is_special = (gender == "Female" or social_cat != "General" or location == "Rural")
    own_cont_pct = 0.05 if is_special else 0.10
    own_cont_amt = total_cost * own_cont_pct
    
    # Official Subsidy %
    if location == "Rural":
        sub_rate = 35 if is_special else 25
    else:
        sub_rate = 25 if is_special else 15
    
    term_loan = pm_cost + furn_cost + lb_cost - own_cont_amt
    subsidy_amt = (total_cost - lb_cost) * (sub_rate / 100)
    
    st.metric("Total Project Cost", f"₹{total_cost:,.0f}")
    st.metric(f"Own Contribution ({int(own_cont_pct*100)}%)", f"₹{own_cont_amt:,.0f}")
    st.success(f"Expected Subsidy: ₹{subsidy_amt:,.0f}")

# --- 3. EXCEL GENERATION ENGINE ---
def generate_pmegp_excel():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # --- Sheet: DPR_print (Top Sheet) ---
        worksheet = workbook.add_worksheet('DPR_print')
        bold = workbook.add_format({'bold': True, 'border': 1})
        center_bold = workbook.add_format({'bold': True, 'align': 'center', 'border': 1})
        normal = workbook.add_format({'border': 1})
        
        # Formatting Top Sheet
        worksheet.merge_range('A1:F1', 'PROJECT AT A GLANCE - TOP SHEET', center_bold)
        worksheet.write('A3', '1.0 Name of Beneficiary', bold)
        worksheet.write('D3', beneficiary_name, normal)
        worksheet.write('A5', '2.0 Constitution', bold)
        worksheet.write('D5', 'Individual', normal)
        worksheet.write('A7', '3.0 Father/Spouse Name', bold)
        worksheet.write('D7', father_husband, normal)
        worksheet.write('A9', '4.0 Unit Address', bold)
        worksheet.write('D9', unit_address, normal)
        
        worksheet.write('A11', 'COST OF PROJECT', bold)
        worksheet.write('D11', '(Amount in Rs.)', bold)
        worksheet.write('A12', 'Fixed Capital', normal)
        worksheet.write('D12', pm_cost + furn_cost + lb_cost, normal)
        worksheet.write('A13', 'Working Capital', normal)
        worksheet.write('D13', wc_margin, normal)
        worksheet.write('A14', 'Total Project Cost', bold)
        worksheet.write('D14', total_cost, bold)
        
        worksheet.write('A16', 'MEANS OF FINANCE', bold)
        worksheet.write('A17', 'Own Contribution', normal)
        worksheet.write('D17', own_cont_amt, normal)
        worksheet.write('A18', 'Bank Loan', normal)
        worksheet.write('D18', term_loan + wc_margin, normal)
        worksheet.write('A19', 'KVIC Margin Money (Subsidy)', bold)
        worksheet.write('D19', subsidy_amt, bold)

        # --- Sheet: DataSheet (Input overview) ---
        # [Similar formatting for other sheets as per smita.xls]
        
    return output.getvalue()

# --- 4. DOWNLOAD ACTION ---
st.markdown("---")
if st.button("🚀 Finalize and Create Excel Report"):
    excel_data = generate_pmegp_excel()
    st.download_button(
        label="📥 Download Official PMEGP Excel (.xlsx)",
        data=excel_data,
        file_name=f"PMEGP_DPR_{beneficiary_name.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.success("Excel report generated successfully. You can now upload this to the government portal.")
