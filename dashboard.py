import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from business_data import load_process_details
from data_loader import get_stage_names, KPI_MATRIX
from visualization import create_radar_chart

# Define the key metrics for the control tower
KEY_METRICS = {
    "STP Rate": {
        "description": "Straight-Through Processing rate - percentage of payments that process without manual intervention",
        "target": 0.95,  # 95% target
        "current": 0.82,  # Example current value
        "processes": ["3A", "3B", "3C", "4A", "4B", "7A", "7B", "7C", "10A"],
        "representative_kpi": "% hits auto-cleared < 1 min",
        "business_outcome": "Risk",
        "bo_indicator": "Compliance Risk"
    },
    "Cost per Transaction": {
        "description": "Average cost to process a single payment transaction",
        "target": 0.15,  # $0.15 target
        "current": 0.28,  # Example current value
        "processes": ["1D", "3A", "3B", "4C", "7A", "7B", "7C", "7D", "10A", "10C"],
        "representative_kpi": "$/payment to process (USD)",
        "business_outcome": "Cost Reduction",
        "bo_indicator": "Activity Execution Cost"
    },
    "Fraud Loss": {
        "description": "Percentage of transaction value lost to fraud",
        "target": 0.0005,  # 0.05% target
        "current": 0.0012,  # Example current value
        "processes": ["2A", "2B", "2C", "3C", "5A", "5B", "5C", "5D", "6B"],
        "representative_kpi": "% fraud blocked pre-auth",
        "business_outcome": "Credit & Operational Risk",
        "bo_indicator": "Fraud Prevention"
    },
    "Latency": {
        "description": "Average processing time for transactions in seconds",
        "target": 2.5,  # 2.5 seconds target
        "current": 4.8,  # Example current value
        "processes": ["3A", "4A", "4B", "4D", "7A", "7B", "8A", "8B", "8D", "9B"],
        "representative_kpi": "Queue latency (ms) to hub",
        "business_outcome": "Speed-to-Market",
        "bo_indicator": "Activity Execution Time"
    }
}

# Payment streams
PAYMENT_STREAMS = [
    "Domestic Low Value (ACH/BACS)",
    "Domestic High Value (RTGS/Fedwire)",
    "International (SWIFT/Cross-Border)",
    "Real-Time Payments (FedNow/RTP)",
    "Cards Processing (Debit/Credit)"
]

# Business goals (based on the provided KPI mapping)
BUSINESS_GOALS = [
    "Customer Satisfaction",
    "Speed-to-Market",
    "Risk Management",
    "Cost Reduction",
    "Revenue Increase"
]

