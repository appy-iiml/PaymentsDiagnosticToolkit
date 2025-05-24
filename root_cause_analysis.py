import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import networkx as nx
import plotly.figure_factory as ff
import random
from business_data import load_process_details
from data_loader import get_stage_names, KPI_MATRIX

# Load upstream process dependencies from the provided data
UPSTREAM_DEPENDENCIES = {
    # Stage 1
    "1A": ["External trigger (user / API)"],
    "1B": ["1A"],
    "1C": ["1A"],
    "1D": ["1C"],
    # Stage 2
    "2A": ["1A", "1D"],
    "2B": ["2A"],
    "2C": ["1B", "2A"],
    "2D": ["2A", "2C"],
    # Stage 3
    "3A": ["1D"],
    "3B": ["1D", "2C", "3A"],
    "3C": ["1D", "3A"],
    "3D": ["3A", "3C"],
    # Stage 4
    "4A": ["1D", "3D"],  # 3D validation
    "4B": ["4A"],
    "4C": ["4B"],
    "4D": ["4C"],
    # Stage 5
    "5A": ["1D", "2D", "4D"],
    "5B": ["1D", "4D"],
    "5C": ["1D", "4D", "5A"],
    "5D": ["5A", "5C"],
    # Stage 6
    "6A": ["1D", "5D"],
    "6B": ["6A"],
    "6C": ["1D", "2C", "5D"],
    "6D": ["6A", "6B"],
    # Stage 7
    "7A": ["7A", "7C"],  # (This might be a typo in the data? 7A depends on itself?)
    "7B": ["1D", "6D"],
    "7C": ["7A", "7B"],  # (Potential circular dependency here)
    "7D": ["7B", "7C"],
    # Stage 8
    "8A": ["7D"],  # (7D validates message)
    "8B": ["8A"],
    "8C": ["4B", "7B", "8A"],
    "8D": ["8A", "8C"],
    # Stage 9
    "9A": ["8D"],
    "9B": ["8D", "9A"],
    "9C": ["4D", "8D", "9A"],
    "9D": ["9A", "9B"],
    # Stage 10
    "10A": ["6D", "8D", "9A", "9B"],
    "10B": ["9B", "10A"],
    "10C": ["3D", "5D", "7B", "8D", "9A", "9B", "10A"],
    "10D": ["1D", "10C"],
    # Stage 11
    "11A": ["Events from Stages 1-10"],  # Special case
    "11B": ["10B"],
    "11C": ["Aggregated Stage 1-10 data"],  # Special case
    "11D": ["Status events Stage 1-10"],   # Special case
    # Stage 12
    "12A": ["Logs from Stages 1-11"],      # Special case
    "12B": ["12A"],
    "12C": ["1D", "5B", "5C", "9A"],
    "12D": ["12A", "12B"]
}

# Map process IDs to their names for better readability
def get_process_names():
    process_data = load_process_details()
    process_names = {}
    for process in process_data:
        process_names[process['qid']] = process['process']
    return process_names

# Generate mock status data for processes
def generate_mock_status(process_ids, target_problem_areas=None):
    """
    Generate mock status data for processes
    
    Parameters:
    - process_ids: List of process IDs to generate status for
    - target_problem_areas: List of process IDs to mark as problematic
    
    Returns:
    - Dictionary mapping process IDs to status ('green', 'amber', 'red')
    """
    status_data = {}
    
    # Set default statuses
    for pid in process_ids:
        # Default to mostly green
        status_data[pid] = random.choices(
            ['green', 'amber', 'red'], 
            weights=[0.7, 0.2, 0.1], 
            k=1
        )[0]
    
    # Override with target problem areas if specified
    if target_problem_areas:
        for pid in target_problem_areas:
            if pid in process_ids:
                status_data[pid] = 'red'
                
                # Find upstream dependencies and mark some as amber/red
                for upstream_pid, deps in UPSTREAM_DEPENDENCIES.items():
                    if pid in deps and upstream_pid in process_ids:
                        # 50% chance to make upstream nodes amber
                        status_data[upstream_pid] = random.choices(
                            ['amber', 'red'], 
                            weights=[0.7, 0.3], 
                            k=1
                        )[0]
    
    return status_data

