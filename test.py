import json
from datetime import date
from pydantic import BaseModel
import streamlit as st
import streamlit.components.v1 as components

# Ensure session state is initialized
if 'flow_chart_steps' not in st.session_state:
    st.session_state['flow_chart_steps'] = []

class FlowChartStep(BaseModel):
    title: str
    description: str

def generate_flow_chart_steps(explanation: str):
    # Placeholder logic to simulate generation of flow chart steps
    return [
        {"title": "Step 1", "description": "This is the first step."},
        {"title": "Step 2", "description": "This is the second step."}
    ]

class RenderHTML:
    def __init__(self, name, flow_chart_steps, arrow_chart, business_activity):
        self.name = name
        self.flow_chart_steps = flow_chart_steps if flow_chart_steps else []  # Ensure flow_chart_steps is a list
        self.arrow_chart = arrow_chart
        self.business_activity = business_activity  # The input business activity is directly passed

    def generate_flow_chart(self):
        """Generate the flow chart HTML content."""
        flow_chart_html = ""
        for index, step in enumerate(self.flow_chart_steps):
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

    def generate_html(self):
        """Generate the complete HTML output including flow chart."""
        flow_chart_html = self.generate_flow_chart()

        # Add the html2pdf JavaScript for PDF generation
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
                    html2pdf().from(element).set({{
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
                    <p>Business Activity: {self.business_activity}</p>
                </div>
                
                <!-- Flow Chart -->
                <div id="flow-chart">
                    <h3>Procurement Process:</h3>
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 20px;">
                        {flow_chart_html}
                    </div>
                </div>
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
business_activity_input = st.text_area("Enter the Business Activity:")
arrow_chart = {}

st.subheader("Flow Chart Steps")
explanation = st.text_area("Step Explanation", "Step Explanation")

# Button to generate flow chart steps
if st.button("Generate Flow Chart"):
    flow_chart_steps = generate_flow_chart_steps(explanation)
    st.session_state['flow_chart_steps'] = flow_chart_steps  # Store in session state

# Render the flow chart HTML and generate PDF
if st.button("Render Flow Chart"):
    if 'flow_chart_steps' in st.session_state:
        html_generator = RenderHTML(
            name=name_input,
            flow_chart_steps=st.session_state['flow_chart_steps'],
            arrow_chart=arrow_chart,
            business_activity=business_activity_input  # Pass the business activity input
        )
        html_output = html_generator.generate_html()
        
        # Render the HTML with the JavaScript to the Streamlit app
        components.html(html_output, height=800, scrolling=True)
