import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from data_loader import get_stage_names

def create_radar_chart(banks_data, selected_banks, title="Bank Capability Comparison"):
    """
    Create a radar chart comparing selected banks across all payment stages
    
    Parameters:
    - banks_data: Dictionary containing bank scores
    - selected_banks: List of bank names to display
    - title: Chart title
    
    Returns:
    - Plotly figure object
    """
    stage_names = get_stage_names()
    categories = [f"{i}. {stage_names[i]}" for i in range(1, 13)]
    
    fig = go.Figure()
    
    for bank in selected_banks:
        if bank in banks_data:
            values = [banks_data[bank][i] for i in range(1, 13)]
            # Add a duplicate value at the end to close the radar loop
            values.append(values[0])
            # Add categories to plot
            categories_plot = categories.copy()
            categories_plot.append(categories[0])
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories_plot,
                fill='toself',
                name=bank
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 4]
            )
        ),
        showlegend=True,
        title=title,
        height=600
    )
    
    return fig

def create_stage_chart(bank_data, stage_id, comparison_banks=None):
    """
    Create a bar chart for a specific stage comparing current assessment with benchmarks
    """
    stage_names = get_stage_names()
    fig = go.Figure()
    
    # Add current assessment
    if bank_data:
        fig.add_trace(go.Bar(
            x=["Your Assessment"],
            y=[bank_data],
            name="Your Assessment",
            marker_color='#663399'
        ))
    
    # Add comparison banks if provided
    if comparison_banks:
        for bank, score in comparison_banks.items():
            if score.get(stage_id):
                fig.add_trace(go.Bar(
                    x=[bank],
                    y=[score[stage_id]],
                    name=bank
                ))
    
    fig.update_layout(
        title=f"Stage {stage_id}: {stage_names[stage_id]} - Comparison",
        xaxis_title="Bank",
        yaxis_title="Maturity Score (0-4)",
        yaxis=dict(range=[0, 4]),
        legend_title="Banks",
        barmode='group'
    )
    
    return fig

def create_outcome_chart(outcome_data):
    """
    Create a radar chart for business outcomes
    """
    outcomes = [item["Outcome"] for item in outcome_data]
    scores = [item["Score"] for item in outcome_data]
    
    # Add the first outcome at the end to close the radar loop
    outcomes.append(outcomes[0])
    scores.append(scores[0])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=outcomes,
        fill='toself',
        name="Business Outcomes"
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 4]
            )
        ),
        showlegend=False,
        title="Business Outcome Analysis",
        height=500
    )
    
    return fig

def create_maturity_heatmap(banks_data, selected_banks):
    """
    Create a heatmap showing maturity levels across stages and banks
    """
    stage_names = get_stage_names()
    
    # Prepare data for heatmap
    z_data = []
    for bank in selected_banks:
        if bank in banks_data:
            bank_scores = [banks_data[bank][i] for i in range(1, 13)]
            z_data.append(bank_scores)
    
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=[f"{i}. {stage_names[i][:10]}..." for i in range(1, 13)],
        y=selected_banks,
        colorscale="Viridis",
        hoverongaps=False,
        colorbar=dict(
            title="Maturity<br>Score",
            tickmode="array",
            tickvals=[0, 1, 2, 3, 4],
            ticktext=["0", "1", "2", "3", "4"],
            ticks="outside"
        )
    ))
    
    fig.update_layout(
        title="Payment Capability Maturity Heatmap",
        height=400,
        margin=dict(l=50, r=50, t=80, b=50),
    )
    
    return fig