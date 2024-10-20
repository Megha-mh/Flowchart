import json
from datetime import date
from pydantic import BaseModel
import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
from typing import List
import os

# Fetching the API key from the environment variable
groq_api_key = os.getenv("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")

# Initializing the Groq object with the API key
groq = Groq(api_key=groq_api_key)

class FlowChartStep(BaseModel):
    title: str
    description: str

def generate_flow_chart_steps(explanation: str) -> List[FlowChartStep]:
    try:
        chat_completion = groq.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Please provide a in very detailed step-by-step guide with 6 to 10 steps. Each step should have a title and a description, description shall include some key points in and it shall have around 4-5 points for each title in description detailed line without new line. Make at least 10 sentences.\n"
                                f"The JSON object must use the schema: {json.dumps(FlowChartStep.model_json_schema(), indent=2)}",
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
        steps = json.loads(chat_completion.choices[0].message.content)
        return steps['steps']
    except Exception as e:
        st.error('No input given')
        return []

class RenderHTML:
    def __init__(self, name, flow_chart_steps, customer_cities, supplier_cities, arrow_chart):
        self.name = name
        self.flow_chart_steps = flow_chart_steps
        self.customer_cities = customer_cities
        self.supplier_cities = [city.strip() for city in supplier_cities if city.strip()]  # Filter out empty or whitespace-only entries
        self.arrow_chart = arrow_chart

    def generate_flow_chart(self):
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
                            {step['description'].replace('*', '') if isinstance(step['description'], str) else str(step['description']).replace('*', '').replace('[', '').replace(']', '')}
                        </div>
                    </div>
                </div>
            """
        return flow_chart_html

    def generate_arrow_chart(self):
        # Check if all arrow chart fields are blank
        if all(not self.arrow_chart.get(key).strip() for key in ['title1', 'title2', 'title3', 'title4', 'content1', 'content2', 'content3', 'content4']):
            return ""  # If all fields are blank, return an empty string (i.e., skip rendering)

        blue_box_content = [
            self.arrow_chart.get('title1', ''),
            self.arrow_chart.get('title2', ''),
            self.arrow_chart.get('title3', ''),
            self.arrow_chart.get('title4', '')
        ]
        grey_box_content = [
            self.arrow_chart.get('content1', ''),
            self.arrow_chart.get('content2', ''),
            self.arrow_chart.get('content3', ''),
            self.arrow_chart.get('content4', '')
        ]

        category_chart_html = ""
        for i in range(4):
            if blue_box_content[i].strip() or grey_box_content[i].strip():  # Only render if there's valid content
                category_chart_html += f"""
                    <div style="display: flex; margin-bottom:20px; align-items: center;">
                        <div style="background-color: #0C6C98; width: 190px; height: 80px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; padding-left: 5px; font-weight: bold;">
                            {blue_box_content[i]}
                        </div>
                        <div style="width: 230px; height: 130px; background-color: #D3D3D3; margin-left: 0px; display: flex; align-items: center; justify-content: flex-start; color: black; font-size: 12px; padding-left: 10px; line-height: 1.5;">
                            {grey_box_content[i].replace(',', '<br>')}
                        </div>
                        <div style="width: 0; height: 0; border-top: 80px solid transparent; border-bottom: 80px solid transparent; border-left: 70px solid #D3D3D3;"></div>
                    </div>
                """
        return category_chart_html

    def generate_city_html(self):
        customer_cities_html = "".join([f"<li style='margin: 2px 0; font-size: 12px;'>{city}</li>" for city in self.customer_cities])
        supplier_cities_html = "".join([f"<li style='margin: 2px 0; font-size: 12px;'>{city}</li>" for city in self.supplier_cities]) if self.supplier_cities else ""
        return customer_cities_html, supplier_cities_html

    def generate_html(self):
        flow_chart_html = self.generate_flow_chart()
        arrow_chart_html = self.generate_arrow_chart()
        customer_cities_html, supplier_cities_html = self.generate_city_html()

        # Check if supplier cities exist and render accordingly
        supplier_section_html = ""
        if supplier_cities_html:  # Only render supplier section if there are supplier cities
            supplier_section_html = f"""
            <h4 style="page-break-inside: avoid;">Location of Suppliers:</h4>
            <ul>{supplier_cities_html}</ul>
            """

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
                            html2canvas: {{ scale: 2 }},
                            jsPDF: {{ format: 'a4', orientation: 'portrait' }}
                        }})
                        .save();
                }}
            </script>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 210mm; margin: 0 auto;">
            <div id="pdf-content" style="padding: 50px;">
                <h3 style="margin-top: 20px; text-align: center;">{self.name}</h3>
                <h5>Date: {date.today().strftime("%d/%m/%Y")}</h5>
                <h4>Subject: Business Flow Chart</h4>
                <div style="font-size: 0.9em;">
                    <p>The "{self.name}" a diversified business model centered around trading and consulting services. Primarily focused on heavy plant and equipment, the company sources machinery from Europe and oversees the logistics of installation and dismantling projects across Africa. This includes full-scale project management, ensuring smooth execution of industrial projects. Alongside these services, the company expands its reach by trading in textiles, foodstuffs, and beverages, providing a broad range of offerings that support business growth and diversified revenue streams.<p>
                </div>
                
                <!-- Arrow Chart with Page Break -->
                {arrow_chart_with_page_break}  <!-- This will have a page break after arrow chart -->
                
                <!-- Flow Chart -->
                <div id="flow-chart">
                    <h3>Procurement Process:</h3>
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 20px;">
                        {flow_chart_html}
                    </div>
                </div>
                
                <!-- Cities -->
                <h4 style="page-break-inside: avoid;">Location of Customers: Outside UAE</h4>
                <ul>{customer_cities_html}</ul>

                <!-- Supplier section, only shown if supplier cities are provided -->
                {supplier_section_html}
                
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
name_input = st.text_input("Enter the name of the company:", "One Planet Travel and Events LLC")
cities_input = st.text_input("Enter the names of cities (separated by commas):", "Serbia, Macedonia, Bosnia, Croatia")
supplier_input = st.text_input("Enter the names of supplier cities (separated by commas):", "")
input_arrowchart_content1 = st.text_input('Enter the content For BUSINESS ACTIVITY', key="input_arrowchart_content1")
input_arrowchart_content2 = st.text_input('Enter the content For CUSTOMERS', key="input_arrowchart_content2")
input_arrowchart_content3 = st.text_input('Enter the content For PLACE OF SUPPLY', key="input_arrowchart_content3")
input_arrowchart_content4 = st.text_input('Enter the content For EXPENSES AND COST OF SALES', key="input_arrowchart_content4")

arrow_chart = {
    "title1": "BUSINESS",
    "title2": "CUSTOMERS",
    "title3": "PLACE OF SUPPLY",
    "title4": "EXPENSES AND COST OF SALES",
    "content1": input_arrowchart_content1,
    "content2": input_arrowchart_content2,
    "content3": input_arrowchart_content3,
    "content4": input_arrowchart_content4
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
            edited_steps.append({"title": "", "description": ""})
    
    st.session_state['flow_chart_steps'] = edited_steps  # Update session state with edited steps

    # Render the flow chart HTML
    if st.button("Render Flow Chart"):
        html_generator = RenderHTML(
            name=name_input,
            flow_chart_steps=st.session_state['flow_chart_steps'],
            customer_cities=cities_input.split(','), 
            supplier_cities=supplier_input.split(','),  # If no input, this will be an empty list
            arrow_chart=arrow_chart
        )
        html_output = html_generator.generate_html()
        components.html(html_output, height=800, scrolling=True)
