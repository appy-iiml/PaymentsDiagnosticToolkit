import pandas as pd
import streamlit as st
from business_data import load_process_details

# KPI Matrix mapping for each process
KPI_MATRIX = {
    "1A": {"kpi": "Channel Transaction Success Rate (%)", "ppe_cap": "Lead PPE Cap: How PPE Engr Technical Solution Architects help Platform Mod Re-platform to Omni-channel"},
    "1B": {"kpi": "Input Validation Error Rate (%)", "ppe_cap": "Agile Implem: Sprint team re Contextual auth rules Platform Mod Stand-up api-IBAM+/NPC+UPI"},
    "1C": {"kpi": "Input Validation Error Rate (%)", "ppe_cap": "Program Debt: Deliver Kafka/Event-stream for data-masking Edge Consult: Design Micro+: NuBank / Finclear"},
    "1D": {"kpi": "Queue latency (ms) to hub", "ppe_cap": "Platform Mod Configure.io/a Transform.io ServiceNow C Low-code dev Camunda DM K8s"},
    "2A": {"kpi": "Authentication Success Rate (%)", "ppe_cap": "Platform Mod: Deploy MTrO, takeover Kong + HSM ServiceNow C Build wired JJ UPath-bot, m/l rules w/BRMS"},
    "2B": {"kpi": "Avg. Authentication Time (seconds)", "ppe_cap": "Regulated Ref: Replace code, Pega Decision Engine Program Debt: Integrate AM for Silent Edge / OCR"},
    "2C": {"kpi": "Fraud blocked pre-auth (%)", "ppe_cap": "Platform Mod: Wire GeoPop for Azure OpenAI Agile Implem: ML 'payment' SageMaker data models"},
    "2D": {"kpi": "% fraud-block-to-false-positive ratio", "ppe_cap": "Platform Mod: Smart router w Volante Smartfx/ Rapid Program Debt: Deliver new TCS Quartz hub"},
    "3A": {"kpi": "Pre-Processing Rejection Rate (%)", "ppe_cap": "Regulated Ref: Implement SA-born Framwork for Mule APIs Platform Mod: Deploy gRPC FaaSLite cloud functions"},
    "3B": {"kpi": "Accuracy", "ppe_cap": "Program Debt: Integrate 'Outer Quantum + AR services' Edge Consult: Real-time Between-the-lines Graph DB"},
    "3C": {"kpi": "Fraud Detection Rate (%) & Fraud False Positive Rate (%)", "ppe_cap": "ServiceNow C: Configure IVS GenNext/wt/ Edge Graph ServiceNow C: Rapid UX node Twilio Verify QR verify"},
    "3D": {"kpi": "Sanctions Screening STP Rate (%) / Avg. Alert/Case Resolution Time (hours)", "ppe_cap": "Salesforce CC: Rapid UX node Tw/Vo Verify QR verify Platform Mod: Event API brkr Finastra Event Manager"},
    "4A": {"kpi": "Optimized fee per tx (USD)", "ppe_cap": "Regulated Ref: Implement re-Containterized TPE Platform Mod: Containerized SWIFT Trans/hub"},
    "4B": {"kpi": "Cut-off Miss Rate (%)", "ppe_cap": "Program Debt: Integrate GE Ref-data quick-change Platform Mod: Auto-split rule MuleaSoft transa"},
    "4C": {"kpi": "Real-time fraud detection F-score", "ppe_cap": "Platform Mod Expose Kafka & UPath-as Service"},
    "4D": {"kpi": "Mean repair handling time", "ppe_cap": "Platform Mod: Replace dev'd IBM MQ on Openshift Platform Mod: K8S IPA auto- Kubernetes Archs"},
    "5A": {"kpi": "Fraud Detection Rate (%) & Fraud False Positive Rate (%)", "ppe_cap": "SalesForce Cx: Track UETR / (z SWIFT gpi, Grids) Platform Mod: Web/host Auto AWS transit/block"},
    "5B": {"kpi": "Sanctions Screening STP Rate (%)", "ppe_cap": "Platform Mod: Real-time hub Fusion-MLM, prebuilt Program Debt: Migrate to SA+ Cloud proxy auth/Okt"},
    "5C": {"kpi": "PEP / AML Compliance Rate", "ppe_cap": "Platform Mod: Treasury user t GITB cash-fold auto (No native PPE --- ONLY remote expert)"},
    "5D": {"kpi": "Avg. Time in Pre-Processing Repair (hours)", "ppe_cap": "ServiceNow C: Reconciliation Duo/BlueLight /Redline MS Dynamics Event-driven + Kafka + Dynamo DB"},
    "6A": {"kpi": "Authorization Turnaround Time (Avg. hours/minutes)", "ppe_cap": "ServiceNow C: Auto-rebill EF Pega BPM / RPA SalesForce Cx: Self-service ops.gw API + Tw. Flex + S"},
    "6B": {"kpi": "Post-Processing Authorization Rejection Rate (%)", "ppe_cap": "MS Dynamics On-demand B-Away API Message bus Platform Mod: Stream to Splk Kafka + Snowfl"},
    "6C": {"kpi": "Operational Loss Reduction", "ppe_cap": "SalesForce Cx: GraphQL suite Graph-D + Logs-D Platform Mod: Immutable AA AWS QLDB, Vertica"},
    "6D": {"kpi": "Compliance Rate", "ppe_cap": "Program Debt: Cloud Guard Vault StrucLed SMS ServiceNow C: RegTech e-Tran AxonIot, galxe/Ov"},
    "7A": {"kpi": "Message Formatting/Mapping STP Rate (%)", "ppe_cap": "MS Dynamics Secure smart SmartView SlaS"},
    "7B": {"kpi": "Avg. Time in Mapping/Formatter Repair Queue (hours)", "ppe_cap": ""},
    "7C": {"kpi": "% data loss events logged", "ppe_cap": ""},
    "7D": {"kpi": "Mean repair handling time", "ppe_cap": ""},
    "8A": {"kpi": "Clearing Network Success Rate (%)", "ppe_cap": ""},
    "8B": {"kpi": "End-to-End Payment Latency (Avg. hours/minutes)", "ppe_cap": ""},
    "8C": {"kpi": "Activity Execution on-time", "ppe_cap": ""},
    "8D": {"kpi": "Throughput", "ppe_cap": ""},
    "9A": {"kpi": "On-Time Settlement Rate (%)", "ppe_cap": ""},
    "9B": {"kpi": "Exact Settlement Rate (%)", "ppe_cap": ""},
    "9C": {"kpi": "Intraday Liquidity Buffer Usage (%) / Cost (bps)", "ppe_cap": ""},
    "9D": {"kpi": "Operational Loss Reduction", "ppe_cap": ""},
    "10A": {"kpi": "Reconciliation Auto-Match Rate (%)", "ppe_cap": ""},
    "10B": {"kpi": "Avg. Age of Open Reconciliation Break Items (days)", "ppe_cap": ""},
    "10C": {"kpi": "Value of Unreconciled Items ($/€/₹)", "ppe_cap": ""},
    "10D": {"kpi": "Net-Promoter Score", "ppe_cap": ""},
    "11A": {"kpi": "Data Latency for Key Reports/Dashboards (Avg. minutes/hours)", "ppe_cap": ""},
    "11B": {"kpi": "Client Self-Service Reporting Usage Rate (%)", "ppe_cap": ""},
    "11C": {"kpi": "Productivity (cross-sell)", "ppe_cap": ""},
    "11D": {"kpi": "Net-Promoter Score", "ppe_cap": ""},
    "12A": {"kpi": "Regulatory Reporting Accuracy / Timeliness Rate (%)", "ppe_cap": ""},
    "12B": {"kpi": "Avg. Time to Retrieve Archived Transaction Data (hours/days)", "ppe_cap": ""},
    "12C": {"kpi": "Compliance Rate", "ppe_cap": ""},
    "12D": {"kpi": "Compliance Rate", "ppe_cap": ""}
}

