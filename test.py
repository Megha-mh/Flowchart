import streamlit as st
from datetime import date
import streamlit.components.v1 as components

class RenderHTML:
    def __init__(self, name, description, business_activity, billing_system, place_of_supply, expenses_costs, flow_chart_steps):
        self.name = name
        self.description = description
        self.business_activity = business_activity
        self.billing_system = billing_system
        self.place_of_supply = place_of_supply
        self.expenses_costs = expenses_costs
        self.flow_chart_steps = flow_chart_steps

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
                            {step['description']}
                        </div>
                    </div>
                </div>
            """
        return flow_chart_html

    def generate_html(self):
        # Generate the dynamic flowchart based on the provided content
        flow_chart_html = self.generate_flow_chart()

        # Create the HTML structure
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
                            filename: '{self.name}_business_flow_chart.pdf',
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

                <!-- Introduction -->
                <div style="margin-bottom: 40px;">
                    <p>{self.description}</p>
                </div>

                <!-- Business Details -->
                <div style="margin-bottom: 40px;">
                    <h4>Business Activity</h4>
                    <p>{self.business_activity}</p>
                    <h4>Billing System</h4>
                    <p>{self.billing_system}</p>
                    <h4>Place of Supply</h4>
                    <p>{self.place_of_supply}</p>
                    <h4>Expenses and Costs</h4>
                    <p>{self.expenses_costs}</p>
                </div>

                <!-- Flow Chart -->
                <div id="flow-chart">
                    <h4>Procurement Process:</h4>
                    {flow_chart_html}
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

# Input fields for the content
name_input = st.text_input("Enter the name of the company:", "Zenith Digital")
description_input = st.text_area("Enter the company description:", "Zenith Digital is a leading digital marketing agency that has been helping businesses of all sizes succeed online. With years of experience and a team of expert strategists, designers, and developers, we craft tailored solutions to drive measurable results.")
business_activity_input = st.text_input('Enter the content For BUSINESS ACTIVITY:', "It’s mainly website and digital services")
billing_system_input = st.text_input('Billing system (how payment is collected from customers):', "Through bank transfers, we submit the invoices and we get paid 30 days via bank transfer after submitting the invoice")
place_of_supply_input = st.text_input('Enter the content For PLACE OF SUPPLY:', "Saudi")
expenses_costs_input = st.text_input('Enter the content For EXPENSES AND COST OF SALES:', "Developers, tools and softwares, employees")

st.subheader("Flow Chart Steps")
flow_chart_steps_input = st.text_area("Step Explanation", """Zenith Digital is a leading digital marketing agency that has been helping businesses of all sizes succeed online. With years of experience and a team of expert strategists, designers, and developers, we craft tailored solutions to drive measurable results.
Digital Marketing: Comprehensive solutions to boost your online presence and drive traffic, leads,
and sales Social Media Marketing: Engaging content, targeted campaigns, and community management to amplify your brand's social impact. Search Engine Optimization (SEO): Data-driven strategies to improve your website's visibility and
organic search rankings.""")

# Button to generate the flowchart
if st.button("Generate Flow Chart"):
    flow_chart_steps = [
        {"title": "Digital Marketing", "description": "Comprehensive solutions to boost your online presence and drive traffic, leads, and sales."},
        {"title": "Social Media Marketing", "description": "Engaging content, targeted campaigns, and community management to amplify your brand's social impact."},
        {"title": "Search Engine Optimization (SEO)", "description": "Data-driven strategies to improve your website's visibility and organic search rankings."}
    ]

    # Generate the flowchart
    html_generator = RenderHTML(
        name=name_input,
        description=description_input,
        business_activity=business_activity_input,
        billing_system=billing_system_input,
        place_of_supply=place_of_supply_input,
        expenses_costs=expenses_costs_input,
        flow_chart_steps=flow_chart_steps
    )
    html_output = html_generator.generate_html()
    components.html(html_output, height=800, scrolling=True)
