import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =======================
# PROMPT TEMPLATES
# =======================

VIEW_PROMPT = """
Act as a Senior Data Architect.

Your task is to perform a deep-dive analysis of the following SQL VIEW definition and generate a comprehensive
"Technical Documentation & Lineage Report" for a new developer.

GOAL:
Ensure a developer with no prior knowledge of this system can understand the business logic,
data dependencies, and output structure within minutes.

IMPORTANT RULES:
- Do NOT suggest modifying, optimizing, or executing the SQL
- Explain the logic clearly in business + technical terms
- Assume the reader is new to the system

VIEW NAME:
{object_name}

SQL VIEW DEFINITION:
{object_sql}

DOCUMENTATION FORMAT (STRICT):

1. Executive Summary
2. Source Tables & Dependencies
3. Logical Flow
4. Field Dictionary
5. Performance & Scaling Notes
6. Example Usage
"""

PROC_PROMPT = """
Act as a Lead Database Engineer.

Perform a technical audit and generate a detailed
"Standard Operating Procedure (SOP) Document" for the following SQL Stored Procedure.

GOAL:
Create a maintenance-ready guide explaining exactly how the data state changes
when this procedure is executed.

IMPORTANT RULES:
- Do NOT rewrite or optimize SQL
- Do NOT suggest improvements
- Focus strictly on behavior, data impact, and operational understanding

PROCEDURE NAME:
{object_name}

SQL PROCEDURE DEFINITION:
{object_sql}

DOCUMENTATION FORMAT (STRICT):

1. Procedure Purpose
2. Input / Output Parameters
3. Execution Logic & Flow
4. Data Impact (CRUD Analysis)
5. Transaction & Error Handling
6. Dependency Map
7. Maintenance Warnings
"""


# =======================
# MAIN FUNCTION
# =======================

def generate_sql_documentation(object_name, object_type, object_sql):
    """
    Generates GenAI documentation for SQL Views and Stored Procedures
    """

    if object_type.lower() == "view":
        prompt = VIEW_PROMPT.format(
            object_name=object_name,
            object_sql=object_sql
        )

    elif object_type.lower() in ["procedure", "proc", "stored procedure"]:
        prompt = PROC_PROMPT.format(
            object_name=object_name,
            object_sql=object_sql
        )

    else:
        raise ValueError("Unsupported object type. Use 'view' or 'procedure'.")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": "You are an expert SQL documentation generator."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
