import os
from fpdf import FPDF
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def generate_maintenance_report(data):
    """
    Generates text analysis using Groq LLM.
    Returns: (report_text, error_message)
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None, "GROQ_API_KEY not found in .env file."

    try:
        llm = ChatGroq(
            temperature=0.7,
            model_name="llama-3.1-8b-instant",
            groq_api_key=api_key
        )
        
        # Prompt AI to ONLY analyze, not rewrite data
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a senior jet engine maintenance engineer. Provide a concise analysis and recommendations based on the provided status. Do NOT repeat the numbers, just analyze the situation."),
            ("human", "Analyze engine status:\nState: {state}\nRUL: {rul}\nTemp: {temp}\nPress: {press}\nVib: {vib}")
        ])

        chain = prompt | llm
        response = chain.invoke({
            "state": data.get('state', 'UNKNOWN'),
            "rul": f"{data.get('rul', 0):.2f}",
            "temp": f"{data.get('temperature', 0):.2f}",
            "press": f"{data.get('pressure', 0):.2f}",
            "vib": f"{data.get('vibration', 0):.2f}"
        })
        
        # Construct Final Text (Injecting Correct Values Manually)
        final_report = f"""
**SENSOR DATA SNAPSHOT**
- State: {data.get('state')}
- RUL: {data.get('rul'):.2f} Cycles
- Temperature: {data.get('temperature'):.2f}
- Pressure: {data.get('pressure'):.2f}
- Vibration: {data.get('vibration'):.2f}

**AI ANALYSIS**
{response.content}
"""
        return final_report, None

    except Exception as e:
        return None, str(e)

def create_pdf_file(report_text, data, save_dir):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="ENGINE HEALTH REPORT", ln=1, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=report_text)
    
    # Use the passed directory
    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    path = os.path.join(save_dir, filename)
    pdf.output(path)
    return path