# Map business outcomes to process IDs, KPIs and improvement areas
GOAL_PROCESS_MAP = {
    "Customer Satisfaction": {
        "processes": ["1A", "1B", "1C", "1D", "2A", "2D", "6A", "8D", "9A", "10D", "11A"],
        "key_metric": "STP Rate",
        "representative_kpis": [
            "% users on biometric/passkey login",
            "Avg. clicks/time to set up tx", 
            "Login failure rate",
            "Confirmation latency to user(s)",
            "% bulk tx approved < SLA",
            "Walk time to clearing cycle (s)",
            "Customer dispute resolution days"
        ],
        "bo_indicators": ["Convenience", "Productivity", "Accuracy", "Net-Promoter Score"],
        "improvement_areas": ["User Experience", "Authentication Flow", "Payment Confirmation"]
    },
    "Speed-to-Market": {
        "processes": ["1D", "3A", "4A", "4B", "4D", "7A", "7B", "8A", "8B", "8D", "9B"],
        "key_metric": "Latency",
        "representative_kpis": [
            "Queue latency (ms) to hub",
            "Avg. session setup latency",
            "First-time-right rate",
            "API fail rate at cutoff",
            "Auto-enrichment hit-rate",
            "Clearing ACK latency (s)"
        ],
        "bo_indicators": ["Activity Execution Time", "Productivity", "Throughput"],
        "improvement_areas": ["Queue Optimization", "API Performance", "Processing Efficiency"]
    },
    "Risk Management": {
        "processes": ["2A", "2B", "2C", "3C", "5A", "5B", "5C", "5D", "6B", "6C", "12A", "12D"],
        "key_metric": "Fraud Loss",
        "representative_kpis": [
            "% fraud blocked pre-auth",
            "% dual-auth breaches caught",
            "% hits auto-cleared < 1 min",
            "Real-time fraud detection F-score",
            "False positive rate",
            "Suspicious activity/1 k tx",
            "% events immutably logged",
            "Restore test success rate"
        ],
        "bo_indicators": ["Fraud Prevention", "Operational Loss", "Compliance Risk", "KYC/AML Compliance"],
        "improvement_areas": ["Fraud Detection", "Authentication Security", "Compliance Automation"]
    },
    "Cost Reduction": {
        "processes": ["1D", "3A", "3B", "4C", "7A", "7B", "7C", "7D", "10A", "10C"],
        "key_metric": "Cost per Transaction",
        "representative_kpis": [
            "Rejection rate at stage",
            "$/payment to process (USD)",
            "% mis-routed payments",
            "Avg. manual repair time (minutes)",
            "Mean repair handling time",
            "EoD statement completion time"
        ],
        "bo_indicators": ["Activity Execution Cost", "Rework Cost", "Turn-Around Time", "Productivity"],
        "improvement_areas": ["Automation", "STP Enhancement", "Error Reduction"]
    },
    "Revenue Increase": {
        "processes": ["1A", "1B", "4C", "6A", "11B", "11C", "11D"],
        "key_metric": "STP Rate",
        "representative_kpis": [
            "Optimized fee per tx (USD)",
            "Adoption % of self-serve BI",
            "% cross-border tx with live ETA"
        ],
        "bo_indicators": ["Throughput Multiplier", "Productivity", "Net-Promoter Score"],
        "improvement_areas": ["Fee Optimization", "Self-Service Analytics", "Cross-Border Improvements"]
    }
}

