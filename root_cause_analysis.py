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

def trace_upstream_path(start_process, depth=1):
    """
    Trace upstream path for a specific process to a certain depth
    Returns only the processes in the path to keep the analysis focused
    """
    if depth <= 0:
        return []
    
    # Start with immediate upstream dependencies
    upstream_processes = get_immediate_upstream_dependencies(start_process)
    
    # If we need to go deeper, recurse for each upstream process
    if depth > 1:
        next_level = []
        for process in upstream_processes:
            next_level.extend(trace_upstream_path(process, depth - 1))
        upstream_processes.extend(next_level)
    
    # Remove any special case dependencies that aren't real process IDs
    upstream_processes = [p for p in upstream_processes if len(p) <= 3 or p in UPSTREAM_DEPENDENCIES]
    
    # Add the start process to the path
    return list(set(upstream_processes + [start_process]))

def generate_focused_status_data(process_ids, target_process=None):
    """
    Generate status data focused only on the upstream path of a target process
    Other processes will be shown as grey to de-emphasize them
    
    Parameters:
    - process_ids: All process IDs in the system
    - target_process: The specific process to trace upstream
    
    Returns:
    - Dictionary mapping process IDs to status ('green', 'amber', 'red', 'grey')
    """
    # Set all processes to grey by default
    status_data = {pid: 'grey' for pid in process_ids}
    
    if target_process:
        # Get the upstream path for the target process
        path_processes = trace_upstream_path(target_process, depth=2)
        
        # Start by setting the target process to red
        status_data[target_process] = 'red'
        
        # For upstream processes, randomly assign statuses with a bias toward amber/red
        for pid in path_processes:
            if pid != target_process:  # Skip the target process as we already set it
                # For upstream processes, we want more amber/red since they might be contributing factors
                status_data[pid] = random.choices(
                    ['green', 'amber', 'red'], 
                    weights=[0.3, 0.4, 0.3],  # More likely to be amber/red
                    k=1
                )[0]
    
    return status_data

