import pandas as pd

# Define the business outcomes and their associated processes
BUSINESS_OUTCOME_MAP = {
    "Increased Customer Satisfaction": [
        "1A", "1B", "1C", "1D", "2A", "2D", "3D", "6A", "10D", "11A", "11D"
    ],
    "Reduced Payment Processing Time": [
        "3A", "3B", "4A", "4B", "4C", "4D", "7A", "7B", "8A", "8B", "8D", "9B"
    ],
    "Enhanced Fraud Prevention": [
        "2A", "2B", "2C", "3C", "5A", "5B", "5C", "5D", "6B", "6C", "12A", "12D"
    ],
    "Improved Regulatory Compliance": [
        "2C", "3C", "5B", "5C", "9D", "12A", "12B", "12C", "12D"
    ],
    "Operational Cost Reduction": [
        "1D", "3A", "3B", "4C", "7A", "7B", "7C", "7D", "10A", "10C"
    ],
    "Increased Straight-Through Processing": [
        "1C", "3A", "3B", "3C", "3D", "4A", "4B", "4D", "7A", "7B", "7C", "10A"
    ],
    "Better Liquidity Management": [
        "4C", "8B", "8C", "9A", "9B", "9C", "11C"
    ],
    "Enhanced Data Analytics Capability": [
        "10B", "11A", "11B", "11C", "11D", "12B", "12D"
    ]
}

def get_business_outcomes():
    """Returns a list of all business outcomes."""
    return list(BUSINESS_OUTCOME_MAP.keys())

def get_processes_for_outcome(outcome):
    """Returns the list of process IDs associated with a business outcome."""
    return BUSINESS_OUTCOME_MAP.get(outcome, [])

def calculate_outcome_score(process_values, outcome):
    """Calculate the average score for a business outcome based on process scores."""
    process_ids = get_processes_for_outcome(outcome)
    if not process_ids:
        return 0
    
    total_score = sum(process_values.get(pid, 0) for pid in process_ids)
    return total_score / len(process_ids)

def get_outcome_process_details(process_values, questions, outcome):
    """Get detailed information about processes for a specific outcome."""
    process_ids = get_processes_for_outcome(outcome)
    details = []
    
    for pid in process_ids:
        details.append({
            "ID": pid,
            "Question": questions.get(pid, "Unknown"),
            "Score": process_values.get(pid, 0),
        })
    
    return sorted(details, key=lambda x: x["ID"])

def get_outcome_summary(process_values):
    """Generate summary statistics for all business outcomes."""
    summary = []
    
    for outcome in get_business_outcomes():
        score = calculate_outcome_score(process_values, outcome)
        process_count = len(get_processes_for_outcome(outcome))
        
        summary.append({
            "Outcome": outcome,
            "Score": score,
            "Process Count": process_count
        })
    
    return summary

def create_outcome_radar_data(process_values):
    """Generate data for the radar chart by business outcome."""
    data = []
    
    for outcome in get_business_outcomes():
        score = calculate_outcome_score(process_values, outcome)
        data.append({
            "Outcome": outcome,
            "Score": score
        })
    
    return data