# Build a dependency graph for visualization
def build_dependency_graph(process_ids, status_data, reverse=False):
    """
    Build a dependency graph for visualization
    
    Parameters:
    - process_ids: List of process IDs to include in the graph
    - status_data: Dictionary mapping process IDs to status
    - reverse: If True, show upstream dependencies instead of downstream
    
    Returns:
    - NetworkX graph object
    """
    G = nx.DiGraph()
    
    # Add nodes with their status
    process_names = get_process_names()
    for pid in process_ids:
        if pid in process_names:
            # Add node with display name and status
            G.add_node(pid, name=f"{pid}: {process_names.get(pid, 'Unknown')}", status=status_data.get(pid, 'grey'))
        else:
            # Handle special cases like "External trigger" that might not be in process_names
            G.add_node(pid, name=pid, status=status_data.get(pid, 'grey'))
    
    # Add edges based on dependencies
    if reverse:
        # Add upstream dependencies (what affects this process)
        for pid in process_ids:
            if pid in UPSTREAM_DEPENDENCIES:
                for dep_pid in UPSTREAM_DEPENDENCIES[pid]:
                    if dep_pid in process_ids:
                        G.add_edge(dep_pid, pid)
    else:
        # Add downstream dependencies (what this process affects)
        for pid in process_ids:
            for target_pid, deps in UPSTREAM_DEPENDENCIES.items():
                if pid in deps and target_pid in process_ids:
                    G.add_edge(pid, target_pid)
    
    return G

# Convert NetworkX graph to Plotly figure
def network_graph_to_plotly(G, height=600):
    """
    Convert NetworkX graph to Plotly figure
    
    Parameters:
    - G: NetworkX graph object
    - height: Height of the figure
    
    Returns:
    - Plotly figure object
    """
    # Create positions for the nodes using a layout algorithm
    pos = nx.spring_layout(G, seed=42)
    
    # Create node traces
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(G.nodes[node]['name'])
        
        # Set color based on status
        status = G.nodes[node]['status']
        if status == 'red':
            node_color.append('red')
        elif status == 'amber':
            node_color.append('orange')
        elif status == 'green':
            node_color.append('green')
        else:
            node_color.append('grey')
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="top center",
        marker=dict(
            showscale=False,
            color=node_color,
            size=15,
            line=dict(width=2, color='black')
        )
    )
    
    # Create edge traces
    edge_x = []
    edge_y = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Create the figure
    fig = go.Figure(data=[edge_trace, node_trace],
                  layout=go.Layout(
                      showlegend=False,
                      hovermode='closest',
                      margin=dict(b=20, l=5, r=5, t=40),
                      xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                      yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                      height=height
                  ))
    
    return fig

# Find upstream root causes for problematic processes
def find_root_causes(problem_processes, depth=2):
    """
    Find potential root causes for problematic processes
    
    Parameters:
    - problem_processes: List of process IDs marked as problematic
    - depth: How many levels up to traverse
    
    Returns:
    - Dictionary mapping problem processes to their potential root causes
    """
    root_causes = {}
    
    for pid in problem_processes:
        causes = set()
        current_level = {pid}
        
        for _ in range(depth):
            next_level = set()
            for process in current_level:
                if process in UPSTREAM_DEPENDENCIES:
                    next_level.update(UPSTREAM_DEPENDENCIES[process])
            causes.update(next_level)
            current_level = next_level
        
        # Remove any special case dependencies that aren't real process IDs
        causes = {c for c in causes if len(c) <= 3 or c in UPSTREAM_DEPENDENCIES}
        
        root_causes[pid] = list(causes)
    
    return root_causes

# Map processes to KPIs for monitoring recommendations
def map_processes_to_kpis(processes):
    """
    Map processes to their related KPIs for monitoring
    
    Parameters:
    - processes: List of process IDs
    
    Returns:
    - Dictionary mapping process IDs to their KPIs
    """
    process_kpis = {}
    
    for pid in processes:
        if pid in KPI_MATRIX:
            process_kpis[pid] = KPI_MATRIX[pid]["kpi"]
    
    return process_kpis

