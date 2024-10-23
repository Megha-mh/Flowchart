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

def rephrase_business_activity(activity: str) -> str:
    """Rephrase the business activity to make it clearer and more formal."""
    if "website" in activity.lower() and "digital" in activity.lower():
        return "The business specializes in providing website development and digital services, offering tailored solutions to meet client needs."
    return activity  # Return as-is if no rephrasing is found.

class RenderHTML:
    def __init__(self, name, description, flow_chart_steps, arrow_chart, business_activity):
        self.name = name
        self.description = description  # New field for company description
        self.flow_chart_steps = flow_chart_steps if flow_chart_steps else []  # Ensure flow_chart_steps is a list
        self.arrow_chart = arrow_chart
        self.business_activity = business_activity  # The input business activity is directly passed

    def generate_flow_chart(self):
        """Generate the visual business flowchart with departments as nodes."""
        if not self.flow_chart_steps:
            return "<p>No flow chart steps available.</p>"

        # Example flowchart structure, connecting departments and steps
        flow_chart_html = """
        <div style="text-align: center; font-family: Arial, sans-serif;">
            <h4>Business Flow Chart</h4>
            <div style="display: flex; justify-content: space-around; align-items: center;">
                <!-- Sales Department -->
                <div style="border: 2px solid #0C6C98; padding: 20px; border-radius: 10px; width: 150px;">
                    Sales
                </div>
                <div style="flex-grow: 1; border-top: 2px solid #0C6C98; margin: 0 10px;"></div>
                <!-- Finance Department -->
                <div style="border: 2px solid #0C6C98; padding: 20px; border-radius: 10px; width: 150px;">
                    Finance
                </div>
                <div style="flex-grow: 1; border-top: 2px solid #0C6C98; margin: 0 10px;"></div>
                <!-- Delivery Department -->
                <div style="border: 2px solid #0C6C98; padding: 20px; border-radius: 10px; width: 150px;">
                    Delivery
                </div>
            </div>
            <div style="margin-top: 20px;">
                <div style="display: inline-block; padding: 5px 15px; border: 1px solid #0C6C98; border-radius: 5px; background-color: #D3D3D3;">
                    Sales Department receives customer order and sends invoice to Finance Department
                </div>
                <br>
                <div style="display: inline-block; padding: 5px 15px; border: 1px solid #0C6C98; border-radius: 5px; background-color: #D3D3D3; margin-top: 10px;">
                    Finance Department processes payment and informs Delivery Department
                </div>
                <br>
                <div style="display: inline-block; padding: 5px 15px; border: 1px solid #0C6C98; border-radius: 5px; background-color: #D3D3D3; margin-top: 10px;">
                    Delivery Department dispatches the product to the customer
                </div>
            </div>
        </div>
        """
        return flow_chart_html

    def generate_html(self):
        """Generate the complete HTML output including flow chart."""
        flow_chart_html = self.generate_flow_chart()

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
                
                <!-- Introduction Section with Company Description -->
                <div style="font-size: 0.9em;">
                    <p>{self.description}</p>
                </div>

                <!-- Flow Chart -->
                <div id="flow-chart">
                    {flow_chart_html}
                </div>

                <p style="margin-top: 100px">I hereby declare that the information is complete and best to my knowledge.</p>
                <p>Authorized Signatory (Sign & Stamp)</p>
            </div>

            <!-- Download button -->
            <button onclick="downloadPDF()">Download PDF</button>
        </body>
        </html>
        """
        return html_content

# Streamlit UI
st.title("Business Flow Chart Renderer")

# Input fields
name_input = st.text_input("Enter the name of the company:", "")
business_description_input = st.text_area("Enter the Company Description:")  # New input for company description
business_activity_input = st.text_area("Enter the Business Activity:")  # New input for business activity

# Button to generate flow chart steps
explanation = st.text_area("Step Explanation", "Step Explanation")
if st.button("Generate Flow Chart"):
    flow_chart_steps = generate_flow_chart_steps(explanation)
    st.session_state['flow_chart_steps'] = flow_chart_steps  # Store in session state

# Render the flow chart HTML
if st.button("Render Flow Chart"):
    html_generator = RenderHTML(
        name=name_input,
        description=business_description_input,  # Pass company description input
        flow_chart_steps=st.session_state['flow_chart_steps'],
        arrow_chart=None,  # Not needed in this version
        business_activity=business_activity_input  # Pass the business activity input
    )
    html_output = html_generator.generate_html()
    components.html(html_output, height=800, scrolling=True)