def render_root_cause_analysis():
    """Main function to render the root cause analysis dashboard"""
    st.header("Payment Process Root Cause Analysis")
    
    # Get all process data
    process_data = load_process_details()
    process_ids = [p['qid'] for p in process_data]
    process_names = get_process_names()
    
    # Create tabs for two different modes
    mode_tabs = st.tabs(["Initial Analysis", "Root Cause Tracing"])
    
    with mode_tabs[0]:
        st.markdown("<p class='subtitle'>Initial analysis to identify which KPIs to monitor based on problem areas</p>", unsafe_allow_html=True)
        
        # Sidebar for selecting problem areas in Initial Analysis mode
        st.sidebar.subheader("Problem Area Selection")
        
        # Group processes by stage for easier selection
        stage_names = get_stage_names()
        processes_by_stage = {}
        
        for process in process_data:
            stage_id = int(process['qid'][0])
            if stage_id not in processes_by_stage:
                processes_by_stage[stage_id] = []
            processes_by_stage[stage_id].append(process)
        
        # Use checkboxes to choose problem processes
        problem_processes = []
        
        # Expand sections by stage
        for stage_id in sorted(processes_by_stage.keys()):
            with st.sidebar.expander(f"Stage {stage_id}: {stage_names[stage_id]}"):
                for process in processes_by_stage[stage_id]:
                    if st.checkbox(f"{process['qid']}: {process['process']}", key=f"process_{process['qid']}"):
                        problem_processes.append(process['qid'])
        
        # Main analysis area for Initial Analysis
        if problem_processes:
            st.success(f"Analyzing {len(problem_processes)} selected problem areas")
            
            # Show KPI monitoring recommendations
            st.subheader("Recommended KPIs to Monitor")
            st.markdown("Based on the identified problem areas, these are the key performance indicators you should monitor.")
            
            # Map processes to KPIs - only for the directly selected problems
            process_kpis = map_processes_to_kpis(problem_processes)
            
            if process_kpis:
                # Create dataframe for display
                kpi_data = []
                
                for pid, kpi in process_kpis.items():
                    process_name = next((p['process'] for p in process_data if p['qid'] == pid), "Unknown")
                    
                    kpi_data.append({
                        "Process ID": pid,
                        "Process": process_name,
                        "KPI to Monitor": kpi,
                        "Priority": "High"  # All directly selected processes are high priority
                    })
                
                kpi_df = pd.DataFrame(kpi_data)
                st.dataframe(kpi_df, use_container_width=True)
                
                # Show upstream dependencies for each problem process
                for pid in problem_processes:
                    process_name = next((p['process'] for p in process_data if p['qid'] == pid), "Unknown")
                    
                    with st.expander(f"Upstream dependencies for {pid}: {process_name}"):
                        upstream_deps = get_immediate_upstream_dependencies(pid)
                        
                        if upstream_deps:
                            st.markdown("#### Immediate Upstream Processes:")
                            
                            upstream_data = []
                            for dep_pid in upstream_deps:
                                # Get name - handle special cases
                                if dep_pid in process_names:
                                    dep_name = process_names[dep_pid]
                                else:
                                    dep_name = dep_pid  # For special cases like "External trigger"
                                
                                # Get KPI if available
                                kpi = map_processes_to_kpis([dep_pid]).get(dep_pid, "N/A")
                                
                                upstream_data.append({
                                    "Process ID": dep_pid,
                                    "Process Name": dep_name,
                                    "KPI to Monitor": kpi
                                })
                            
                            upstream_df = pd.DataFrame(upstream_data)
                            st.dataframe(upstream_df, use_container_width=True)
                            
                            # Option to explore this process in Root Cause Tracing mode
                            if st.button(f"Trace Root Cause for {pid}", key=f"trace_{pid}"):
                                # Store in session state to switch to Root Cause Tracing mode with this process
                                st.session_state.trace_process = pid
                                st.session_state.active_tab = "Root Cause Tracing"
                                st.rerun()
                        else:
                            st.info("No upstream dependencies found. This appears to be a root cause itself.")
            else:
                st.warning("No relevant KPIs found for the selected processes")
        else:
            st.info("Please select one or more problem areas from the sidebar to begin analysis")
    
    with mode_tabs[1]:
        st.markdown("<p class='subtitle'>Trace upstream dependencies to find the root cause of a specific issue</p>", unsafe_allow_html=True)
        
        # If coming from Initial Analysis, use the process from session state
        if 'trace_process' in st.session_state and 'active_tab' in st.session_state and st.session_state.active_tab == "Root Cause Tracing":
            default_process = st.session_state.trace_process
            # Clear the session state so we don't keep redirecting
            st.session_state.active_tab = None
        else:
            default_process = None
        
        # Select a specific process to trace
        st.subheader("Select a Process to Trace")
        
        # First select a stage
        stage_options = [f"Stage {i}: {stage_names[i]}" for i in range(1, 13)]
        selected_stage_option = st.selectbox("Select a stage", stage_options)
        selected_stage_id = int(selected_stage_option.split(":")[0].replace("Stage ", ""))
        
        # Then select a process from that stage
        stage_processes = [p for p in process_data if int(p['qid'][0]) == selected_stage_id]
        process_options = [f"{p['qid']}: {p['process']}" for p in stage_processes]
        
        # Find the index of the default process if it exists
        default_index = 0
        if default_process:
            for i, option in enumerate(process_options):
                if option.startswith(default_process):
                    default_index = i
                    break
        
        selected_process_option = st.selectbox("Select a process", process_options, index=default_index)
        selected_process_id = selected_process_option.split(":")[0].strip()
        
        # Options for trace depth
        trace_depth = st.slider("Trace Depth", min_value=1, max_value=5, value=2, 
                               help="How many levels upstream to trace. Higher values show more distant dependencies.")
        
        if st.button("Trace Root Cause", type="primary"):
            # Generate focused status data
            focused_status = generate_focused_status_data(process_ids, selected_process_id)
            
            # Create tabs for different views of the trace
            result_tabs = st.tabs(["Dependency Map", "Path Analysis", "KPI Monitoring"])
            
            with result_tabs[0]:
                st.subheader("Upstream Dependency Map")
                st.markdown(f"This visualization shows the upstream dependencies that could be causing issues with **{selected_process_id}**. Red nodes indicate the problem area, and amber nodes show potential contributing factors.")
                
                # Get upstream path with the selected depth
                path_processes = trace_upstream_path(selected_process_id, depth=trace_depth)
                
                # Build graph showing only the upstream path
                focused_graph = build_dependency_graph(
                    path_processes,
                    focused_status,
                    reverse=True  # Upstream dependencies
                )
                
                graph_fig = network_graph_to_plotly(focused_graph, height=600)
                st.plotly_chart(graph_fig, use_container_width=True)
            
            with result_tabs[1]:
                st.subheader("Path Analysis")
                st.markdown("This analysis identifies potential root causes by tracing upstream dependencies.")
                
                # Get path processes
                path_processes = trace_upstream_path(selected_process_id, depth=trace_depth)
                
                # Remove the selected process itself
                upstream_processes = [p for p in path_processes if p != selected_process_id]
                
                if upstream_processes:
                    # Create and display a table of upstream processes
                    upstream_data = []
                    for pid in upstream_processes:
                        # Get status
                        status = focused_status.get(pid, 'grey')
                        
                        # Get name - handle special cases
                        if pid in process_names:
                            process_name = process_names[pid]
                        else:
                            process_name = pid  # For special cases like "External trigger"
                        
                        upstream_data.append({
                            "Process ID": pid,
                            "Process Name": process_name,
                            "Status": status.title(),
                            "Impact": "High" if status == 'red' else ("Medium" if status == 'amber' else "Low")
                        })
                    
                    # Sort by impact
                    impact_order = {"High": 0, "Medium": 1, "Low": 2}
                    upstream_data = sorted(upstream_data, key=lambda x: impact_order.get(x["Impact"], 3))
                    
                    upstream_df = pd.DataFrame(upstream_data)
                    st.dataframe(upstream_df, use_container_width=True)
                    
                    # Show process details for problematic upstream processes
                    problem_upstreams = [p["Process ID"] for p in upstream_data if p["Impact"] in ["High", "Medium"]]
                    
                    if problem_upstreams:
                        st.subheader("Problematic Upstream Processes")
                        
                        for pid in problem_upstreams:
                            process_info = next((p for p in process_data if p['qid'] == pid), None)
                            
                            if process_info:
                                with st.expander(f"{pid}: {process_info['process']}"):
                                    st.markdown("#### Process Details:")
                                    st.markdown(f"**Description:** {process_info.get('description', 'No description available')}")
                                    
                                    # Show maturity levels
                                    st.markdown("#### Maturity Levels:")
                                    cols = st.columns(2)
                                    with cols[0]:
                                        st.markdown("**Basic:**")
                                        st.markdown(process_info.get('basic', 'N/A'))
                                        
                                        st.markdown("**Advanced:**")
                                        st.markdown(process_info.get('advanced', 'N/A'))
                                    
                                    with cols[1]:
                                        st.markdown("**Leading:**")
                                        st.markdown(process_info.get('leading', 'N/A'))
                                        
                                        st.markdown("**Emerging:**")
                                        st.markdown(process_info.get('emerging', 'N/A'))
                                    
                                    # Option to further trace this upstream process
                                    if st.button(f"Trace Root Cause for {pid}", key=f"trace_further_{pid}"):
                                        # Store in session state to switch to this process
                                        st.session_state.trace_process = pid
                                        st.rerun()
                    else:
                        st.info("No problematic upstream processes identified")
                else:
                    st.info("No upstream dependencies found. This appears to be a root cause itself.")
            
            with result_tabs[2]:
                st.subheader("KPI Monitoring Recommendations")
                st.markdown("Based on the trace analysis, these are the key performance indicators you should monitor.")
                
                # Get path processes
                path_processes = trace_upstream_path(selected_process_id, depth=trace_depth)
                
                # Map processes to KPIs
                process_kpis = map_processes_to_kpis(path_processes)
                
                if process_kpis:
                    # Create dataframe for display
                    kpi_data = []
                    
                    for pid, kpi in process_kpis.items():
                        if pid in process_names:
                            process_name = process_names[pid]
                        else:
                            process_name = pid  # For special cases
                            
                        status = focused_status.get(pid, 'grey')
                        
                        kpi_data.append({
                            "Process ID": pid,
                            "Process": process_name,
                            "KPI to Monitor": kpi,
                            "Status": status.title(),
                            "Priority": "High" if status == 'red' or pid == selected_process_id else 
                                      ("Medium" if status == 'amber' else "Low")
                        })
                    
                    # Sort by priority
                    priority_order = {"High": 0, "Medium": 1, "Low": 2}
                    kpi_data = sorted(kpi_data, key=lambda x: priority_order.get(x["Priority"], 3))
                    
                    kpi_df = pd.DataFrame(kpi_data)
                    st.dataframe(kpi_df, use_container_width=True)
                    
                    # Summary KPI list for quick reference
                    st.subheader("Critical KPIs to Monitor")
                    
                    high_priority_kpis = [(k["Process ID"], k["KPI to Monitor"]) for k in kpi_data if k["Priority"] == "High"]
                    if high_priority_kpis:
                        for pid, kpi in high_priority_kpis:
                            st.markdown(f"""
                            <div style="background-color: rgba(255, 0, 0, 0.1); padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 4px solid red;">
                                <strong>{pid}: {kpi}</strong>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No high-priority KPIs identified")
                    
                    # Monitoring plan
                    st.subheader("Data Collection Plan")
                    st.markdown("""
                    Based on the root cause analysis, follow these steps to collect the necessary data:
                    
                    1. **Start with high priority KPIs** - These represent the potential root causes
                    2. **Check data availability** - Determine what data sources are needed for these KPIs
                    3. **Collect historical data** where available to establish normal behavior
                    4. **Set up real-time monitoring** for these specific KPIs
                    5. **Establish thresholds** for triggering alerts based on historical trends
                    """)
                    
                    # Call to action
                    st.markdown("""
                    <div style="background-color: #F8F5FF; padding: 15px; border-radius: 5px; margin-top: 20px; border-left: 4px solid #663399;">
                        <h4 style="margin-top: 0; color: #663399;">Next Steps</h4>
                        <p>To confirm the root cause, request data for the high-priority KPIs identified above. 
                        Once collected, analyze the data to verify which upstream process is the actual root cause.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("No relevant KPIs found for the traced processes")