# Create a timeline view of the payment process journey
def create_process_journey_figure(status_data):
    """
    Create a horizontal timeline view of the payment process journey
    
    Parameters:
    - status_data: Dictionary mapping process IDs to their status
    
    Returns:
    - Plotly figure object
    """
    # Group processes by stage
    stages = {}
    process_names = get_process_names()
    
    for pid in status_data:
        stage_id = int(pid[0]) if pid[0].isdigit() else 0
        if stage_id not in stages:
            stages[stage_id] = []
        
        # Get process name and status
        name = process_names.get(pid, pid)
        status = status_data.get(pid, 'grey')
        
        stages[stage_id].append({
            'id': pid,
            'name': name,
            'status': status
        })
    
    # Sort stages
    sorted_stages = sorted(stages.items())
    
    # Create the figure
    fig = go.Figure()
    
    # Add each stage as a group of nodes
    y_pos = 0
    annotations = []
    stage_names = get_stage_names()
    
    for stage_id, processes in sorted_stages:
        if stage_id == 0:  # Skip special cases
            continue
            
        # Get stage name
        stage_name = stage_names.get(stage_id, f"Stage {stage_id}")
        
        # Create text annotation for stage
        annotations.append(
            dict(
                x=0,
                y=y_pos,
                xref="paper",
                yref="y",
                text=f"<b>Stage {stage_id}:</b><br>{stage_name}",
                showarrow=False,
                font=dict(color="black"),
                align="right",
                xanchor="right",
                yanchor="middle"
            )
        )
        
        # Add processes for this stage
        for i, process in enumerate(processes):
            marker_color = {'red': 'red', 'amber': 'orange', 'green': 'green'}.get(process['status'], 'grey')
            
            fig.add_trace(go.Scatter(
                x=[stage_id + (i * 0.2)],  # Position within stage
                y=[y_pos],
                mode="markers+text",
                marker=dict(size=15, color=marker_color, line=dict(width=1, color="black")),
                text=process['id'],
                textposition="top center",
                hovertext=f"{process['id']}: {process['name']} (Status: {process['status']})",
                hoverinfo="text",
                showlegend=False,
                name=process['id']
            ))
        
        # Next row
        y_pos -= 1
    
    # Add process flow arrows between stages
    for stage_id in range(1, max(stages.keys())):
        fig.add_shape(
            type="line",
            x0=stage_id + 0.5,
            y0=-(stage_id - 1),
            x1=stage_id + 0.5,
            y1=-(stage_id),
            line=dict(color="grey", width=2, dash="dot"),
        )
    
    # Configure layout
    fig.update_layout(
        title="Payment Process Journey",
        height=len(sorted_stages) * 100,
        margin=dict(l=200, r=20, t=50, b=20),
        xaxis=dict(
            range=[0, 13],
            showgrid=False, 
            zeroline=False, 
            showticklabels=False
        ),
        yaxis=dict(
            range=[-(len(sorted_stages) - 1) - 0.5, 0.5],
            showgrid=False, 
            zeroline=False, 
            showticklabels=False
        ),
        annotations=annotations,
        plot_bgcolor="white"
    )
    
    return fig

def get_immediate_upstream_dependencies(process_id):
    """Get only the immediate upstream dependencies for a given process ID"""
    if process_id in UPSTREAM_DEPENDENCIES:
        return UPSTREAM_DEPENDENCIES[process_id]
    return []

