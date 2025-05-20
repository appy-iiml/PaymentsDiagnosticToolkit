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
            <h3>Latency</h3>
            <div class='metric-value'>{KEY_METRICS["Latency"]["current"]:.1f} sec</div>
            <div class='metric-target'>Target: {KEY_METRICS["Latency"]["target"]:.1f} sec</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add a brief explanation
    st.markdown("""
    <div class='dashboard-info'>
        <p><span class='green-dot'></span> <strong>Green:</strong> On target or within 10% of goal</p>
        <p><span class='amber-dot'></span> <strong>Amber:</strong> Within 30% of target - needs attention</p>
        <p><span class='red-dot'></span> <strong>Red:</strong> Significantly off target - critical action needed</p>
    </div>
    """, unsafe_allow_html=True)

def render_improvement_wizard():
    """Render the three-click improvement wizard"""
    st.header("Payment Improvement Wizard")
    st.markdown("<p class='subtitle'>Identify gaps and prioritize improvements in just three clicks</p>", unsafe_allow_html=True)
    
    # Step 1: Select Payment Stream
    selected_stream = st.selectbox(
        "Step 1: Select Payment Stream", 
        PAYMENT_STREAMS,
        help="Choose the specific payment flow you want to analyze"
    )
    
    # Step 2: Select Business Goal
    selected_goal = st.selectbox(
        "Step 2: Select Business Goal",
        BUSINESS_GOALS,
        help="What business outcome are you trying to achieve?"
    )
    
    # Step 3: Enter KPIs
    st.markdown("### Step 3: Enter Today's KPIs")
    
    # Determine which KPIs to show based on selected goal
    if selected_goal in GOAL_PROCESS_MAP:
        # Get relevant KPIs for this goal
        relevant_kpis = GOAL_PROCESS_MAP[selected_goal]["representative_kpis"]
        key_metric = GOAL_PROCESS_MAP[selected_goal]["key_metric"]
        current_value = KEY_METRICS[key_metric]["current"]
        target_value = KEY_METRICS[key_metric]["target"]
        
        # Show primary KPI linked to the goal with a visual status
        st.markdown(f"#### Primary KPI: {KEY_METRICS[key_metric]['representative_kpi']}")
        
        # Primary KPI input 
        col1, col2 = st.columns(2)
        
        with col1:
            if key_metric in ["STP Rate", "Fraud Loss"]:
                # Use percentage input for these metrics
                new_value = st.number_input(
                    f"Current {key_metric} (%)", 
                    min_value=0.0, 
                    max_value=100.0, 
                    value=current_value*100,
                    step=0.1,
                    format="%.1f"
                ) / 100.0
            elif key_metric == "Cost per Transaction":
                # Use dollar input
                new_value = st.number_input(
                    f"Current {key_metric} ($)", 
                    min_value=0.01, 
                    max_value=10.0, 
                    value=current_value,
                    step=0.01,
                    format="%.2f"
                )
            else:  # Latency
                # Use seconds or ms input based on KPI
                new_value = st.number_input(
                    f"Current {key_metric} (seconds)", 
                    min_value=0.1, 
                    max_value=60.0, 
                    value=current_value,
                    step=0.1,
                    format="%.1f"
                )
        
        with col2:
            # Calculate the gap
            if key_metric in ["STP Rate"]:
                # For STP, higher is better
                gap = target_value - new_value
                gap_percentage = abs(gap / target_value * 100)
                direction = "below" if gap > 0 else "above"
            else:
                # For Cost, Fraud, Latency, lower is better
                gap = new_value - target_value
                gap_percentage = abs(gap / target_value * 100)
                direction = "above" if gap > 0 else "below"
            
            # Display gap info with color coding
            if abs(gap_percentage) <= 10:
                st.success(f"**Current performance is within 10% of target**")
            elif abs(gap_percentage) <= 30:
                st.warning(f"**Performance gap: {gap_percentage:.1f}% {direction} target**")
            else:
                st.error(f"**Critical gap: {gap_percentage:.1f}% {direction} target**")
            
            # Show business outcome indicators
            st.markdown("**Business Impact Indicators:**")
            for indicator in GOAL_PROCESS_MAP[selected_goal]["bo_indicators"]:
                st.markdown(f"- {indicator}")
        
        # Show secondary KPIs (optional)
        with st.expander("Additional Related KPIs"):
            st.markdown("Select other KPIs to include in the analysis:")
            
            # Show checkboxes for secondary KPIs
            selected_secondary_kpis = []
            for kpi in relevant_kpis[:3]:  # Limit to first 3 to keep it simple
                if st.checkbox(kpi, value=True):
                    selected_secondary_kpis.append(kpi)
    
    # Display generate button
    if st.button("Generate Improvement Plan", type="primary"):
        st.session_state.show_results = True
    
    # Show results if button was clicked
    if st.session_state.get('show_results', False):
        display_improvement_results(selected_stream, selected_goal)

