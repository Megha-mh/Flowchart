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

class FlowChartStep(BaseModel):
    title: str
    description: str

def generate_flow_chart_steps(explanation: str) -> List[FlowChartStep]:
    try:
        # API call to Groq
        chat_completion = groq.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": ("Please provide a very detailed step-by-step guide with 6 to 10 steps. Each step should have a title and a description, "
                                "description shall include key points and it shall have 4-5 points for each title, "
                                "without new lines. Ensure the JSON is correctly formatted with commas separating the fields, "
                                "and avoid any extra fields or incorrect structure. "
                                f"The JSON object must use the schema: {json.dumps(FlowChartStep.model_json_schema(), indent=2)}")
                },
                {
                    "role": "user",
                    "content": explanation,
                },
            ],
            model="llama3-8b-8192",
            temperature=0,
            stream=False,
            response_format={"type": "json_object"},
        )
        # Ensure response parsing is handled correctly
        try:
            steps = json.loads(chat_completion.choices[0].message.content)
        except json.JSONDecodeError as e:
            st.error(f"JSON parsing error: {str(e)}")
            return []
        
        return steps['steps']
    except Exception as e:
        st.error(f"Error generating flow chart steps: {str(e)}")
        return []

class RenderHTML:
    def __init__(self, name, flow_chart_steps, arrow_chart, introduction):
        self.name = name
        self.flow_chart_steps = flow_chart_steps if flow_chart_steps else []  # Ensure flow_chart_steps is a list
        self.arrow_chart = arrow_chart
        self.introduction = introduction

    def improve_arrow_chart_content(self):
        """Modify and improve the arrow chart content, making it more professional and capitalized."""
        return {
            "title1": self.arrow_chart.get('title1', 'Business Activity').title().strip(),
            "content1": "The business focuses on delivering high-quality services to its clients by leveraging industry best practices and ensuring customer satisfaction across various domains.".title().strip(),
            
            "title2": self.arrow_chart.get('title2', 'Billing System').title().strip(),
            "content2": "The company utilizes an efficient billing system where payments are collected through secure gateways. Clients are invoiced electronically with various payment options available.".title().strip(),
            
            # Dynamic Place of Supply with elaboration
            "title3": self.arrow_chart.get('title3', 'Place Of Supply').title().strip(),
            "content3": f"The primary place of supply is {self.arrow_chart.get('content3')}. This location is crucial for ensuring compliance with local tax regulations.".title().strip(),
            
            # Dynamic Expenses and Cost of Sales with elaboration
            "title4": self.arrow_chart.get('title4', 'Expenses And Cost Of Sales').title().strip(),
            "content4": f"The company manages expenses such as {self.arrow_chart.get('content4')}, ensuring cost-effective practices to maximize profitability.".title().strip(),
        }

    def generate_arrow_chart(self):
        """Generate the improved arrow chart HTML."""
        improved_arrow_chart = self.improve_arrow_chart_content()

        category_chart_html = ""
        for i in range(1, 5):
            title = improved_arrow_chart.get(f'title{i}', '').strip()
            content = improved_arrow_chart.get(f'content{i}', '').strip()
            
            if title or content:  # Only render if there's valid content
                category_chart_html += f"""
                    <div style="display: flex; margin-bottom:20px; align-items: center;">
                        <div style="background-color: #0C6C98; width: 190px; height: 80px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; padding-left: 5px; font-weight: bold;">
                            {title}
                        </div>
                        <div style="width: 230px; height: 130px; background-color: #D3D3D3; margin-left: 0px; display: flex; align-items: center; justify-content: flex-start; color: black; font-size: 12px; padding-left: 10px; line-height: 1.5;">
                            {content.replace(',', '<br>')}
                        </div>
                        <div style="width: 0; height: 0; border-top: 80px solid transparent; border-bottom: 80px solid transparent; border-left: 70px solid #D3D3D3;"></div>
                    </div>
                """
        return category_chart_html

    def generate_flow_chart(self):
        """Generate the flow chart HTML content."""
        if not self.flow_chart_steps:
            return "<p>No flow chart steps available.</p>"

        flow_chart_html = ""
        try:
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
                                {step['description'].replace('*', '') if isinstance(step['description'], str) else str(step['description']).replace('*', '').replace('[', '').replace(']', '')}
                            </div>
                        </div>
                    </div>
                """
        except Exception as e:
            st.error(f"Error generating flow chart: {str(e)}")
            return "<p>Error generating flow chart content.</p>"

        return flow_chart_html

    def generate_html(self):
        """Generate the complete HTML output including flow chart and arrow chart."""
        flow_chart_html = self.generate_flow_chart()
        arrow_chart_html = self.generate_arrow_chart()

        # Add page break after arrow chart if arrow_chart_html exists
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
                            html2canvas: {{ scale: 2 }}),
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
                    <p>{self.introduction}</p>
                </div>
                
                <!-- Arrow Chart with Page Break -->
                {arrow_chart_with_page_break}
                
                <!-- Flow Chart -->
                <div id="flow-chart">
                    <h3>Procurement Process:</h3>
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 20px;">
                        {flow_chart_html}
                    </div>
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
company_intro_input = st.text_area("Enter the introduction for the company:")
input_arrowchart_content1 = st.text_input('Enter the content For BUSINESS ACTIVITY', key="input_arrowchart_content1")
input_arrowchart_content2 = st.text_input('Billing system (how payment is collected from customers)', key="input_arrowchart_content2")
input_arrowchart_content3 = st.text_input('Enter the Place of Supply', key="input_arrowchart_content3")  # Updated Place of Supply
input_arrowchart_content4 = st.text_input('Enter the content For EXPENSES AND COST OF SALES', key="input_arrowchart_content4")  # Updated for expenses

arrow_chart = {
    "title1": "BUSINESS",
    "title2": "Billing System",
    "title3": "PLACE OF SUPPLY",
    "title4": "EXPENSES AND COST OF SALES",
    "content1": input_arrowchart_content1,
    "content2": input_arrowchart_content2,
    "content3": input_arrowchart_content3,  # Dynamically pass the Place of Supply content
    "content4": input_arrowchart_content4   # Dynamically pass the Expenses and Cost of Sales content
}

st.subheader("Flow Chart Steps")
explanation = st.text_area("Step Explanation", "Step Explanation")

# Button to generate flow chart steps
if st.button("Generate Flow Chart"):
    flow_chart_steps = generate_flow_chart_steps(explanation)
    st.session_state['flow_chart_steps'] = flow_chart_steps  # Store in session state

# Check if flow chart steps are in session state
if 'flow_chart_steps' in st.session_state:
    st.subheader("Edit Flow Chart Steps")
    edited_steps = []
    
    for i, step in enumerate(st.session_state['flow_chart_steps']):
        title_input = st.text_input(f"Step {i+1} Title", value=step['title'], key=f"title_{i}")
        description_input = st.text_area(f"Step {i+1} Description", value=step['description'], key=f"description_{i}")
        edited_steps.append({"title": title_input, "description": description_input})
        
        # Add "Add Step" button after each step
        if st.button(f"Add Step after Step {i+1}"):
            edited_steps.insert(i+1, {"title": "", "description": ""})

        # Add "Delete Step" button to remove a step
        if st.button(f"Delete Step {i+1}"):
            edited_steps.pop(i)

    st.session_state['flow_chart_steps'] = edited_steps  # Update session state with edited steps

    # Render the flow chart HTML
    if st.button("Render Flow Chart"):
        html_generator = RenderHTML(
            name=name_input,
            flow_chart_steps=st.session_state['flow_chart_steps'],
            arrow_chart=arrow_chart,
            introduction=company_intro_input
        )
        html_output = html_generator.generate_html()
        components.html(html_output, height=800, scrolling=True)