def render_root_cause_analysis():
    """Main function to render the root cause analysis interface"""
    st.header("Root Cause Analysis")
    st.write("Analyze payment process dependencies and identify root causes of issues")
    
    # Initialize session state for RCA
    if 'rca_scenario' not in st.session_state:
        st.session_state.rca_scenario = "Custom Scenario"
    if 'problem_processes' not in st.session_state:
        st.session_state.problem_processes = []
    if 'status_data' not in st.session_state:
        st.session_state.status_data = {}
    
    # Scenario selection
    st.subheader("Analysis Scenario")
    
    scenarios = [
        "Custom Scenario",
        "High Transaction Rejection Rate",
        "Fraud Detection False Positives",
        "Settlement Delays",
        "Compliance Alert Backlog"
    ]
    
    selected_scenario = st.selectbox(
        "Select analysis scenario:",
        options=scenarios,
        index=scenarios.index(st.session_state.rca_scenario)
    )
    
    st.session_state.rca_scenario = selected_scenario
    
    # Get all process IDs
    process_data = load_process_details()
    all_process_ids = [p['qid'] for p in process_data]
    
    # Scenario-specific problem areas
    scenario_problems = {
        "High Transaction Rejection Rate": ["3A", "3B", "4A", "7A"],
        "Fraud Detection False Positives": ["2C", "3C", "5A", "5C"],
        "Settlement Delays": ["8A", "8B", "9A", "9B"],
        "Compliance Alert Backlog": ["5B", "5C", "12A", "12C"]
    }
    
    # Set problem processes based on scenario
    if selected_scenario in scenario_problems:
        st.session_state.problem_processes = scenario_problems[selected_scenario]
        # Generate status data with these problem areas
        st.session_state.status_data = generate_mock_status(
            all_process_ids, 
            st.session_state.problem_processes
        )
    else:
        # Custom scenario - let user select problem processes
        st.session_state.problem_processes = st.multiselect(
            "Select problematic processes:",
            options=all_process_ids,
            default=st.session_state.problem_processes,
            format_func=lambda x: f"{x}: {get_process_names().get(x, 'Unknown')}"
        )
        
        # Generate status data
        st.session_state.status_data = generate_mock_status(
            all_process_ids, 
            st.session_state.problem_processes
        )
    
    if not st.session_state.problem_processes:
        st.warning("Please select at least one problematic process to analyze")
        return
    
    # Create tabs for different analysis views
    tab1, tab2, tab3, tab4 = st.tabs([
        "Process Journey View",
        "Dependency Analysis",
        "Root Cause Investigation",
        "Monitoring Recommendations"
    ])
    
    with tab1:
        st.subheader("Payment Process Journey")
        st.write("Overview of all processes with current status")
        
        # Create process journey visualization
        journey_fig = create_process_journey_figure(st.session_state.status_data)
        st.plotly_chart(journey_fig, use_container_width=True)
        
        # Status legend
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("🟢 **Green:** Normal operation")
        with col2:
            st.markdown("🟠 **Amber:** Warning/degraded")
        with col3:
            st.markdown("🔴 **Red:** Critical issue")
    
    with tab2:
        st.subheader("Process Dependency Analysis")
        
        # Focus process selection
        focus_process = st.selectbox(
            "Select process to analyze dependencies:",
            options=st.session_state.problem_processes,
            format_func=lambda x: f"{x}: {get_process_names().get(x, 'Unknown')}"
        )
        
        if focus_process:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Upstream Dependencies")
                st.write("Processes that affect this process:")
                
                upstream_deps = get_immediate_upstream_dependencies(focus_process)
                for dep in upstream_deps:
                    if dep in st.session_state.status_data:
                        status = st.session_state.status_data[dep]
                        status_emoji = {"green": "🟢", "amber": "🟠", "red": "🔴"}.get(status, "⚪")
                        process_name = get_process_names().get(dep, dep)
                        st.write(f"{status_emoji} {dep}: {process_name}")
                    else:
                        st.write(f"⚪ {dep}")
            
            with col2:
                st.markdown("#### Downstream Impact")
                st.write("Processes affected by this process:")
                
                downstream_processes = []
                for target_pid, deps in UPSTREAM_DEPENDENCIES.items():
                    if focus_process in deps:
                        downstream_processes.append(target_pid)
                
                for target in downstream_processes:
                    if target in st.session_state.status_data:
                        status = st.session_state.status_data[target]
                        status_emoji = {"green": "🟢", "amber": "🟠", "red": "🔴"}.get(status, "⚪")
                        process_name = get_process_names().get(target, target)
                        st.write(f"{status_emoji} {target}: {process_name}")
            
            # Create dependency graph visualization
            st.markdown("#### Dependency Graph")
            
            # Get relevant processes for visualization (focus + dependencies)
            relevant_processes = set([focus_process])
            relevant_processes.update(upstream_deps)
            relevant_processes.update(downstream_processes)
            
            # Filter out special case dependencies
            relevant_processes = {p for p in relevant_processes if len(p) <= 3}
            
            if len(relevant_processes) > 1:
                G = build_dependency_graph(
                    list(relevant_processes), 
                    st.session_state.status_data
                )
                
                if G.number_of_nodes() > 0:
                    graph_fig = network_graph_to_plotly(G, height=400)
                    st.plotly_chart(graph_fig, use_container_width=True)
    
    with tab3:
        st.subheader("Root Cause Investigation")
        
        # Find root causes for all problem processes
        root_causes = find_root_causes(st.session_state.problem_processes, depth=3)
        
        for problem_process in st.session_state.problem_processes:
            with st.expander(f"Root Cause Analysis: {problem_process} - {get_process_names().get(problem_process, 'Unknown')}"):
                causes = root_causes.get(problem_process, [])
                
                if causes:
                    st.write("**Potential root causes (up to 3 levels upstream):**")
                    
                    for cause in causes:
                        if cause in st.session_state.status_data:
                            status = st.session_state.status_data[cause]
                            status_emoji = {"green": "🟢", "amber": "🟠", "red": "🔴"}.get(status, "⚪")
                            process_name = get_process_names().get(cause, cause)
                            
                            # Highlight problematic upstream processes
                            if status in ['red', 'amber']:
                                st.error(f"{status_emoji} **{cause}: {process_name}** - Requires investigation")
                            else:
                                st.write(f"{status_emoji} {cause}: {process_name}")
                        else:
                            st.write(f"⚪ {cause}")
                    
                    # Analysis recommendations
                    st.markdown("**Recommended Actions:**")
                    problematic_causes = [c for c in causes if st.session_state.status_data.get(c) in ['red', 'amber']]
                    
                    if problematic_causes:
                        st.write("1. **Immediate:** Investigate the highlighted upstream processes")
                        st.write("2. **Short-term:** Implement monitoring for these dependency chains")
                        st.write("3. **Long-term:** Consider process redesign to reduce dependencies")
                    else:
                        st.write("1. **Check:** All upstream processes appear healthy - investigate local issues")
                        st.write("2. **Monitor:** Set up alerts for this process and immediate dependencies")
                else:
                    st.write("No upstream dependencies found - this may be a root cause itself")
    
    with tab4:
        st.subheader("Monitoring Recommendations")
        
        # Map problem processes to KPIs
        process_kpis = map_processes_to_kpis(st.session_state.problem_processes)
        
        st.markdown("#### Key Performance Indicators to Monitor")
        
        kpi_df_data = []
        for process_id, kpi in process_kpis.items():
            process_name = get_process_names().get(process_id, 'Unknown')
            status = st.session_state.status_data.get(process_id, 'unknown')
            
            kpi_df_data.append({
                "Process ID": process_id,
                "Process Name": process_name,
                "Key KPI": kpi,
                "Current Status": status.title(),
                "Priority": "High" if status == 'red' else ("Medium" if status == 'amber' else "Low")
            })
        
        if kpi_df_data:
            kpi_df = pd.DataFrame(kpi_df_data)
            st.dataframe(kpi_df, use_container_width=True)
        
        # Monitoring recommendations by scenario
        st.markdown("#### Scenario-Specific Monitoring Strategy")
        
        monitoring_strategies = {
            "High Transaction Rejection Rate": {
                "immediate": [
                    "Set up real-time alerts for rejection rate spikes (>10% increase)",
                    "Monitor pre-processing validation failures",
                    "Track business rules engine performance"
                ],
                "ongoing": [
                    "Daily rejection rate trending analysis",
                    "Weekly root cause categorization",
                    "Monthly business rules effectiveness review"
                ]
            },
            "Fraud Detection False Positives": {
                "immediate": [
                    "Monitor false positive rate in real-time",
                    "Set up alerts for ML model performance degradation",
                    "Track manual review queue length"
                ],
                "ongoing": [
                    "Weekly model performance analysis",
                    "Monthly false positive rate trending",
                    "Quarterly model retraining assessment"
                ]
            },
            "Settlement Delays": {
                "immediate": [
                    "Monitor clearing network response times",
                    "Set up alerts for settlement SLA breaches",
                    "Track liquidity buffer utilization"
                ],
                "ongoing": [
                    "Daily settlement performance dashboard",
                    "Weekly liquidity management analysis",
                    "Monthly network performance review"
                ]
            },
            "Compliance Alert Backlog": {
                "immediate": [
                    "Monitor alert queue length and age",
                    "Set up SLA breach notifications",
                    "Track investigator workload distribution"
                ],
                "ongoing": [
                    "Daily compliance dashboard",
                    "Weekly productivity analysis",
                    "Monthly regulatory reporting preparation"
                ]
            }
        }
        
        if selected_scenario in monitoring_strategies:
            strategy = monitoring_strategies[selected_scenario]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Immediate Actions (24-48 hours):**")
                for action in strategy["immediate"]:
                    st.write(f"• {action}")
            
            with col2:
                st.markdown("**Ongoing Monitoring:**")
                for action in strategy["ongoing"]:
                    st.write(f"• {action}")
        
        # Export recommendations
        st.markdown("#### Export Analysis")
        
        if st.button("Generate RCA Report"):
            report_data = {
                "scenario": selected_scenario,
                "problem_processes": st.session_state.problem_processes,
                "root_causes": root_causes,
                "kpis_to_monitor": list(process_kpis.values()),
                "recommendation_summary": f"Focus on {len(set(sum(root_causes.values(), [])))} upstream processes"
            }
            
            st.json(report_data)
            st.success("RCA report generated! Copy the JSON data above for documentation.")