# Load the benchmark data from the provided images
def load_data():
    """
    Load and process the benchmark data for different banks
    """
    # Create data structure based on the provided images
    data = {
        "JPMC (Global)": {
            1: 3.32, 2: 3.32, 3: 2.64, 4: 2.64, 5: 3.66, 6: 2.64, 
            7: 1.98, 8: 3.66, 9: 4, 10: 2.64, 11: 3.66, 12: 2.64,
            "Overall": 3.04
        },
        "DBS (Asia)": {
            1: 3.32, 2: 2.66, 3: 2.66, 4: 2.66, 5: 3.32, 6: 2.66, 
            7: 2.66, 8: 3.32, 9: 3.32, 10: 1.98, 11: 2.66, 12: 1.98,
            "Overall": 2.85
        },
        "HSBC (Wholesale)": {
            1: 3.32, 2: 2.66, 3: 1.98, 4: 2.66, 5: 3.32, 6: 2.66, 
            7: 2.66, 8: 3.32, 9: 2.66, 10: 1.98, 11: 2.66, 12: 1.98,
            "Overall": 2.72
        },
        "HDFC (India)": {
            1: 2.66, 2: 2.66, 3: 1.98, 4: 1.98, 5: 2.66, 6: 1.98, 
            7: 1.98, 8: 2.66, 9: 2.66, 10: 1.98, 11: 1.98, 12: 1.32,
            "Overall": 2.3
        },
        "SBI (Scale)": {
            1: 2.66, 2: 1.98, 3: 1.32, 4: 1.98, 5: 1.98, 6: 1.98, 
            7: 1.98, 8: 2.66, 9: 2.66, 10: 1.32, 11: 1.32, 12: 1.32,
            "Overall": 1.89
        },
        "ICICI Bank": {
            1: 3.32, 2: 2.64, 3: 1.32, 4: 1.32, 5: 2.64, 6: 2.64, 
            7: 1.32, 8: 2.64, 9: 2.64, 10: 1.32, 11: 1.32, 12: 1.32,
            "Overall": 1.95
        }
    }
    
    # Also create a mapping of stage names for reference
    stage_names = {
        1: "Payment Initiation & Data Capture",
        2: "Authentication & Identity Validation",
        3: "Pre-Submission Validation",
        4: "Payment Orchestration & Routing",
        5: "Risk, Fraud & Compliance",
        6: "Final Authorisation & Approval",
        7: "Message Generation & Transformation",
        8: "Transmission, Clearing & ACK",
        9: "Settlement & Funds Movement",
        10: "Reconciliation & Exceptions",
        11: "Reporting, Analytics & Notifications",
        12: "Audit, Archival & Compliance"
    }
    
    return data, stage_names

def get_bank_names():
    """Returns list of bank names from the benchmark data"""
    data, _ = load_data()
    return list(data.keys())

def get_bank_scores(bank_name):
    """Returns the scores for a specific bank"""
    data, _ = load_data()
    if bank_name in data:
        return data[bank_name]
    return None

def get_stage_names():
    """Returns mapping of stage IDs to names"""
    _, stage_names = load_data()
    return stage_names

def get_process_data_for_stage(stage_id):
    """Returns process data for a specific stage"""
    process_data = load_process_details()
    return [p for p in process_data if p['stage'].startswith(get_stage_names()[stage_id])]

def create_assessment_dataframe(assessment_data):
    """Convert assessment data to DataFrame for analysis"""
    data = []
    for process_id, score in assessment_data.items():
        data.append({
            "Process ID": process_id,
            "Score": score
        })
    return pd.DataFrame(data)