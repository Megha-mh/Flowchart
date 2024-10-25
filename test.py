import json
from datetime import date
from pydantic import BaseModel
import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
from typing import List
import os

# Fetching the API key from the environment variable
groq_api_key = os.getenv("GROQ_API_KEY")

# Check if API key is available
if not groq_api_key:
    st.error("Groq API key not found in environment variable!")

# Initializing the Groq object with the API key
groq = Groq(api_key=groq_api_key)

# Ensure session state is initialized
if 'flow_chart_steps' not in st.session_state:
    st.session_state['flow_chart_steps'] = []

if 'business_flow_steps' not in st.session_state:
    st.session_state['business_flow_steps'] = []

class FlowChartStep(BaseModel):
    title: str
    description: str

# Function to generate professional content based on input
def generate_professional_content(section_title: str, user_input: str) -> str:
    """Simulate generating professional content based on user input."""
    if "billing" in section_title.lower():
        return f"The company has implemented a robust billing system. {user_input} This ensures a streamlined invoicing process with multiple payment gateways available to customers."
    elif "place of supply" in section_title.lower():
        return f"The primary place of supply is {user_input}, which ensures compliance with the relevant regional tax laws and regulations."
    elif "expenses and cost of sales" in section_title.lower():
        return f"The company manages expenses like {user_input}, ensuring that the cost of sales is minimized while maximizing profitability."
    else:
        return f"{user_input}"  # Default fallback if no match