# Improvement recommendations mapped to business outcomes
IMPROVEMENT_RECOMMENDATIONS = {
    "Customer Satisfaction": {
        "quick_wins": [
            {"title": "Biometric Authentication Expansion", "impact": "High", "effort": "Medium", "timeframe": "3 months", "kpi_impact": "Increase % users on biometric/passkey login by 35%"},
            {"title": "Streamlined Payment Entry UX", "impact": "Medium", "effort": "Low", "timeframe": "2 months", "kpi_impact": "Reduce avg. clicks to set up tx by 40%"},
            {"title": "Real-time Payment Status Notifications", "impact": "Medium", "effort": "Low", "timeframe": "2 months", "kpi_impact": "Reduce confirmation latency to user by 60%"}
        ],
        "strategic_investments": [
            {"title": "Omni-channel Payment Experience Platform", "impact": "Very High", "effort": "High", "timeframe": "12 months", "kpi_impact": "Improve Net-Promoter Score by 25 points"},
            {"title": "AI-powered Dispute Resolution System", "impact": "High", "effort": "High", "timeframe": "9 months", "kpi_impact": "Reduce dispute resolution time by 70%"}
        ]
    },
    "Speed-to-Market": {
        "quick_wins": [
            {"title": "Queue Processing Optimization", "impact": "High", "effort": "Medium", "timeframe": "2 months", "kpi_impact": "Reduce queue latency by 65%"},
            {"title": "API Request Caching Implementation", "impact": "Medium", "effort": "Low", "timeframe": "1 month", "kpi_impact": "Reduce API fail rate at cutoff by 40%"},
            {"title": "Parallel ACK Processing", "impact": "High", "effort": "Medium", "timeframe": "3 months", "kpi_impact": "Reduce clearing ACK latency by 55%"}
        ],
        "strategic_investments": [
            {"title": "Event-Driven Payment Architecture", "impact": "Very High", "effort": "High", "timeframe": "12 months", "kpi_impact": "Improve overall activity execution time by 80%"},
            {"title": "Auto-enrichment Machine Learning System", "impact": "High", "effort": "High", "timeframe": "9 months", "kpi_impact": "Increase auto-enrichment hit rate by 200%"}
        ]
    },
    "Risk Management": {
        "quick_wins": [
            {"title": "Enhanced Pre-Auth Fraud Rules", "impact": "High", "effort": "Medium", "timeframe": "2 months", "kpi_impact": "Increase % fraud blocked pre-auth by 25%"},
            {"title": "Dual-Auth Verification Enhancement", "impact": "High", "effort": "Medium", "timeframe": "3 months", "kpi_impact": "Increase % dual-auth breaches caught by 40%"},
            {"title": "Suspicious Activity Detection Tuning", "impact": "Medium", "effort": "Low", "timeframe": "1 month", "kpi_impact": "Improve suspicious activity detection rate by 30%"}
        ],
        "strategic_investments": [
            {"title": "Real-time AI Fraud Detection Platform", "impact": "Very High", "effort": "High", "timeframe": "12 months", "kpi_impact": "Improve F-score by 0.3 points while reducing false positives by 45%"},
            {"title": "Blockchain-based Transaction Immutability", "impact": "High", "effort": "High", "timeframe": "9 months", "kpi_impact": "Achieve 100% immutable logging of all transactions"}
        ]
    },
    "Cost Reduction": {
        "quick_wins": [
            {"title": "Rejection Root Cause Analysis & Fix", "impact": "High", "effort": "Medium", "timeframe": "3 months", "kpi_impact": "Reduce rejection rate at stage by 35%"},
            {"title": "Payment Routing Optimization", "impact": "Medium", "effort": "Low", "timeframe": "2 months", "kpi_impact": "Reduce mis-routed payments by 65%"},
            {"title": "Repair Workflow Automation", "impact": "High", "effort": "Medium", "timeframe": "4 months", "kpi_impact": "Reduce mean repair handling time by 50%"}
        ],
        "strategic_investments": [
            {"title": "End-to-end Payment Process Automation", "impact": "Very High", "effort": "High", "timeframe": "18 months", "kpi_impact": "Reduce $/payment to process by 75%"},
            {"title": "Real-time Reconciliation Platform", "impact": "High", "effort": "High", "timeframe": "12 months", "kpi_impact": "Reduce EoD statement completion time by 90%"}
        ]
    },
    "Revenue Increase": {
        "quick_wins": [
            {"title": "Dynamic Fee Optimization Engine", "impact": "High", "effort": "Medium", "timeframe": "3 months", "kpi_impact": "Increase optimized fee per tx by 12%"},
            {"title": "Self-Service BI Dashboard Rollout", "impact": "Medium", "effort": "Low", "timeframe": "2 months", "kpi_impact": "Increase adoption % of self-serve BI by 60%"},
            {"title": "Cross-Border Payment Tracking", "impact": "Medium", "effort": "Medium", "timeframe": "4 months", "kpi_impact": "Increase % cross-border tx with live ETA to 85%"}
        ],
        "strategic_investments": [
            {"title": "AI-driven Fee Personalization Platform", "impact": "Very High", "effort": "High", "timeframe": "12 months", "kpi_impact": "Increase revenue per payment by 35%"},
            {"title": "Embedded Payments Marketplace", "impact": "High", "effort": "High", "timeframe": "15 months", "kpi_impact": "Create new revenue stream worth $3M/year"}
        ]
    }
}

