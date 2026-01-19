from flask import Flask, request, jsonify

app = Flask(__name__)

def check_pmegp_eligibility(data):
    """
    Validates PMEGP eligibility based on the user's constraints.
    """
    # 1. Project Age Constraint
    if data.get('project_type') != 'new':
        return False, "Ineligible: Only NEW projects are eligible. Existing units are excluded."

    # 2. Subsidy Constraint
    if data.get('has_other_subsidies') is True:
        return False, "Ineligible: Units already receiving other government subsidies cannot apply."

    # 3. Applicant Type Constraint
    if data.get('applicant_type') != 'individual':
        return False, "Ineligible: This specific program is restricted to Individual Entrepreneurs only."

    # 4. Mandatory Education Check (Standard PMEGP Rule)
    # Manufacturing > 10L or Service > 5L requires 8th Pass
    cost = float(data.get('project_cost', 0))
    sector = data.get('sector') # 'manufacturing' or 'service'
    is_8th_pass = data.get('is_8th_pass', False)

    if sector == 'manufacturing' and cost > 1000000 and not is_8th_pass:
        return False, "Ineligible: Manufacturing projects over ₹10L require 8th standard pass."
    
    if sector == 'service' and cost > 500000 and not is_8th_pass:
        return False, "Ineligible: Service projects over ₹5L require 8th standard pass."

    return True, "Eligible: You meet the basic criteria for PMEGP."

@app.route('/validate', methods=['POST'])
def validate():
    user_data = request.json
    is_eligible, message = check_pmegp_eligibility(user_data)
    
    return jsonify({
        "status": "success" if is_eligible else "failed",
        "message": message
    })

if __name__ == '__main__':
    app.run(debug=True)