class RenderHTML:
    def __init__(self, name, description, flow_chart_steps, arrow_chart, business_activity, business_flow_steps):
        self.name = name
        self.description = description
        self.flow_chart_steps = flow_chart_steps if flow_chart_steps else []
        self.arrow_chart = arrow_chart
        self.business_activity = business_activity
        self.business_flow_steps = business_flow_steps if business_flow_steps else []

    def improve_arrow_chart_content(self):
        """Modify and improve the arrow chart content based on user inputs."""
        return {
            "title1": self.arrow_chart.get('title1', 'Business Activity').title().strip(),
            "content1": generate_professional_content('Business Activity', self.business_activity),

            "title2": self.arrow_chart.get('title2', 'Billing System').title().strip(),
            "content2": generate_professional_content('Billing System', self.arrow_chart.get('content2')),
            
            "title3": self.arrow_chart.get('title3', 'Place Of Supply').title().strip(),
            "content3": generate_professional_content('Place of Supply', self.arrow_chart.get('content3')),
            
            "title4": self.arrow_chart.get('title4', 'Expenses And Cost Of Sales').title().strip(),
            "content4": generate_professional_content('Expenses and Cost of Sales', self.arrow_chart.get('content4')),
        }

    def generate_arrow_chart(self):
        """Generate the improved arrow chart HTML with bold headings for bullet points."""
        improved_arrow_chart = self.improve_arrow_chart_content()

        category_chart_html = ""
        for i in range(1, 5):
            title = improved_arrow_chart.get(f'title{i}', '').strip()
            content = improved_arrow_chart.get(f'content{i}', '').strip()
            
            if title or content:
                # Split content into bullet points and apply formatting for bold headings
                bullet_points = content.split('•')
                formatted_content = "".join(
                    f"<li><strong>{point.split(':')[0].strip()}</strong>: {':'.join(point.split(':')[1:]).strip()}</li>"
                    for point in bullet_points if point.strip()
                )
                category_chart_html += f"""
                    <div style="display: flex; margin-bottom:20px; align-items: center;">
                        <div style="background-color: #0C6C98; width: 190px; min-height: 80px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; padding-left: 5px; font-weight: bold;">
                            {title}
                        </div>
                        <div style="width: 230px; min-height: 80px; background-color: #D3D3D3; margin-left: 0px; display: flex; align-items: center; justify-content: flex-start; color: black; font-size: 12px; padding-left: 10px; line-height: 1.5;">
                            <ul style="list-style: none; padding: 0; margin: 0;">{formatted_content}</ul>
                        </div>
                        <div style="width: 0; height: 0; border-top: 40px solid transparent; border-bottom: 40px solid transparent; border-left: 70px solid #D3D3D3;"></div>
                    </div>
                """
        return category_chart_html

    def generate_business_flow_chart(self):
        """Generate the business flow chart HTML content with arrows between steps."""
        if not self.business_flow_steps:
            return "<p>No business flow steps available.</p>"

        flow_chart_html = ""
        for index, step in enumerate(self.business_flow_steps):
            flow_chart_html += f"""
                <div style="padding: 10px; margin-bottom: 15px; background-color: #f0f0f0; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <h4 style="margin: 5px 0; color: #333;">Step {index + 1}: {step['title']}</h4>
                    <p style="font-size: 0.9em; color: #555;">{step['description']}</p>
                </div>
            """
            if index < len(self.business_flow_steps) - 1:
                flow_chart_html += """
                    <div style="text-align: center; font-size: 24px; margin: 10px 0;">
                        &#x2193;
                    </div>
                """
        return flow_chart_html

    def generate_html(self):
        """Generate the complete HTML output, including arrow chart and business flow chart."""
        arrow_chart_html = self.generate_arrow_chart()
        business_flow_chart_html = self.generate_business_flow_chart()

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Business Flow Chart</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.9.2/html2pdf.bundle.min.js"></script>
            <script>
                function downloadPDF() {{
                    const element = document.getElementById('pdf-content');
                    html2pdf()
                        .from(element)
                        .set({{
                            margin: 1,
                            filename: 'business_flow_chart.pdf',
                            html2canvas: {{ scale: 2 }},
                            jsPDF: {{ format: 'a4', orientation: 'portrait' }}
                        }}).save();
                }}
            </script>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 210mm; margin: 0 auto;">
            <div id="pdf-content" style="padding: 50px;">
                <h3 style="margin-top: 20px; text-align: center;">{self.name}</h3>
                <h5>Date: {date.today().strftime("%d/%m/%Y")}</h5>
                <h4>Subject: Business Flow Chart</h4>
                
                <div style="font-size: 0.9em;">
                    <p>{self.description}</p>
                </div>

                <div style="page-break-after: always;">
                    {arrow_chart_html}
                </div>

                <h3>Business Flow Chart</h3>
                <div id="flow-chart">
                    {business_flow_chart_html}
                </div>

                <p style="margin-top: 100px">I hereby declare that the information is complete and best to my knowledge.</p>
                <p>Authorized Signatory (Sign & Stamp)</p>
            </div>

            <button onclick="downloadPDF()">Download PDF</button>
        </body>
        </html>
        """
        return html_content

# Streamlit UI
st.title("Business Flow Chart Renderer")

# Input fields
name_input = st.text_input("Enter the name of the company:", "")
business_description_input = st.text_area("Enter the Company Description:")
business_activity_input = st.text_area("Enter the Business Activity (bullet points with headings):")
input_arrowchart_content2 = st.text_input('Billing system (how payment is collected from customers)', key="input_arrowchart_content2")
input_arrowchart_content3 = st.text_input('Enter the Place of Supply', key="input_arrowchart_content3")
input_arrowchart_content4 = st.text_input('Enter the content For EXPENSES AND COST OF SALES', key="input_arrowchart_content4")

arrow_chart = {
    "title1": "BUSINESS",
    "title2": "Billing System",
    "title3": "PLACE OF SUPPLY",
    "title4": "EXPENSES AND COST OF SALES",
    "content1": business_activity_input,
    "content2": input_arrowchart_content2,
    "content3": input_arrowchart_content3,
    "content4": input_arrowchart_content4
}

# Select number of business flow steps
num_steps = st.number_input("How many steps do you want to add to the Business Flow Chart?", min_value=1, max_value=20, value=1, step=1)

# Collect business flow steps
st.subheader("Add Steps for Business Flow Chart")
for i in range(num_steps):
    step_title = st.text_input(f"Step {i + 1} Title", key=f"title_{i}")
    step_description = st.text_area(f"Step {i + 1} Description", key=f"description_{i}")

    # Store each step
    if st.button(f"Add Step {i + 1}"):
        st.session_state['business_flow_steps'].append({
            "title": step_title,
            "description": step_description
        })
        st.success(f"Step {i + 1} added successfully")

# Display and edit flow steps
if st.session_state['business_flow_steps']:
    st.subheader("Edit Business Flow Steps")
    for i, step in enumerate(st.session_state['business_flow_steps']):
        st.text_input(f"Step {i+1} Title", value=step['title'], key=f"edit_title_{i}")
        st.text_area(f"Step {i+1} Description", value=step['description'], key=f"edit_description_{i}")

    if st.button("Render Flow Chart"):
        html_generator = RenderHTML(
            name=name_input,
            description=business_description_input,
            flow_chart_steps=st.session_state['flow_chart_steps'],
            arrow_chart=arrow_chart,
            business_activity=business_activity_input,
            business_flow_steps=st.session_state['business_flow_steps']
        )
        html_output = html_generator.generate_html()
        components.html(html_output, height=800, scrolling=True)
