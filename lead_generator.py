#!/usr/bin/env python3
"""
AI Lead Generation System - Complete Deployable Script
Uses Together AI's Llama 3.3 70B model to find, analyze and qualify business leads
"""

import os
import json
import time
import pandas as pd
from datetime import datetime
import streamlit as st
from together import Together
import base64

# API Configuration
API_KEY = "92d982839350af340663ea7ad18ce538fb4a2ebfb8ab182e1be3a64a1bea6949"
client = Together(api_key=API_KEY)
MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

class LeadGenerator:
    def __init__(self):
        self.leads = []
        self.qualified_leads = []
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    def research_leads(self, industry, location, num_leads=3):
        """AI #1: Research and find leads using Llama 3.3"""
        st.write("🔍 Researching businesses...")
        
        # Progress bar for research
        research_progress = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            research_progress.progress(i + 1)
        
        research_prompt = f"""
        You are a B2B lead generation specialist. Find {num_leads} high-potential {industry} in {location}.
        
        For each business, provide the following information in a JSON array:
        - business_name: Full name of the business
        - address: Complete address
        - phone: Phone number if available
        - website: Website URL if available
        - email: Email if available
        - description: Brief description of the business
        - estimated_size: Estimated size (small, medium, large, or square footage if known)
        - year_established: Year established if available (or estimate)
        
        Return ONLY valid JSON that can be parsed, with no additional text.
        """
        
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a lead generation assistant that provides accurate, well-researched business information in JSON format."},
                    {"role": "user", "content": research_prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Find JSON in the response (in case there's surrounding text)
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            
            self.leads = json.loads(content)
            return self.leads
            
        except Exception as e:
            st.error(f"Error during research: {str(e)}")
            # Fallback to sample data
            self.leads = [
                {
                    "business_name": "Premier Dental Care of Buckhead",
                    "address": "3580 Piedmont Rd NE Suite 113, Atlanta, GA 30305",
                    "phone": "(404) 491-7711",
                    "website": "premierdentalcareofbuckhead.com",
                    "email": "info@premierdentalcare.com",
                    "description": "Full-service dental practice with cosmetic and general dentistry services",
                    "estimated_size": "medium",
                    "year_established": "2015"
                },
                {
                    "business_name": "Buckhead Dental Partners",
                    "address": "3525 Piedmont Rd NE Building 8 Suite 415, Atlanta, GA 30305",
                    "phone": "(404) 261-0610",
                    "website": "buckheaddentalpartners.com",
                    "email": "appointment@buckheaddentalpartners.com",
                    "description": "Upscale dental practice specializing in cosmetic and implant dentistry",
                    "estimated_size": "medium",
                    "year_established": "2012"
                },
                {
                    "business_name": "Atlanta Dental Spa - Buckhead",
                    "address": "3189 Maple Dr NE, Atlanta, GA 30305",
                    "phone": "(404) 816-2230",
                    "website": "atlantadentalspa.com",
                    "email": "smile@atlantadentalspa.com",
                    "description": "Luxury dental spa offering high-end dentistry with comfort amenities",
                    "estimated_size": "large",
                    "year_established": "2008"
                }
            ]
            return self.leads
    
    def analyze_and_score_leads(self, industry_criteria=None):
        """AI #2: Analyze and score leads using Llama 3.3"""
        st.write("🧠 Analyzing and scoring leads...")
        
        # Progress bar for analysis
        analysis_progress = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            analysis_progress.progress(i + 1)
        
        if not industry_criteria:
            # Default criteria for generic businesses
            industry_criteria = """
            High-value leads have these characteristics:
            - Located in upscale areas
            - Larger facilities
            - Offering premium services
            - Recent renovations or upscale facilities
            - Complete contact information available
            """
        
        analysis_prompt = f"""
        You are a lead qualification expert for cleaning services. Review these potential business leads:
        
        {json.dumps(self.leads, indent=2)}
        
        Based on these criteria:
        {industry_criteria}
        
        For each lead, add the following fields:
        1. score: A score from 1-5 (5 being highest value)
        2. classification: "High Value", "Medium Value", or "Low Value" based on score
        3. reasoning: Brief explanation of the score
        4. best_contact_method: Recommended way to contact them
        5. personalized_note: A specific observation to mention in outreach
        
        Return the enhanced leads as a valid, parseable JSON array with all original fields plus the new ones.
        """
        
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a lead qualification assistant that analyzes business data and provides scoring in perfect JSON format with no additional text."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Find JSON in the response (in case there's surrounding text)
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)
            
            self.qualified_leads = json.loads(content)
            return self.qualified_leads
            
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
            # Create sample scored data
            self.qualified_leads = self.leads.copy()
            for lead in self.qualified_leads:
                lead["score"] = 4.2
                lead["classification"] = "High Value"
                lead["reasoning"] = "Located in upscale area with complete contact information"
                lead["best_contact_method"] = "Email"
                lead["personalized_note"] = "Your facility's premium image would benefit from specialized cleaning services"
            
            return self.qualified_leads
    
    def generate_outreach_email(self, lead):
        """AI #3: Generate a personalized outreach email"""
        
        prompt = f"""
        Create a personalized outreach email to {lead.get('business_name')} for cleaning services.
        
        Business details:
        {json.dumps(lead, indent=2)}
        
        The email should:
        1. Reference something specific about their business
        2. Position cleaning services as enhancing their professional image
        3. Include their personalized note: {lead.get('personalized_note', '')}
        4. Offer a free consultation
        5. Keep it under 150 words
        
        Return just the email text, with subject line on the first line.
        """
        
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a sales outreach specialist who writes highly effective, personalized business emails."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            st.error(f"Error generating email: {str(e)}")
            return "Error generating personalized email template."
    
    def prepare_spreadsheet(self):
        """Format and export data for client review"""
        st.write("📊 Preparing lead data for export...")
        
        try:
            # Convert to DataFrame for easy export
            df = pd.DataFrame(self.qualified_leads)
            
            # Sort by score (descending)
            df = df.sort_values(by='score', ascending=False)
            
            # Save to Excel
            filename = f"qualified_leads_{self.timestamp}.xlsx"
            df.to_excel(filename, index=False)
            
            # Create a download link
            with open(filename, "rb") as file:
                excel_data = file.read()
            b64 = base64.b64encode(excel_data).decode('utf-8')
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">Download Excel Report</a>'
            
            return href
            
        except Exception as e:
            st.error(f"Error preparing spreadsheet: {str(e)}")
            return None


def create_streamlit_app():
    # Set page config
    st.set_page_config(page_title="AI Lead Generation System", page_icon="🔍", layout="wide")
    
    # Add CSS
    st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton button {
        background-color: #4F46E5;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton button:hover {
        background-color: #4338CA;
    }
    .css-18e3th9 {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    h1, h2, h3 {
        color: #111827;
    }
    .highlight {
        background-color: #f3f4f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .lead-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #4F46E5;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6B7280;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("AI Lead Generation System")
        st.write("Find, analyze, and qualify high-value business leads in minutes")
    with col2:
        st.write("")
        st.write("")
        st.caption("Powered by AI Lead Scoring")
    
    # Initialize session state
    if 'leads' not in st.session_state:
        st.session_state.leads = None
    if 'qualified_leads' not in st.session_state:
        st.session_state.qualified_leads = None
    if 'download_link' not in st.session_state:
        st.session_state.download_link = None
    if 'selected_lead' not in st.session_state:
        st.session_state.selected_lead = None
    if 'email_template' not in st.session_state:
        st.session_state.email_template = None
        
    # Initialize LeadGenerator
    lead_generator = LeadGenerator()
    
    # Input form
    with st.form("lead_gen_form"):
        st.markdown("### Search Parameters")
        
        col1, col2 = st.columns(2)
        with col1:
            industry = st.text_input("Target Industry", "dental practices", help="Type of businesses you want to find")
        with col2:
            location = st.text_input("Location", "Buckhead, Atlanta, GA", help="Geographic area to search in")
        
        criteria = st.text_area(
            "Qualification Criteria (Optional)", 
            "- Located in upscale areas\n- Larger facilities with multiple staff\n- Offering premium services\n- Recent renovations or upscale facilities",
            help="Specific criteria for identifying high-value leads"
        )
        
        num_leads = st.slider("Number of Leads to Find", min_value=3, max_value=10, value=3, help="More leads will take longer to process")
        
        submitted = st.form_submit_button("Generate Qualified Leads")
    
    # Process form submission
    if submitted:
        with st.spinner("Researching businesses..."):
            st.session_state.leads = lead_generator.research_leads(industry, location, num_leads)
        
        with st.spinner("Analyzing and scoring leads..."):
            st.session_state.qualified_leads = lead_generator.analyze_and_score_leads(criteria)
        
        with st.spinner("Preparing export..."):
            st.session_state.download_link = lead_generator.prepare_spreadsheet()
    
    # Display results
    if st.session_state.qualified_leads:
        # Summary metrics
        st.markdown("### Lead Generation Results")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{len(st.session_state.qualified_leads)}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total Leads</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            high_value = len([l for l in st.session_state.qualified_leads if l.get('classification') == 'High Value'])
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{high_value}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">High Value Leads</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            medium_value = len([l for l in st.session_state.qualified_leads if l.get('classification') == 'Medium Value'])
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{medium_value}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Medium Value Leads</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Export link
        if st.session_state.download_link:
            st.markdown(st.session_state.download_link, unsafe_allow_html=True)
        
        # Lead cards
        st.markdown("### Qualified Leads")
        for i, lead in enumerate(st.session_state.qualified_leads):
            st.markdown(f'<div class="lead-card">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"#### {lead.get('business_name')}")
                st.markdown(f"**Address:** {lead.get('address')}")
                st.markdown(f"**Contact:** {lead.get('phone')} | {lead.get('email', 'N/A')}")
                
                expander = st.expander("View details")
                with expander:
                    st.markdown(f"**Website:** {lead.get('website', 'N/A')}")
                    st.markdown(f"**Description:** {lead.get('description', 'N/A')}")
                    st.markdown(f"**Size:** {lead.get('estimated_size', 'N/A')}")
                    st.markdown(f"**Established:** {lead.get('year_established', 'N/A')}")
                    st.markdown(f"**Reasoning:** {lead.get('reasoning', 'N/A')}")
                    st.markdown(f"**Best Contact Method:** {lead.get('best_contact_method', 'N/A')}")
                    st.markdown(f"**Personalized Note:** {lead.get('personalized_note', 'N/A')}")
            
            with col2:
                score = lead.get('score', 0)
                st.markdown(f"**Score: {score}/5**")
                st.progress(float(score)/5)
                st.markdown(f"**Classification:** {lead.get('classification', 'Unknown')}")
                
                if st.button(f"Generate Email for {lead.get('business_name')}", key=f"email_btn_{i}"):
                    st.session_state.selected_lead = lead
                    with st.spinner("Generating personalized email..."):
                        st.session_state.email_template = lead_generator.generate_outreach_email(lead)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Email template display
        if st.session_state.email_template and st.session_state.selected_lead:
            st.markdown("### Personalized Outreach Email")
            st.markdown(f'<div class="highlight">', unsafe_allow_html=True)
            st.write(st.session_state.email_template)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Add copy to clipboard button
            st.button("Copy Email to Clipboard", key="copy_email")
    
    # Footer
    st.markdown("---")
    st.caption("AI Lead Generation System | Prototype Demo")

if __name__ == "__main__":
    create_streamlit_app()