def get_metric_status(metric_data):
    """Determine the status (green, amber, red) based on metric value vs target"""
    current = metric_data["current"]
    target = metric_data["target"]
    
    # For metrics where lower is better (Cost, Fraud, Latency)
    if metric_data in [KEY_METRICS["Cost per Transaction"], KEY_METRICS["Fraud Loss"], KEY_METRICS["Latency"]]:
        if current <= target * 1.1:  # Within 10% of target
            return "green"
        elif current <= target * 1.3:  # Within 30% of target
            return "amber"
        else:
            return "red"
    else:  # For metrics where higher is better (STP Rate)
        if current >= target * 0.9:  # Within 10% of target
            return "green"
        elif current >= target * 0.7:  # Within 30% of target
            return "amber"
        else:
            return "red"

def render_control_tower_metrics():
    """Render the control tower metrics dashboard"""
    st.header("Payment Control Tower Dashboard")
    st.markdown("<p class='subtitle'>Real-time view of key payment performance indicators</p>", unsafe_allow_html=True)
    
    # Create the four metric tiles in a grid
    col1, col2 = st.columns(2)
    
    with col1:
        # STP Rate
        status = "green" if KEY_METRICS["STP Rate"]["current"] >= KEY_METRICS["STP Rate"]["target"] * 0.9 else ("amber" if KEY_METRICS["STP Rate"]["current"] >= KEY_METRICS["STP Rate"]["target"] * 0.7 else "red")
        st.markdown(f"""
        <div class='metric-tile {status}'>
            <h3>STP Rate</h3>
            <div class='metric-value'>{KEY_METRICS["STP Rate"]["current"]*100:.1f}%</div>
            <div class='metric-target'>Target: {KEY_METRICS["STP Rate"]["target"]*100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Fraud Loss
        status = "green" if KEY_METRICS["Fraud Loss"]["current"] <= KEY_METRICS["Fraud Loss"]["target"] * 1.1 else ("amber" if KEY_METRICS["Fraud Loss"]["current"] <= KEY_METRICS["Fraud Loss"]["target"] * 1.3 else "red")
        st.markdown(f"""
        <div class='metric-tile {status}'>
            <h3>Fraud Loss</h3>
            <div class='metric-value'>{KEY_METRICS["Fraud Loss"]["current"]*100:.3f}%</div>
            <div class='metric-target'>Target: {KEY_METRICS["Fraud Loss"]["target"]*100:.3f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Cost per Transaction
        status = "green" if KEY_METRICS["Cost per Transaction"]["current"] <= KEY_METRICS["Cost per Transaction"]["target"] * 1.1 else ("amber" if KEY_METRICS["Cost per Transaction"]["current"] <= KEY_METRICS["Cost per Transaction"]["target"] * 1.3 else "red")
        st.markdown(f"""
        <div class='metric-tile {status}'>
            <h3>Cost per Transaction</h3>
            <div class='metric-value'>${KEY_METRICS["Cost per Transaction"]["current"]:.2f}</div>
            <div class='metric-target'>Target: ${KEY_METRICS["Cost per Transaction"]["target"]:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Latency
        status = "green" if KEY_METRICS["Latency"]["current"] <= KEY_METRICS["Latency"]["target"] * 1.1 else ("amber" if KEY_METRICS["Latency"]["current"] <= KEY_METRICS["Latency"]["target"] * 1.3 else "red")
        st.markdown(f"""
        <div class='metric-tile {status}'>
            <h3>Processing Latency</h3>
            <div class='metric-value'>{KEY_METRICS["Latency"]["current"]:.1f}s</div>
            <div class='metric-target'>Target: {KEY_METRICS["Latency"]["target"]:.1f}s</div>
        </div>
        """, unsafe_allow_html=True)

def render_payment_streams_analysis():
    """Render payment streams analysis section"""
    st.subheader("Payment Streams Analysis")
    
    # Payment stream selector
    selected_stream = st.selectbox(
        "Select Payment Stream for Analysis:",
        options=PAYMENT_STREAMS
    )
    
    # Mock data for payment stream metrics
    stream_metrics = {
        "Domestic Low Value (ACH/BACS)": {
            "volume": "2.3M",
            "value": "$45.2B",
            "stp_rate": "94.2%",
            "avg_latency": "2.1s",
            "cost_per_tx": "$0.12"
        },
        "Domestic High Value (RTGS/Fedwire)": {
            "volume": "156K",
            "value": "$127.8B",
            "stp_rate": "98.7%",
            "avg_latency": "1.8s",
            "cost_per_tx": "$2.45"
        },
        "International (SWIFT/Cross-Border)": {
            "volume": "89K",
            "value": "$23.4B",
            "stp_rate": "78.3%",
            "avg_latency": "12.3s",
            "cost_per_tx": "$8.75"
        },
        "Real-Time Payments (FedNow/RTP)": {
            "volume": "1.8M",
            "value": "$12.7B",
            "stp_rate": "96.8%",
            "avg_latency": "0.9s",
            "cost_per_tx": "$0.08"
        },
        "Cards Processing (Debit/Credit)": {
            "volume": "12.4M",
            "value": "$89.3B",
            "stp_rate": "99.1%",
            "avg_latency": "0.3s",
            "cost_per_tx": "$0.05"
        }
    }
    
    # Display metrics for selected stream
    if selected_stream in stream_metrics:
        metrics = stream_metrics[selected_stream]
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Daily Volume", metrics["volume"])
        with col2:
            st.metric("Daily Value", metrics["value"])
        with col3:
            st.metric("STP Rate", metrics["stp_rate"])
        with col4:
            st.metric("Avg Latency", metrics["avg_latency"])
        with col5:
            st.metric("Cost/Tx", metrics["cost_per_tx"])

def render_business_goals_section():
    """Render business goals and improvement recommendations"""
    st.subheader("Business Goal Analysis & Improvement Roadmap")
    
    # Business goal selector
    selected_goal = st.selectbox(
        "Select Business Goal:",
        options=BUSINESS_GOALS
    )
    
    if selected_goal in GOAL_PROCESS_MAP:
        goal_data = GOAL_PROCESS_MAP[selected_goal]
        
        # Display goal overview
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {selected_goal}")
            st.write(f"**Key Metric:** {goal_data['key_metric']}")
            st.write(f"**Contributing Processes:** {len(goal_data['processes'])} processes")
            
            # Representative KPIs
            st.markdown("**Representative KPIs:**")
            for kpi in goal_data["representative_kpis"]:
                st.write(f"• {kpi}")
        
        with col2:
            # Business outcome indicators
            st.markdown("**Business Outcome Indicators:**")
            for indicator in goal_data["bo_indicators"]:
                st.write(f"• {indicator}")
        
        # Improvement recommendations
        if selected_goal in IMPROVEMENT_RECOMMENDATIONS:
            recommendations = IMPROVEMENT_RECOMMENDATIONS[selected_goal]
            
            st.markdown("### Improvement Roadmap")
            
            # Quick wins
            st.markdown("#### Quick Wins (1-4 months)")
            for i, rec in enumerate(recommendations["quick_wins"]):
                with st.expander(f"Quick Win {i+1}: {rec['title']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Impact:** {rec['impact']}")
                    with col2:
                        st.write(f"**Effort:** {rec['effort']}")
                    with col3:
                        st.write(f"**Timeframe:** {rec['timeframe']}")
                    st.write(f"**Expected KPI Impact:** {rec['kpi_impact']}")
            
            # Strategic investments
            st.markdown("#### Strategic Investments (6-18 months)")
            for i, rec in enumerate(recommendations["strategic_investments"]):
                with st.expander(f"Strategic Investment {i+1}: {rec['title']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Impact:** {rec['impact']}")
                    with col2:
                        st.write(f"**Effort:** {rec['effort']}")
                    with col3:
                        st.write(f"**Timeframe:** {rec['timeframe']}")
                    st.write(f"**Expected KPI Impact:** {rec['kpi_impact']}")

def render_process_dependency_view():
    """Render process dependency and impact analysis"""
    st.subheader("Process Dependency & Impact Analysis")
    
    # Create a simple dependency visualization
    process_data = load_process_details()
    
    # Select a process to analyze
    process_options = [f"{p['qid']}: {p['process']}" for p in process_data]
    selected_process = st.selectbox(
        "Select Process for Dependency Analysis:",
        options=process_options
    )
    
    if selected_process:
        process_id = selected_process.split(":")[0]
        
        # Find the process details
        process_detail = next((p for p in process_data if p['qid'] == process_id), None)
        
        if process_detail:
            st.markdown(f"### {process_detail['process']}")
            st.write(process_detail['description'])
            
            # Mock dependency analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Upstream Dependencies")
                st.write("Processes that this process depends on:")
                # Mock upstream dependencies
                if process_id in ["2A", "2B", "2C"]:
                    st.write("• 1A: Channel Setup & Session Management")
                    st.write("• 1D: Data Enrichment & Standardization")
                elif process_id in ["3A", "3B", "3C"]:
                    st.write("• 1D: Data Enrichment & Standardization")
                    st.write("• 2A: Multi-Factor Authentication")
                else:
                    st.write("• Multiple upstream processes identified")
            
            with col2:
                st.markdown("#### Downstream Impact")
                st.write("Processes that depend on this process:")
                # Mock downstream impact
                if process_id in ["1A", "1B", "1C"]:
                    st.write("• 2A: Multi-Factor Authentication")
                    st.write("• 3A: Business Rules Engine")
                elif process_id in ["2A", "2B", "2C"]:
                    st.write("• 3A: Business Rules Engine")
                    st.write("• 4A: Intelligent Payment Routing")
                else:
                    st.write("• Multiple downstream processes affected")

def render_dashboard_tab():
    """Main function to render the complete dashboard tab"""
    
    # Control tower metrics at the top
    render_control_tower_metrics()
    
    # Add some spacing
    st.markdown("---")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "Payment Streams", 
        "Business Goals", 
        "Process Dependencies", 
        "Executive Summary"
    ])
    
    with tab1:
        render_payment_streams_analysis()
    
    with tab2:
        render_business_goals_section()
    
    with tab3:
        render_process_dependency_view()
    
    with tab4:
        # Executive summary
        st.subheader("Executive Summary")
        
        st.markdown("""
        ### Key Findings
        
        **Performance Highlights:**
        - Overall STP Rate at 82% (target: 95%) - **13 percentage points below target**
        - Processing costs 87% above target at $0.28 per transaction
        - Fraud prevention performing well with losses at 0.12% vs 0.05% target
        - Latency concerns with 4.8s average vs 2.5s target
        
        **Priority Areas for Improvement:**
        1. **Straight-Through Processing** - Focus on automation and exception handling
        2. **Cost Optimization** - Implement intelligent routing and reduce manual interventions
        3. **Latency Reduction** - Optimize queue processing and API performance
        
        **Recommended Actions:**
        - Immediate: Implement queue processing optimization (2-month timeline)
        - Short-term: Deploy enhanced fraud rules and routing optimization (3-4 months)
        - Long-term: Event-driven architecture transformation (12-18 months)
        """)
        
        # Key metrics summary chart
        st.markdown("### Metrics Summary")
        
        metrics_df = pd.DataFrame({
            "Metric": ["STP Rate", "Cost per Tx", "Fraud Loss", "Latency"],
            "Current": [82, 0.28, 0.12, 4.8],
            "Target": [95, 0.15, 0.05, 2.5],
            "Status": ["Red", "Red", "Amber", "Red"]
        })
        
        st.dataframe(metrics_df, use_container_width=True)
