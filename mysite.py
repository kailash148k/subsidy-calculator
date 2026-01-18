results = []

# 1. ODOP Benefit (Rajasthan 2024 Policy)
if is_odop_unit:
    # 25% for micro units, capped at 15L
    odop_benefit = min(total_project_cost * 0.25, 1500000)
    results.append({
        "Scheme": "Rajasthan ODOP 2024",
        "Benefit": "Margin Money Grant",
        "Value": odop_benefit,
        "Detail": "25% Grant on ODOP Project Cost"
    })

# 2. PM Vishwakarma (Full Benefits)
if is_vishwakarma:
    vishwa_toolkit = 15000 # One-time
    # Collateral-free loan benefit (5% int vs 12% market)
    vishwa_int_saving = min(total_project_cost, 300000) * 0.07 * 5 
    results.append({
        "Scheme": "PM Vishwakarma",
        "Benefit": "Toolkit + Interest Subvention",
        "Value": vishwa_toolkit + vishwa_int_saving,
        "Detail": "₹15,000 Toolkit + 5% Subsidized Interest"
    })

# 3. Additional Rajasthan Interest Subvention (Over & Above RIPS 2024)
# ODOP units get an additional 2% subvention over the base RIPS rate
if is_odop_unit:
    additional_rips = term_loan_amt * 0.02 * 7 # 7 Years
    results.append({
        "Scheme": "RIPS 2024 (Additional)",
        "Benefit": "Interest Subvention",
        "Value": additional_rips,
        "Detail": "Extra 2% Interest Saving for ODOP Units"
    })
