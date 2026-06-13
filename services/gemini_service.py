import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")


def build_prompt(report_data: dict) -> str:
    return f"""
You are an HR analytics assistant. A manager wants insights about their team's performance.
Here is the team data for the {report_data['period']} period ({report_data['start_date']} to {report_data['end_date']}):

Total Employees: {report_data['total_employees']}

Attendance Summary (per employee):
{json.dumps(report_data['attendance'], indent=2)}

Task Summary (per employee):
{json.dumps(report_data['tasks'], indent=2)}

Performance Scores (per employee):
{json.dumps(report_data['performance'], indent=2)}

Please provide:
1. Overall team health summary
2. Top performers and why
3. Employees who may need support or attention
4. Attendance concerns if any
5. Task completion analysis
6. Actionable recommendations for the manager

Be concise, professional, and specific. Use the actual employee names from the data.
"""


def get_gemini_insights(report_data: dict) -> str:
    try:
        prompt = build_prompt(report_data)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating insights: {str(e)}"