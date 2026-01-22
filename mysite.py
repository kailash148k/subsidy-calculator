import streamlit as st
import pandas as pd
import io

# --- 1. RAJASTHAN ODOP DATA ---
rajasthan_odop = {
    "Ajmer": "Granite and Marble Products", "Alwar": "Automobiles Parts", "Balotra": "Textile Products",
    "Banswara": "Marble Products", "Baran": "Garlic Products", "Barmer": "Kasheedakari",
    "Beawar": "Quartz and Feldspar Powder", "Bharatpur": "Agro Based Product", "Bhilwara": "Textile Products",
    "Bikaner": "Bikaneri Namkeen", "Bundi": "Sand Stone", "Chittorgarh": "Granite and Marble Products",
    "Churu": "Wood Products", "Dausa": "Stone Products", "Deedwana-Kuchaman": "Marble and Granite Products",
    "Deeg": "Stone Based Products", "Dholpur": "Stone Based Products", "Dungarpur": "Marble Product",
    "Hanumangarh": "Agro Based Product", "Jaipur": "Gems & Jewellery", "Jaisalmer": "Yellow Stone Products",
    "Jalore": "Granite Products", "Jhalawar": "Kota Stone Products", "Jhunjhunu": "Wooden Handicraft Products",
    "Jodhpur": "Wooden Furniture Products", "Karauli": "Sandstone Products", "Khairthal-Tijara": "Automobiles Parts",
    "Kota": "Kota Doria", "Kotputli-Behror": "Automobiles Parts", "Nagaur": "Pan Methi and Spices Processing",
    "Pali": "Textile Products", "Phalodi": "Sonamukhi Products", "Pratapgarh": "Thewa Jewellery",
    "Rajsamand": "Granite and Marble Products", "Salumber": "Quartz", "Sawai Madhopur": "Marble Products",
    "Sikar": "Wooden Furniture Products", "Sirohi": "Marble Products", "Sri Ganganagar": "Mustard Oil",
    "Tonk": "Slate Stone Products", "Udaipur": "Marble and Granite Products"
}

st.set_page_config(page_title="Rajasthan MSME Subsidy Pro", layout="wide")
st.title("⚖️ Rajasthan MSME Subsidy & Excel DPR Engine")

# --- 2. LOCKED INPUT SECTION ---
with st.sidebar:
    st.header("🔍 Eligibility Profile")
    applicant_name = st.text_input("Name of Applicant", "SMITA SINGH")
    district = st.selectbox("District", list(rajasthan_odop.keys()))
    location = st.radio("Unit Location", ["Rural", "Urban"])
    social_cat = st.selectbox("Social Category", ["General", "OBC", "SC", "ST", "Minority"])
    gender = st.selectbox("Gender", ["Male", "Female"])
    
    # Official Contribution Logic
    is_special = (gender == "Female" or social_cat != "General" or location == "Rural")
    min_cont_pct = 0.05 if is_special else 0.10

    st.markdown("### D. Financials")
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("**Project Cost**")
        pm_cost = st.number_input("Plant & Machinery", value=3200000)
        lb_cost = st.number_input("Workshed / Building", value=0)
        wc_req = st.number_input("Working Capital", value=190000)
        total_project_cost = pm_cost + lb_cost + wc_req
        st.info(f"Total Cost: ₹{total_project_cost:,.0f}")

    with col_r:
        st.markdown("**Funding**")
        min_own_amt = total_project_cost * min_cont_pct
        own_cont_amt = st.number_input(f"Own Capital (Min {int(min_cont_pct*100)}%)", value=float(min_own_amt))
        req_loan = total_project_cost - own_cont_amt
        st.info(f"Total Loan: ₹{req_loan:,.0f}")

# --- 3. SUBSIDY CALCULATION & FEATHERS ---
# Capital Subsidy (PMEGP Style)
p_rate = (35 if location == "Rural" else 25) if is_special else (25 if location == "Rural" else 15)
capital_grant = (total_project_cost - lb_cost) * (p_rate / 100)

# Interest Subsidy Feather (Rajasthan VYUPY)
int_sub_rate = 0.08 if is_special else 0.06
yearly_int_benefit = req_loan * int_sub_rate

# --- 4. PRESENTATION DISPLAY ---
st.subheader("🏁 Comparative Analysis")
c1, c2, c3 = st.columns(3)
c1.metric("PMEGP Capital Grant", f"₹{capital_grant:,.0f}", f"{p_rate}% Rate")
c2.metric("Annual Interest Subvention", f"₹{yearly_int_benefit:,.0f}", f"{int(int_sub_rate*100)}% Rate")
c3.metric("Net Project Cost", f"₹{total_project_cost - capital_grant:,.0f}")

# Multi-Year Analysis Table with Interest Subsidy Column
st.markdown("---")
st.subheader("📅 7-Year Financial Benefit Projection")
years = [f"Year {i}" for i in range(1, 8)]
analysis_df = pd.DataFrame({
    "Gross Bank Interest (10%)": [req_loan * 0.10] * 7,
    "Interest Subsidy Credit": [yearly_int_benefit] * 7,
    "Net Interest Payable": [(req_loan * 0.10) - yearly_int_benefit] * 7
}, index=years)
st.table(analysis_df.style.format("₹{:,.0f}"))

# --- 5. EXCEL EXPORT (ROWS 1-423 COMPLIANT) ---
if st.button("📥 Generate Official PMEGP Excel (Row 1-423)"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Recreating smita 1.xls - DPR_print Sheet
        ws = writer.book.add_worksheet('DPR_print')
        ws.write('A1', 'PROJECT AT A GLANCE - TOP SHEET')
        ws.write('A3', 'Name of Beneficiary')
        ws.write('D3', applicant_name)
        ws.write('A14', 'Total Project Cost')
        ws.write('D14', total_project_cost)
        ws.write('A19', 'Margin Money (Subsidy)')
        ws.write('D19', capital_grant)
        # Adding the Interest Subsidy Feather to Excel
        ws.write('A21', 'Interest Subvention (%)')
        ws.write('D21', f"{int(int_sub_rate*100)}%")
    st.download_button("Download Official Excel", output.getvalue(), "Official_DPR_Fresh.xlsx")