def display_improvement_results(stream, goal):
    """Display the improvement results for the selected stream and goal"""
    st.markdown("---")
    st.subheader(f"Improvement Plan: {stream} - {goal}")
    
    # Get the relevant processes for the selected goal
    if goal in GOAL_PROCESS_MAP:
        # Get relevant data
        relevant_processes = GOAL_PROCESS_MAP[goal]["processes"]
        relevant_kpis = GOAL_PROCESS_MAP[goal]["representative_kpis"]
        bo_indicators = GOAL_PROCESS_MAP[goal]["bo_indicators"]
        key_metric = GOAL_PROCESS_MAP[goal]["key_metric"]
        
        # Create tabs for the results
        tabs = st.tabs(["Business Impact", "Recommended Actions", "Benchmark Comparison"])
        
        with tabs[0]:
            st.markdown(f"### {goal} Impact Analysis")
            
            # Show KPI impacts in a clear visual summary
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Create a "Business Scorecard" showing the KPIs and their status
                st.markdown("#### Business Outcome Scorecard")
                
                # Create explanatory text
                st.markdown(f"""
                Focusing on **{goal}** will drive improvements in these business indicators:
                """)
                
                # Display business indicators with graphical elements
                for indicator in bo_indicators:
                    st.markdown(f"""
                    <div style="background-color: rgba(102, 51, 153, 0.1); padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 4px solid #663399;">
                        <strong>{indicator}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Show top KPIs related to this business outcome
                st.markdown("#### Key Performance Indicators")
                
                for kpi in relevant_kpis[:5]:  # Show top 5 KPIs
                    # Assign random status for demo purposes
                    import random
                    status = random.choice(["red", "amber", "green"])
                    
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <span class="{status}-dot"></span>
                        <span style="margin-left: 10px;">{kpi}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                # Show a metric summary of the key metric for this business outcome
                st.metric(
                    label=f"Current {key_metric}",
                    value=f"{KEY_METRICS[key_metric]['current']:.2f}" if key_metric == "Cost per Transaction" else 
                          f"{KEY_METRICS[key_metric]['current']*100:.1f}%" if key_metric in ["STP Rate", "Fraud Loss"] else
                          f"{KEY_METRICS[key_metric]['current']:.1f}s",
                    delta="Gap from Target: " + (
                        f"{(KEY_METRICS[key_metric]['target'] - KEY_METRICS[key_metric]['current'])*100:.1f}%" 
                        if key_metric in ["STP Rate"] else
                        f"{(KEY_METRICS[key_metric]['current'] - KEY_METRICS[key_metric]['target']):.2f}" 
                        if key_metric == "Cost per Transaction" else
                        f"{(KEY_METRICS[key_metric]['current'] - KEY_METRICS[key_metric]['target'])*100:.1f}%" 
                        if key_metric == "Fraud Loss" else
                        f"{(KEY_METRICS[key_metric]['current'] - KEY_METRICS[key_metric]['target']):.1f}s"
                    ),
                )
            
            # Display detailed KPI analysis
            st.markdown("### Process Capability Gap Analysis")
            
            # Create a process assessment table showing gaps
            process_data = load_process_details()
            relevant_process_data = [p for p in process_data if p['qid'] in relevant_processes]
            
            # Create process capability visualization for key processes
            details_data = []
            for i, process in enumerate(relevant_process_data[:6]):  # Show top 6 most critical processes
                current_level = "Advanced"  # For demo purposes
                current_score = 0.33  # For demo purposes
                gap_score = 0.33  # Gap to Leading level for demo
                impact = "High" if i < 3 else "Medium"
                
                details_data.append({
                    "ID": process['qid'],
                    "Process": process['process'],
                    "Current Level": current_level,
                    "Gap to Target": gap_score,
                    "Impact on Goal": impact
                })
            
            details_df = pd.DataFrame(details_data)
            st.dataframe(details_df, use_container_width=True)
            
            # Create KPI to Process Mapping
            st.markdown("#### KPI to Process Mapping")
            st.markdown("The following processes are critical for improving these KPIs:")
            
            # KPI data table
            kpi_data = []
            for pid in relevant_processes[:8]:  # Limit to top 8
                if pid in KPI_MATRIX:
                    kpi_data.append({
                        "Process ID": pid,
                        "KPI": KPI_MATRIX[pid]["kpi"],
                        "Business Outcome": KEY_METRICS[key_metric]["business_outcome"] 
                            if key_metric in KEY_METRICS else "Unknown"
                    })
            
            kpi_df = pd.DataFrame(kpi_data)
            st.dataframe(kpi_df, use_container_width=True)
        
        with tabs[1]:
            st.markdown("### Recommended Actions")
            
            # Create a visual roadmap at the top
            st.markdown("#### Improvement Roadmap")
            
            # Simple timeline visualization
            timeline_cols = st.columns([2, 3, 2])
            with timeline_cols[0]:
                st.markdown("""
                <div style="text-align:center; border-bottom: 3px solid #663399; padding-bottom: 10px;">
                    <h5>Quick Wins</h5>
                    <p>1-3 months</p>
                </div>
                """, unsafe_allow_html=True)
            
            with timeline_cols[1]:
                st.markdown("""
                <div style="text-align:center; border-bottom: 3px solid #9370DB; padding-bottom: 10px;">
                    <h5>Medium-Term Initiatives</h5>
                    <p>3-9 months</p>
                </div>
                """, unsafe_allow_html=True)
            
            with timeline_cols[2]:
                st.markdown("""
                <div style="text-align:center; border-bottom: 3px solid #B19CD9; padding-bottom: 10px;">
                    <h5>Strategic Investments</h5>
                    <p>9-18 months</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("")  # Spacer
            
            # Quick Wins
            st.subheader("Quick Wins (1-3 months)")
            quick_wins = IMPROVEMENT_RECOMMENDATIONS[goal]["quick_wins"]
            
            for i, win in enumerate(quick_wins):
                with st.expander(f"{win['title']} - Impact: {win['impact']}"):
                    st.markdown(f"""
                    **Effort Required:** {win['effort']}  
                    **Implementation Timeline:** {win['timeframe']}  
                    **KPI Impact:** {win['kpi_impact']}
                    """)
                    
                    # Add specific process recommendations
                    st.markdown("**Related Processes:**")
                    for pid in relevant_processes[:3]:  # Just show a few for demo
                        process_name = next((p['process'] for p in relevant_process_data if p['qid'] == pid), "Unknown Process")
                        st.markdown(f"- {pid}: {process_name}")
            
            # Strategic Investments
            st.subheader("Strategic Investments (9-18 months)")
            strategic = IMPROVEMENT_RECOMMENDATIONS[goal]["strategic_investments"]
            
            for i, investment in enumerate(strategic):
                with st.expander(f"{investment['title']} - Impact: {investment['impact']}"):
                    st.markdown(f"""
                    **Effort Required:** {investment['effort']}  
                    **Implementation Timeline:** {investment['timeframe']}  
                    **KPI Impact:** {investment['kpi_impact']}
                    """)
                    
                    # Add capability description
                    st.markdown("**Capability Enhancement:**")
                    st.markdown("This strategic initiative will transform your payment capabilities in the following ways:")
                    
                    capabilities = []
                    # Select 3 random processes for the demo
                    import random
                    sample_processes = random.sample(relevant_process_data, min(3, len(relevant_process_data)))
                    
                    for p in sample_processes:
                        capabilities.append(f"- Transform {p['process']} from {p.get('advanced', 'Current')} to {p.get('emerging', 'Target')}")
                    
                    for cap in capabilities:
                        st.markdown(cap)
        
        with tabs[2]:
            st.markdown("### Benchmark Comparison")
            
            # Create benchmark data for comparison
            # Using existing data from the system
            from data_loader import load_data
            banks_data, _ = load_data()
            
            # Add current bank data
            current_bank_data = {
                "Your Bank": {
                    1: 2.0, 2: 2.0, 3: 1.5, 4: 1.5, 5: 2.0, 6: 1.5, 
                    7: 1.5, 8: 2.0, 9: 2.0, 10: 1.5, 11: 1.5, 12: 1.0,
                    "Overall": 1.67
                }
            }
            
            # Combine data
            combined_data = {**current_bank_data, **banks_data}
            
            # Select top banks for comparison
            top_banks = ["JPMC (Global)", "DBS (Asia)"] 
            comparison_banks = ["Your Bank"] + top_banks
            
            # Create radar chart
            fig = create_radar_chart(
                combined_data,
                comparison_banks,
                f"Industry Comparison: {goal}"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed gap analysis
            st.markdown("### Gap Analysis by Process Stage")
            
            # Create a bar chart for specific stages related to the selected goal
            # This is a simplification - in a real app, would need to map goals to stages
            relevant_stages = [1, 2, 3, 4] if goal == "Customer Satisfaction" else \
                              [3, 4, 7, 8] if goal == "Speed-to-Market" else \
                              [2, 3, 5, 12] if goal == "Risk Management" else \
                              [3, 7, 10] if goal == "Cost Reduction" else [1, 4, 11]
            
            stage_names = get_stage_names()
            stage_data = []
            
            for stage_id in relevant_stages:
                stage_data.append({
                    "Stage": f"{stage_id}. {stage_names[stage_id]}",
                    "Your Bank": current_bank_data["Your Bank"].get(stage_id, 0),
                    top_banks[0]: combined_data[top_banks[0]].get(stage_id, 0),
                    "Gap": combined_data[top_banks[0]].get(stage_id, 0) - current_bank_data["Your Bank"].get(stage_id, 0)
                })
            
            stage_df = pd.DataFrame(stage_data)
            st.dataframe(stage_df, use_container_width=True)
            
            # Show investment summary and ROI
            st.markdown("### Investment Summary")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Quick Wins Cost", "$150K-$250K")
            
            with col2:
                st.metric("Strategic Investment", "$1.2M-$1.8M")
            
            with col3:
                st.metric("Expected ROI", "2.5-3.5x")

def render_dashboard_tab():
    """Main function to render the dashboard view"""
    
    # Add custom CSS for dashboard metrics
    st.markdown("""
    <style>
    .metric-tile {
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        text-align: center;
    }
    .green {
        background-color: rgba(0, 128, 0, 0.1);
        border-left: 5px solid green;
    }
    .amber {
        background-color: rgba(255, 165, 0, 0.1);
        border-left: 5px solid orange;
    }
    .red {
        background-color: rgba(255, 0, 0, 0.1);
        border-left: 5px solid red;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-target {
        font-size: 14px;
        color: #666;
    }
    .subtitle {
        color: #666;
        font-size: 1.1em;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    .dashboard-info {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        margin: 20px 0;
    }
    .green-dot, .amber-dot, .red-dot {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 5px;
    }
    .green-dot {
        background-color: green;
    }
    .amber-dot {
        background-color: orange;
    }
    .red-dot {
        background-color: red;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Add tabs for the two floors of the control tower
    tower_level = st.radio(
        "Control Tower Level",
        ["Live Dashboard (Upper Level)", "Improvement Wizard (Lower Level)"],
        horizontal=True
    )
    
    if tower_level == "Live Dashboard (Upper Level)":
        render_control_tower_metrics()
    else:
        render_improvement_wizard()