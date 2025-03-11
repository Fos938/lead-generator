#!/usr/bin/env python3
"""
Enaks Prospector 3.0 - Medical/Commercial Lead Generation
Optimized for Atlanta & Charlotte Markets (Local AI Version)
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import pandas as pd
from datetime import datetime
import streamlit as st
import json
import re

# Local Model Configuration
MODELS = {
    "lead_research": "mistralai/Mistral-7B-Instruct-v0.2",
    "analysis": "HuggingFaceH4/zephyr-7b-beta",
    "compliance": "Epic-Research/Meditron-7B"
}

# Hardware Configuration
device = "cuda" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if device == "cuda" else torch.float32

@st.cache_resource
def load_model(model_name):
    """Load quantized models locally"""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        torch_dtype=torch_dtype,
        load_in_4bit=True
    )
    return pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device=device
    )

class EnaksLeadGenerator:
    def __init__(self):
        self.research_pipe = load_model(MODELS["lead_research"])
        self.analysis_pipe = load_model(MODELS["analysis"])
        self.compliance_pipe = load_model(MODELS["compliance"])
        self.leads = []
        
    # Enaks-specific configuration
    ENAKS_PROFILE = {
        "services": ["Medical Facility Cleaning", "Class A Office Maintenance",
                    "Post-Construction Cleanup", "LEED Certification Support"],
        "usp": "OSHA/HIPAA-compliant cleaning with eco-friendly products",
        "locations": ["Atlanta", "Charlotte"],
        "certifications": ["Bloodborne Pathogen", "HIPAA Compliance", "Green Seal"],
        "targets": {
            "medical": ["Buckhead Dental Partners", "MetroDerm", "Northside Orthopedic"],
            "commercial": ["Perimeter Summit", "Concourse Corporate", "Premier Plaza"]
        }
    }

    def generate_leads(self, property_type, location):
        """Mistral-7B lead generation with Enaks focus"""
        prompt = f"""
        [ENAKS PROFILE]
        {json.dumps(self.ENAKS_PROFILE, indent=2)}
        
        [INSTRUCTIONS]
        Find 5 {property_type} in {location} needing cleaning services.
        Focus on:
        - Medical: 10+ procedure rooms, 2020+ renovations
        - Commercial: Class A offices >10k sq ft, high tenant turnover
        
        Output JSON array with:
        - name, address, phone, sq_ft, renovation_year, pain_points
        """
        
        response = self.research_pipe(
            prompt,
            max_new_tokens=1024,
            temperature=0.3
        )
        
        json_str = re.search(r'\[.*\]', response[0]['generated_text'], re.DOTALL).group()
        self.leads = json.loads(json_str)
        return self.leads

    def analyze_leads(self):
        """Zephyr-7B analysis with medical/commercial scoring"""
        analysis_prompt = f"""
        Analyze these leads for Enaks Cleaning Services:
        {json.dumps(self.leads, indent=2)}
        
        Medical Scoring (0-100):
        - 35% Procedure rooms
        - 30% Renovation recency
        - 20% Square footage
        - 15% Compliance needs
        
        Commercial Scoring (0-100):
        - 40% Class rating
        - 30% Renovation age
        - 20% Tenant turnover
        - 10% Medical proximity
        
        Add fields:
        - priority_score
        - service_package
        - urgency (Immediate/<1 month/1-3 months)
        """
        
        response = self.analysis_pipe(
            analysis_prompt,
            max_new_tokens=2048,
            temperature=0.2
        )
        
        analyzed = json.loads(response[0]['generated_text'])
        return analyzed

    def generate_proposal(self, lead):
        """Meditron-7B compliance-focused outreach"""
        prompt = f"""
        Create HIPAA/OSHA-compliant outreach for:
        {json.dumps(lead, indent=2)}
        
        Include:
        - Recent similar clients (Grady Correll Pavilion, Perimeter Summit)
        - Free compliance audit offer
        - Eco-friendly product emphasis
        - 24/7 availability
        """
        
        response = self.compliance_pipe(
            prompt,
            max_new_tokens=512,
            temperature=0.6
        )
        return response[0]['generated_text']

# Streamlit Interface
def enaks_interface():
    st.set_page_config(page_title="Enaks Lead AI", layout="wide", page_icon="🏥")
    
    st.markdown("""
    <style>
    .enaks-header { color: #1a4f8b; }
    .metric-card { background: #f8f9fa; border-radius: 10px; padding: 20px; }
    .stProgress > div > div { background-color: #1a4f8b !important; }
    </style>
    """, unsafe_allow_html=True)

    st.title("🏥 Enaks Prospector 3.0")
    st.write("**Medical & Commercial Cleaning Lead Generation**")
    
    generator = EnaksLeadGenerator()
    
    with st.form("lead_form"):
        col1, col2 = st.columns(2)
        with col1:
            prop_type = st.selectbox("Property Type", ["Medical", "Commercial"])
        with col2:
            location = st.selectbox("Location", ["Buckhead, Atlanta", "Ballantyne, Charlotte"])
        
        if st.form_submit_button("Generate Leads"):
            with st.spinner("Scanning commercial registries..."):
                st.session_state.leads = generator.generate_leads(prop_type, location)
                st.session_state.scored = generator.analyze_leads()
    
    if st.session_state.get('scored'):
        st.header("Priority Targets")
        
        # Metrics
        high = sum(1 for l in st.session_state.scored if l['priority_score'] >= 80)
        st.metric("High Priority Leads", high)
        
        # Leads Display
        for lead in st.session_state.scored:
            with st.expander(f"{lead['name']} - Score: {lead['priority_score']}"):
                col1, col2 = st.columns([3,1])
                with col1:
                    st.write(f"**Address:** {lead['address']}")
                    st.write(f"**Square Feet:** {lead.get('sq_ft', 'N/A')}")
                    st.write(f"**Renovation Year:** {lead.get('renovation_year', 'N/A')}")
                    st.write(f"**Service Package:** {lead['service_package']}")
                with col2:
                    st.write(f"**Urgency:** {lead['urgency']}")
                    if st.button("Generate Proposal", key=lead['name']):
                        st.session_state.proposal = generator.generate_proposal(lead)
        
        if 'proposal' in st.session_state:
            st.subheader("Compliance-Focused Proposal")
            st.code(st.session_state.proposal)

    st.markdown("---")
    st.caption("Enaks Cleaning Services - AI Lead Generation System")

if __name__ == "__main__":
    enaks_interface()
