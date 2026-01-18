import streamlit as st
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="SubsidyClaim Comparison", layout="wide")

st.title("⚖️ MSME Subsidy Comparison & Project Report")
st.markdown("---")

# --- 1. DETAILED USER INPUTS ---
with st.sidebar:
    st.header("Project Profile")
    name = st.text_input("Entrepreneur Name", "Kailash")
    sector = st.selectbox("Industry Sector", ["Manufacturing", "Service", "Food Processing", "Traditional Artisan"])
    state = st.selectbox("State", ["Rajasthan", "Other"])
    
    col_a, col_b = st.columns(2)
    with col_a:
        loc = st.selectbox("Location", ["Urban", "Rural"])
    with col_b:
        gender = st.selectbox("Gender", ["Male", "Female"])
        
    cat = st.selectbox("Social Category", ["General", "OBC", "SC", "ST", "Minority"])
    cost = st.number_input("Total Project Cost (INR)", min_value=10000, value=1000000, step=50000)

# Determining if "Special Category" applies
is_special = (gender == "Female" or cat != "General" or loc == "Rural")

# --- 2. MULTI-SCHEME ENGINE ---
results = []

# A. PMEGP Logic
pmegp_max_cost = 5000000 if sector == "Manufacturing" or sector == "Food Processing" else 2000000
eligible_pmegp_cost = min(cost, pmegp_max_cost)

if loc == "Rural":
    pmegp_rate = 0.35 if is_special else 0.25
else:
    pmegp_rate = 0.25 if is_special else 0.15 # Fix: 15% for Urban General

pmegp_benefit = eligible_pmegp_cost * pmegp_rate
results.append({"Scheme": "PMEGP", "Benefit Type": "Cash Subsidy", "Value": pmegp_benefit, "Details": f"{pmegp_rate*100}% Margin Money"})

# B. PMFME Logic (Food Processing)
if sector == "Food Processing":
    pmfme_sub = min(cost * 0.35, 1000000)
    results.append({"Scheme": "PMFME", "Benefit Type": "Cash Subsidy", "Value": pmfme_sub, "Details": "35% (Max 10L) for Food Units"})

# C. PM Vishwakarma (Artisans)
if sector == "Traditional Artisan" and cost <= 300000:
    vishwa_toolkit = 15000
    interest_saving = cost * 0.08 * 4 # Estimated 8% saving over 4 years
    results.append({"Scheme": "PM Vishwakarma", "Benefit Type": "Toolkit + Interest", "Value": vishwa_toolkit + interest_saving, "Details": "Toolkit + 5% Fixed Interest Loan"})

# D. RIPS 2024 (Rajasthan Interest Subvention)
if state == "Rajasthan":
    # 6% standard + 2% for special/women = 8% total subvention
    rips_rate = 0.08 if is_special else 0.06
    rips_saving = cost * rips_rate * 7 # 7-year benefit period
    results.append({"Scheme": "RIPS 2024", "Benefit Type": "Interest Saving", "Value": rips_saving, "Details": f"{rips_rate*100}% Subvention for 7 Years"})

# E. CLCSS (Tech Upgrade)
if sector == "Manufacturing":
    clcss_sub = min(cost, 10000000) * 0.15
    results.append({"Scheme": "CLCSS", "Benefit Type": "Machinery Subsidy", "Value": clcss_sub, "Details": "15% for Tech Upgradation"})

# --- 3. DISPLAY & COMPARISON ---
st.subheader("🏁 Best Subsidy Recommendations")
df = pd.DataFrame(results).sort_values(by="Value", ascending=False)

# Highlight Best
best_scheme = df.iloc[0]['Scheme']
st.success(f"🏆 **Recommended Scheme:** {best_scheme} (Estimated Benefit: ₹{df.iloc[0]['Value']:,.0f})")

st.table(df.style.format({"Value": "₹{:,.0f}"}))

# --- 4. PROJECT REPORT GENERATION ---
def create_dpr(name, cost, scheme_name, value):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "DETAILED PROJECT REPORT (SUMMARY)", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, f"Entrepreneur: {name}")
    pdf.ln(8)
    pdf.cell(100, 10, f"Project Cost: INR {cost:,.2f}")
    pdf.ln(8)
    pdf.cell(100, 10, f"Recommended Scheme: {scheme_name}")
    pdf.ln(8)
    pdf.cell(100, 10, f"Estimated Benefit: INR {value:,.2f}")
    
    # Financial breakdown
    pdf.ln(15)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(100, 10, "Means of Finance")
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(100, 10, f"- Promoter Contribution (10%): INR {cost*0.1:,.2f}")
    pdf.ln(8)
    pdf.cell(100, 10, f"- Bank Loan Required (90%): INR {cost*0.9:,.2f}")
    
    return pdf.output(dest='S').encode('latin-1')

st.markdown("---")
if st.button("Generate Detailed Project Report (PDF)"):
    report_bytes = create_dpr(name, cost, best_scheme, df.iloc[0]['Value'])
    st.download_button("📥 Download My Project Report", report_bytes, file_name="MSME_Report.pdf")
