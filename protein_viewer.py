import streamlit as st
from stmol import showmol
import py3Dmol
import requests  # <--- NEW LIBRARY

# --- PAGE CONFIG ---
st.set_page_config(page_title="3D Protein Viewer", layout="wide")

st.title("🧬 3D Protein Structure Viewer")
st.markdown("""
Visualize the 3D structure of proteins using their **PDB ID**. 
Useful for analyzing folding patterns, binding sites, and secondary structures.
""")

# --- HELPER: FETCH DATA FROM RCSB API ---
@st.cache_data  # Cache this so we don't spam the API on every click
def fetch_pdb_details(pdb_id):
    try:
        # RCSB PDB REST API endpoint
        url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Visualization Settings")
    
    # Input for PDB ID (Default is 4GES based on your discovery)
    pdb_id = st.text_input("Enter PDB ID (e.g., 4GES, 4HHB):", "4GES").upper()
    
    # Style Selection
    style = st.selectbox("Structure Style", ["cartoon", "stick", "sphere", "line"])
    
    # Color Scheme
    color_scheme = st.selectbox("Color Scheme", ["spectrum", "chain", "residue"])
    
    # Spin Animation
    spin = st.checkbox("Auto Spin", value=False)
    
    st.divider()
    st.info(f"Viewing: {pdb_id}")

# --- MAIN VIEWER FUNCTION ---
def render_protein(pdb_id, style, color, spin):
    view = py3Dmol.view(query=f'pdb:{pdb_id}', width=800, height=600)
    
    if style == "cartoon":
        view.setStyle({'cartoon': {'color': color}})
    elif style == "stick":
        view.setStyle({'stick': {}})
    elif style == "sphere":
        view.setStyle({'sphere': {'scale': 0.3}})
    elif style == "line":
        view.setStyle({'line': {}})
        
    view.setBackgroundColor('white')
    
    if spin:
        view.spin(True)
    
    view.zoomTo()
    return view

# --- DISPLAY ---
try:
    # 3 Columns: 70% Viewer, 30% Info
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Render the 3D Model
        view_obj = render_protein(pdb_id, style, color_scheme, spin)
        showmol(view_obj, height=600, width=800)
        
    with col2:
        st.subheader("Structure Details")
        
        # Fetch live data
        data = fetch_pdb_details(pdb_id)
        
        if data:
            # Extract info safely (using .get in case fields are missing)
            title = data.get("struct", {}).get("title", "No Title Found")
            classification = data.get("struct_keywords", {}).get("pdbx_keywords", "Unknown")
            method = data.get("exptl", [{}])[0].get("method", "Unknown")
            deposition_date = data.get("rcsb_accession_info", {}).get("deposit_date", "Unknown")
            
            # Display the info
            st.success(f"**ID:** {pdb_id}")
            st.markdown(f"**Title:**  \n{title.title()}")
            st.markdown(f"**Classification:**  \n{classification}")
            st.markdown(f"**Method:**  \n{method}")
            st.markdown(f"**Deposited:**  \n{deposition_date}")
            
        else:
            st.warning("Could not fetch details from PDB. The ID might be valid but missing metadata, or internet is down.")

        st.divider()
        st.markdown(f"[View on RCSB.org](https://www.rcsb.org/structure/{pdb_id})")

except Exception as e:
    st.error(f"Error loading structure: {e}")