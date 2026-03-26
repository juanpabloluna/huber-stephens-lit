"""
Visualizations page — generate interactive concept maps, causal graphs,
and comparison diagrams from the Huber-Stephens literature corpus.
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import streamlit.components.v1 as components
from loguru import logger

from src.utils.auth import require_auth

require_auth()

st.title("Interactive Visualizations")
st.markdown(
    "Generate concept maps, causal graphs, timelines, and comparison diagrams "
    "grounded in the Huber-Stephens literature corpus."
)


@st.cache_resource
def get_viz_engine():
    """Initialize and cache the visualization engine."""
    try:
        from src.agents.visualization_engine import VisualizationEngine
        return VisualizationEngine()
    except Exception as e:
        st.error(f"Error initializing visualization engine: {e}")
        logger.error(f"Failed to init viz engine: {e}", exc_info=True)
        return None


# Sidebar controls
with st.sidebar:
    st.markdown("### Visualization Settings")
    n_results = st.slider("Context chunks", 10, 30, 20)
    year_min = st.number_input("Min year", 1980, 2025, 1992)
    year_max = st.number_input("Max year", 1980, 2025, 2025)

    st.markdown("---")
    st.markdown("### Example Prompts")
    examples = [
        "Map the causal drivers of welfare state generosity across the corpus",
        "Show the evolution of the state concept from 1992 to 2024",
        "Create a comparison: power resources theory vs. state erosion framework",
        "Graph the relationship between partisanship, labor, and redistribution",
        "Timeline of how the three power clusters concept evolved",
        "Concept map of state capacity dimensions: autonomy, reach, effectiveness",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex[:30]}", use_container_width=True):
            st.session_state["viz_request"] = ex


# Main input
request = st.text_area(
    "Describe the visualization you want:",
    value=st.session_state.get("viz_request", ""),
    height=100,
    placeholder="e.g., Map the causal relationship between partisan incumbency, welfare generosity, and inequality reduction across the Huber-Stephens corpus",
)

col1, col2 = st.columns([1, 4])
with col1:
    generate = st.button("Generate", type="primary", use_container_width=True)

if generate and request:
    engine = get_viz_engine()
    if engine is None:
        st.error("Visualization engine not available.")
    else:
        with st.spinner("Searching across the Huber-Stephens corpus and building your visualization... This may take 30-60 seconds."):
            try:
                html = engine.generate_visualization(
                    request=request,
                    n_results=n_results,
                    year_range=(year_min, year_max),
                )

                # Store for download
                st.session_state["last_viz_html"] = html

                # Render
                st.markdown("---")
                st.markdown("### Generated Visualization")
                components.html(html, height=700, scrolling=True)

            except Exception as e:
                st.error(f"Error generating visualization: {e}")
                logger.error(f"Viz generation failed: {e}", exc_info=True)

# Download button (persists across reruns)
if "last_viz_html" in st.session_state:
    st.download_button(
        label="Download HTML",
        data=st.session_state["last_viz_html"],
        file_name="huber_stephens_visualization.html",
        mime="text/html",
        use_container_width=True,
    )
