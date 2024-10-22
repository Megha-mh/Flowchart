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

def modify_input_using_chatgpt(prompt: str) -> str:
    """
    This function modifies user input using Groq/ChatGPT to rephrase or enhance it.
    """
    try:
        response = groq.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that rephrases and enhances text. Please rephrase and enhance the following input to sound more professional and polished.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.7,
        )
        # Return the enhanced text from the response
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return prompt

def sanitize_input(text: str, replace_commas: bool = False) -> str:
    """
    This function sanitizes the input text, removing extra spaces and optionally replacing commas with line breaks.
    """
    text = text.strip()  # Remove leading/trailing whitespace
    if replace_commas:
        text = text.replace(",", "<br>")  # Replace commas with line breaks for better readability
    return text

class RenderHTML:
    def __init__(self, name, description, flow_chart_steps, arrow_chart):
        self.name = name
        self.description = description  # This will be dynamically inserted
        self.flow_chart_steps = flow_chart_steps
        self.arrow_chart = arrow_chart

    def modify_inputs_using_gpt(self):
        # Modify the company name (capitalize first letter of each word)
        self.name = modify_input_using_chatgpt(f"Rephrase the company name: {self.name}")
        
        # Modify the description using GPT (enhance or rephrase it)
        self.description = modify_input_using_chatgpt(f"Enhance and polish the company description: {self.description}")

        # Modify arrow chart titles and content by enhancing or rephrasing them using GPT
        for key in self.arrow_chart:
            if "title" in key or "content" in key:
                self.arrow_chart[key] = modify_input_using_chatgpt(f"Rephrase this content to sound more professional: {self.arrow_chart[key]}")

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
                        <h4 style="margin: 5px 0; color: #333;">{sanitize_input(step['title'])}</h4>
                        <div style="margin-top: 5px; font-size: 0.9em; color: #555; text-align: left;">
                            {sanitize_input(step['description']) if isinstance(step['description'], str) else str(step['description'])}
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
            sanitize_input(self.arrow_chart.get('title1', '')),
            sanitize_input(self.arrow_chart.get('title2', '')),
            sanitize_input(self.arrow_chart.get('title3', '')),
            sanitize_input(self.arrow_chart.get('title4', ''))
        ]
        grey_box_content = [
            sanitize_input(self.arrow_chart.get('content1', ''), replace_commas=True),
            sanitize_input(self.arrow_chart.get('content2', ''), replace_commas=True),
            sanitize_input(self.arrow_chart.get('content3', ''), replace_commas=True),
            sanitize_input(self.arrow_chart.get('content4', ''), replace_commas=True)
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
                            {grey_box_content[i]}
                        </div>
                        <div style="width: 0; height: 0; border-top: 80px solid transparent; border-bottom: 80px solid transparent; border-left: 70px solid #D3D3D3;"></div>
                    </div>
                """
        return category_chart_html

    def generate_html(self):
        # Apply modifications to inputs using GPT
        self.modify_inputs_using_gpt()

        flow_chart_html = self.generate_flow_chart()
        arrow_chart_html = self.generate_arrow_chart()

        # Add page break after arrow chart if arrow_chart_html exists
        arrow_chart_with_page_break = f"""
        <div style="page-break-after: always;">
            {arrow_chart_html}
        </div>
        """ if arrow_chart_html else ""

        # Generate dynamic introduction based on modified description input
        introduction = f"""
        <p>The "{sanitize_input(self.name)}" specializes in {sanitize_input(self.description)}. This includes managing operations in several areas and ensuring the smooth execution of business processes. The company is focused on {sanitize_input(self.description)} to diversify its revenue streams and grow its market share.</p>
        """

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
                <h3 style="margin-top: 20px; text-align: center;">{sanitize_input(self.name)}</h3>
                <h5>Date: {date.today().strftime("%d/%m/%Y")}</h5>
                <h4>Subject: Business Flow Chart</h4>
                
                <!-- Dynamic Introduction -->
                {introduction}

                <!-- Arrow Chart with Page Break -->
                {arrow_chart_with_page_break}  <!-- This will have a page break after arrow chart -->
                
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
name_input = st.text_input("Enter the name of the company:", "One Planet Travel and Events LLC")
description_input = st.text_area("Enter the company description:", "a diversified business model centered around trading and consulting services, focused on heavy plant and equipment, textiles, and beverages")

input_arrowchart_content1 = st.text_input('Enter the content For BUSINESS ACTIVITY', key="input_arrowchart_content1")
input_arrowchart_content2 = st.text_input('Billing system (how payment is collected from customers)', key="input_arrowchart_content2")
input_arrowchart_content3 = st.text_input('Enter the content For PLACE OF SUPPLY', key="input_arrowchart_content3")
input_arrowchart_content4 = st.text_input('Enter the content For EXPENSES AND COST OF SALES', key="input_arrowchart_content4")

arrow_chart = {
    "title1": "BUSINESS",
    "title2": "Billing System",
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
            edited_steps.insert(i+1, {"title": "", "description": ""})

        # Add "Delete Step" button to remove a step
        if st.button(f"Delete Step {i+1}"):
            edited_steps.pop(i)

    st.session_state['flow_chart_steps'] = edited_steps  # Update session state with edited steps

    # Render the flow chart HTML
    if st.button("Render Flow Chart"):
        html_generator = RenderHTML(
            name=name_input,
            description=description_input,  # Pass the dynamic description input
            flow_chart_steps=st.session_state['flow_chart_steps'],
            arrow_chart=arrow_chart
        )
        html_output = html_generator.generate_html()
        components.html(html_output, height=800, scrolling=True)
