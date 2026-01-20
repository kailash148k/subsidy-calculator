import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Government-Ready PMEGP Excel Generator", layout="wide")
st.title("🏛️ Official PMEGP Excel Project Report Engine")

# --- 1. SIDEBAR: APPLICANT PROFILE (Matches row-wise DataSheet) ---
with st.sidebar:
    st.header("📋 Applicant Profile")
    beneficiary_name = st.text_input("Name of Beneficiary", "SMITA SINGH")
    father_husband = st.text_input("Father's/Spouse's Name", "SOURAV SINGH")
    unit_address = st.text_area("Unit Address", "F-1 GOKUL BILISS BHUWANA, UDAIPUR 313001")
    mobile = st.text_input("Mobile", "9982668727")
    activity = st.text_input("Proposed Activity", "ORTHODONTIC AND IMPLANT CENTRE")
    social_cat = st.selectbox("Social Category", ["General", "OBC", "SC", "ST", "Minority"])
    gender = st.selectbox("Gender", ["Male", "Female"])
    location = st.radio("Unit Location", ["Rural", "Urban"])

# --- 2. MAIN INPUTS: PROJECT COST (Matching row 1-423 Financials) ---
st.subheader("🏗️ Financial Inputs (Assets vs Funding)")
col1, col2 = st.columns(2)

with col1:
    pm_cost = st.number_input("Plant & Machinery", value=3200000)
    furn_cost = st.number_input("Furniture & Fixtures", value=200000)
    lb_cost = st.number_input("Workshed / Building", value=0)
    wc_loan = st.number_input("Working Capital Loan", value=190000)
    total_cost = pm_cost + furn_cost + lb_cost + wc_loan

with col2:
    is_special = (gender == "Female" or social_cat != "General" or location == "Rural")
    own_cont_pct = 0.05 if is_special else 0.10
    own_cont_amt = total_cost * own_cont_pct
    
    # Official KVIC Margin Money (Subsidy) Logic 
    sub_rate = 0.35 if (location == "Rural" and is_special) else (0.25 if location == "Rural" else 0.15)
    subsidy_amt = (total_cost - lb_cost) * sub_rate
    term_loan = total_cost - own_cont_amt - wc_loan
    
    st.metric("Total Project Cost", f"₹{total_cost:,.0f}")
    st.metric(f"Own Contribution ({int(own_cont_pct*100)}%)", f"₹{own_cont_amt:,.0f}")
    st.success(f"Expected Subsidy: ₹{subsidy_amt:,.0f}")

# --- 3. EXCEL GENERATION ENGINE ---
def generate_official_excel():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Styles 
        header_fmt = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D7E4BC', 'border': 1})
        bold_fmt = workbook.add_format({'bold': True, 'border': 1})
        normal_fmt = workbook.add_format({'border': 1})
        currency_fmt = workbook.add_format({'num_format': '₹#,##0', 'border': 1})

        # Sheet 1: DPR_print (The Top Sheet) 
        ws_print = workbook.add_worksheet('DPR_print')
        ws_print.merge_range('A1:G1', 'PROJECT AT A GLANCE - TOP SHEET', header_fmt)
        
        # Row-wise data mapping (Matches row 1-423 sequence)
        ws_print.write('A3', '1.0 Name of Beneficiary', bold_fmt)
        ws_print.write('D3', beneficiary_name, normal_fmt)
        ws_print.write('A5', '2.0 Constitution', bold_fmt)
        ws_print.write('D5', 'Individual', normal_fmt)
        ws_print.write('A7', '3.0 Father/Spouse Name', bold_fmt)
        ws_print.write('D7', father_husband, normal_fmt)
        ws_print.write('A9', '4.0 Unit Address', bold_fmt)
        ws_print.write('D9', unit_address, normal_fmt)
        
        ws_print.write('A11', 'COST OF PROJECT', header_fmt)
        ws_print.write('D11', '(Amount in Rs.)', header_fmt)
        ws_print.write('A12', 'Fixed Capital', normal_fmt)
        ws_print.write('D12', pm_cost + furn_cost + lb_cost, currency_fmt)
        ws_print.write('A13', 'Working Capital', normal_fmt)
        ws_print.write('D13', wc_loan, currency_fmt)
        ws_print.write('A14', 'Total Project Cost', bold_fmt)
        ws_print.write('D14', total_cost, currency_fmt)
        
        ws_print.write('A16', 'MEANS OF FINANCE', header_fmt)
        ws_print.write('A17', 'Own Contribution', normal_fmt)
        ws_print.write('D17', own_cont_amt, currency_fmt)
        ws_print.write('A18', 'Term Loan', normal_fmt)
        ws_print.write('D18', term_loan, currency_fmt)
        ws_print.write('A19', 'KVIC Margin Money (Subsidy)', bold_fmt)
        ws_print.write('D19', subsidy_amt, currency_fmt)

        # Sheet 2: DataSheet (Input Sheet) [cite: 400]
        ws_data = workbook.add_worksheet('DataSheet')
        ws_data.write('A1', 'DATA INPUT SHEET', header_fmt)
        ws_data.write('A5', 'Preference for sponsoring agency', normal_fmt)
        ws_data.write('G5', 'DIC', bold_fmt)
        ws_data.write('A6', 'Unit Location', normal_fmt)
        ws_data.write('G6', location, bold_fmt)

        # Sheet 3: Project_Report (Analytical) [cite: 458]
        ws_report = workbook.add_worksheet('Project_Report')
        ws_report.write('A1', 'PROJECT REPORT FOR', header_fmt)
        ws_report.write('G1', beneficiary_name, bold_fmt)

    return output.getvalue()

# --- 4. DOWNLOAD BUTTON ---
st.markdown("---")
if st.button("🚀 Finalize Rows 1-423 & Create Excel"):
    excel_file = generate_official_excel()
    st.download_button(
        label="📥 Download Full PMEGP Excel for Upload",
        data=excel_file,
        file_name=f"Official_DPR_{beneficiary_name.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.success("Your Excel file is formatted and ready for the government portal.")
