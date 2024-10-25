import json
from datetime import date
from pydantic import BaseModel
import streamlit as st
import streamlit.components.v1 as components
import os
from typing import List, Dict

# Fetching the API key from the environment variable
groq_api_key = os.getenv("GROQ_API_KEY")

# Check if API key is available
if not groq_api_key:
    st.error("Groq API key not found in environment variable!")

# Ensure session state is initialized
if 'flow_chart_steps' not in st.session_state:
    st.session_state['flow_chart_steps'] = []

class FlowChartStep(BaseModel):
    title: str
    description: str

# Function to simulate dynamic, professional content generation based on input
def generate_professional_content(section_title: str, user_input: str) -> str:
    """Generate tailored professional content based on section context."""
    if "billing" in section_title.lower():
        return f"The company has implemented a robust billing system. {user_input} This ensures a streamlined invoicing process with multiple payment gateways available to customers."
    elif "place of supply" in section_title.lower():
        return f"The primary place of supply is {user_input}, which ensures compliance with relevant regional tax laws."
    elif "expenses and cost of sales" in section_title.lower():
        return f"Expenses, including {user_input}, are managed carefully to maintain cost-efficiency and profitability."
    else:
        return user_input  # Fallback if no specific match

# Function to generate flow chart steps
def generate_flow_chart_steps(explanation: str) -> List[Dict[str, str]]:
    # Simulated response interpretation to generate a set of flow chart steps
    steps = []
    
    # Example mock steps based on input context
    if "process" in explanation.lower():
        steps.append({"title": "Step 1: Identify Needs", "description": "Determine business requirements for a customized process."})
        steps.append({"title": "Step 2: Resource Allocation", "description": "Assign necessary resources and personnel."})
        steps.append({"title": "Step 3: Implement Strategy", "description": "Execute the designed process with all steps."})
    else:
        steps.append({"title": "Initial Setup", "description": "Outline the initial setup requirements."})

    return steps

class RenderHTML:
    def __init__(self, name, description, flow_chart_steps, arrow_chart, business_activity):
        self.name = name
        self.description = description
        self.flow_chart_steps = flow_chart_steps if flow_chart_steps else []
        self.arrow_chart = arrow_chart
        self.business_activity = business_activity

    def improve_arrow_chart_content(self) -> Dict[str, str]:
        """Modify and improve the arrow chart content based on user inputs."""
        return {
            "title1": self.arrow_chart.get('title1', 'Business Activity').title(),
            "content1": generate_professional_content('Business Activity', self.business_activity),
            "title2": self.arrow_chart.get('title2', 'Billing System').title(),
            "content2": generate_professional_content('Billing System', self.arrow_chart.get('content2')),
            "title3": self.arrow_chart.get('title3', 'Place Of Supply').title(),
            "content3": generate_professional_content('Place of Supply', self.arrow_chart.get('content3')),
            "title4": self.arrow_chart.get('title4', 'Expenses And Cost Of Sales').title(),
            "content4": generate_professional_content('Expenses and Cost of Sales', self.arrow_chart.get('content4')),
        }

    def generate_arrow_chart(self) -> str:
        """Generate the improved arrow chart HTML."""
        improved_arrow_chart = self.improve_arrow_chart_content()
        category_chart_html = ""
        for i in range(1, 5):
            title = improved_arrow_chart.get(f'title{i}', '').strip()
            content = improved_arrow_chart.get(f'content{i}', '').strip()
            if title or content:
                category_chart_html += f"""
                    <div style="display: flex; margin-bottom:20px; align-items: center;">
                        <div style="background-color: #0C6C98; width: 190px; min-height: 80px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; padding-left: 5px; font-weight: bold;">
                            {title}
                        </div>
                        <div style="width: 230px; min-height: 80px; background-color: #D3D3D3; margin-left: 0px; display: flex; align-items: center; justify-content: flex-start; color: black; font-size: 12px; padding-left: 10px; line-height: 1.5;">
                            {content.replace(',', '<br>')}
                        </div>
                        <div style="width: 0; height: 0; border-top: 40px solid transparent; border-bottom: 40px solid transparent; border-left: 70px solid #D3D3D3;"></div>
                    </div>
                """
        return category_chart_html

    def generate_flow_chart(self) -> str:
        """Generate the flow chart HTML content."""
        if not self.flow_chart_steps:
            return "<p>No flow chart steps available.</p>"

        flow_chart_html = ""
        for index, step in enumerate(self.flow_chart_steps):
            if index != 0:
                flow_chart_html += """<div style="position: relative; text-align: center; font-size: 24px;">
                                        <div style="width: 0; height: 0; border-left: 10px solid transparent; border-right: 10px solid transparent; border-top: 10px solid #333; margin: 10px auto;"></div>
                                    </div>"""
            flow_chart_html += f"""
                <div style="padding: 0px 0px 0px 50px;">
                    <div style="max-width: 90%; padding: 10px 10px 10px 30px; background-color: #f0f0f0; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); text-align: center; position: relative; page-break-inside: avoid;">
                        <h4 style="margin: 5px 0; color: #333;">{step['title']}</h4>
                        <div style="margin-top: 5px; font-size: 0.9em; color: #555; text-align: left;">
                            {step['description']}
                        </div>
                    </div>
                </div>
            """
        return flow_chart_html

    def generate_html(self) -> str:
        """Generate the complete HTML output including flow chart and arrow chart."""
        flow_chart_html = self.generate_flow_chart()
        arrow_chart_html = self.generate_arrow_chart()

        arrow_chart_with_page_break = f"""
        <div style="page-break-after: always;">
            {arrow_chart_html}
        </div>
        """ if arrow_chart_html else ""

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
                {arrow_chart_with_page_break}
                <div id="flow-chart">
                    <h3>Procurement Process:</h3>
                    {flow_chart_html}
                </div>
                <p>I hereby declare that the information is complete and best to my knowledge.</p>
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
business_activity_input = st.text_area("Enter the Business Activity:")
input_arrowchart_content2 = st.text_input('Billing system (how payment is collected from customers)')
input_arrowchart_content3 = st.text_input('Enter the Place of Supply')
input_arrowchart_content4 = st.text_input('Enter the content For EXPENSES AND COST OF SALES')

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

st.subheader("Flow Chart Steps")
explanation = st.text_area("Step Explanation", "Step Explanation")

# Button to generate flow chart steps
if st.button("Generate Flow Chart"):
    flow_chart_steps = generate_flow_chart_steps(explanation)
    st.session_state['flow_chart_steps'] = flow_chart_steps

# Editing Flow Chart Steps
if 'flow_chart_steps' in st.session_state:
    st.subheader("Edit Flow Chart Steps")
    edited_steps = []
    
    for i, step in enumerate(st.session_state['flow_chart_steps']):
        title_input = st.text_input(f"Step {i+1} Title", value=step['title'], key=f"title_{i}")
        description_input = st.text_area(f"Step {i+1} Description", value=step['description'], key=f"description_{i}")
        edited_steps.append({"title": title_input, "description": description_input})

    st.session_state['flow_chart_steps'] = edited_steps

    # Render the flow chart HTML
    if st.button("Render Flow Chart"):
        html_generator = RenderHTML(
            name=name_input,
            description=business_description_input,
            flow_chart_steps=st.session_state['flow_chart_steps'],
            arrow_chart=arrow_chart,
            business_activity=business_activity_input
        )
        html_output = html_generator.generate_html()
        components.html(html_output, height=800, scrolling=True)
