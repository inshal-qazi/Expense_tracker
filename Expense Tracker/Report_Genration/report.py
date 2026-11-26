import requests
import json
import os
import io
from datetime import date
from google import genai
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


# # 1. INITIALIZE GEMINI CLIENT

Client = genai.Client(api_key="Gemn api key")


# # 2. OAUTH 2.0 AUTHENTICATION FLOW

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

creds = None

#Step A: Check if saved tokens exist
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

# Step B: If credentials don't exist or are invalid, handle login/refresh
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception:
            creds = None

    if not creds or not creds.valid:
        # Load secrets from auth.json and open browser for user consent
        flow = InstalledAppFlow.from_client_secrets_file("auth.json", SCOPES)
        creds = flow.run_local_server(port=0)

    # Save authorized credentials to token.json for future runs
    with open("token.json", "w") as token:
        token.write(creds.to_json())

# Step C: Build Google API Services
docs_service = build("docs", "v1", credentials=creds)
drive_service = build("drive", "v3", credentials=creds)

#PROVIDING AND CONNECTING APP SCRPIT AND REPLCING PLACE HPLDER NESSCARY INFO
report_date=date.today().strftime("%B %Y")
pdf_title = f"{report_date} Financial Report.pdf"
url = "https://script.google.com/macros/s/AKfycbysaMNeZ6y6BbV_sqM6LnKmQeJIn6twWOX9uRve_XwtIyTBtYzfgRWCMNP6kUBZK8_Rig/exec"
dashboard_responce=requests.get(url + "?api=dashboard")
dashboard_data = dashboard_responce.json()
dashboard_json = json.dumps(dashboard_data, indent=2)



# 3. GEMINI REPORT GENERATION

interaction = Client.interactions.create(
    model="gemini-3-flash-preview",
    input=f"""
You are a financial data analysis assistant.

Below is the actual dashboard data calculated from the user's Google Sheet.
This data is the ONLY source of financial facts for this report.

==============================
DASHBOARD DATA
==============================

{dashboard_json}

==============================
IMPORTANT DATA RULES
==============================

1. Use the supplied dashboard data as the single source of truth.

2. Do NOT invent, assume, or create financial data that is not present
   in the dashboard data.

3. Do NOT use hardcoded financial values from this prompt.

4. You may calculate percentages, ratios, comparisons, and totals ONLY
   when they can be mathematically derived from the supplied data.

5. When calculating percentages, verify the calculation carefully.

6. Do not double-count categories or financial components.

7. Do not introduce income because income is not provided.

8. Do not introduce savings because savings are not provided.

9. Do not introduce historical months or trends because historical data
   is not provided.

10. Do not introduce transactions that are not present in the supplied data.

11. Do not convert Pakistani Rupees into another currency.

12. Use "Rs." for monetary values.

13. The fields inside the dashboard data may change from month to month.
    Always analyze the actual values supplied rather than assuming
    specific numbers.

==============================
OUTPUT REQUIREMENTS
==============================

Your final response MUST be a valid JSON object.

DO NOT return Markdown.

DO NOT use Markdown headings.

DO NOT wrap the JSON in ```json or ``` code fences.

DO NOT write anything before the JSON.

DO NOT write anything after the JSON.

The JSON must contain EXACTLY these 8 keys:

{{
  "executive_summary": "",
  "financial_overview": "",
  "spending_patterns": "",
  "discretionary_analysis": "",
  "food_health_audit": "",
  "areas_attention": "",
  "recommendations": "",
  "conclusion": ""
}}

Each key represents one section of the financial report.

==============================
SECTION REQUIREMENTS
==============================

1. executive_summary

Write a concise professional overview of the supplied financial data.

Include, when available:
- Total spending
- Number of transactions
- Good expenses
- Bad expenses
- Debt repayment
- Main spending categories
- One or two important observations

Do not mention income or savings.

Use only values from the supplied dashboard data or calculations
directly derived from it.

Return only the content of this section as a JSON string.

--------------------------------

2. financial_overview

Explain the relationship between:
- Total spending
- Good expenses
- Bad expenses
- Debt repayment

Calculate useful percentages when they can be directly derived
from the supplied data.

For example:
- Good expenses as a percentage of total spending
- Bad expenses as a percentage of total spending
- Debt repayment as a percentage of total spending

Make sure every percentage is mathematically correct.

Do not double-count financial components.

Return only the content of this section as a JSON string.

--------------------------------

3. spending_patterns

Analyze the spending categories contained in:

dashboard_data["categories"]

Identify the largest spending categories.

Calculate their percentage of total spending when useful.

Explain what the distribution shows.

Do not claim a reason for the spending unless the supplied data
supports that conclusion.

Do not assume that the category names or their values will remain
the same in future reports.

Return only the content of this section as a JSON string.

--------------------------------

4. discretionary_analysis

Analyze the items contained in:

dashboard_data["topBadItems"]

Use the actual item names, prices, and categories supplied by the
dashboard.

Identify which items contribute most to the amount classified as
bad/discretionary spending.

Do not invent additional items.

Do not automatically describe every discretionary item as
unnecessary.

Return only the content of this section as a JSON string.

--------------------------------

5. food_health_audit

Analyze the food-related values contained in:

dashboard_data["food"]

Compare the available food categories such as healthy and junk
spending when those fields are present.

Calculate percentages when they can be mathematically derived
from the supplied food data.

Discuss only the spending pattern shown by the data.

Do not claim that the user has a health problem.

Do not make medical or nutritional diagnoses.

Return only the content of this section as a JSON string.

--------------------------------

6. areas_attention

Identify 3 areas that deserve attention based ONLY on the supplied
dashboard data.

For each area:

- State the factual observation.
- Explain its possible financial significance.
- Clearly identify anything that cannot be determined from the data.

Do not use unsupported claims.

Do not use words such as "worst" unless directly supported by
the supplied data.

Return only the content of this section as a JSON string.

--------------------------------

7. recommendations

Give practical recommendations directly connected to the supplied
dashboard data.

Focus on areas such as:

- Controlling discretionary spending where appropriate.
- Monitoring food spending.
- Reviewing large spending categories.
- Reviewing the "Others" category when it represents a significant
  portion of spending.
- Understanding debt repayment spending.
- Maintaining awareness of spending distribution.

Do NOT invent a specific monthly budget.

Do NOT recommend a specific savings amount because income is not
provided.

Every recommendation must be connected to an observation in the
supplied data.

Return only the content of this section as a JSON string.

--------------------------------

8. conclusion

Write a short professional conclusion.

Summarize the main financial observations and the areas that should
be reviewed in the next reporting period.

Do not introduce new financial facts.

Return only the content of this section as a JSON string.

==============================
FINAL ACCURACY CHECK
==============================

Before returning the JSON, internally verify:

1. Every numerical statement comes from the supplied dashboard data
   or is mathematically derived from it.

2. No financial information has been invented.

3. No income has been introduced.

4. No savings amount has been introduced.

5. No historical month or unsupported trend has been introduced.

6. No transaction has been invented.

7. No currency conversion has been performed.

8. All monetary values use Rs.

9. All calculated percentages are mathematically correct.

10. Exactly 8 required keys are present.

11. No additional keys are present.

12. Every key contains the appropriate section content.

13. The final response contains ONLY the JSON object.

Return the JSON object now.
""",
)

output = interaction.output_text
gemini_report = json.loads(output)
#PLACEHOLDER FOE GEMNI OUTPUT

report_data = {
    
    "{{REPORT_DATE}}": report_date,
    "{{DASHBOARD_LINK}}": url,
    "{{TOTAL_SPENT}}":str(dashboard_data["kpis"]['total']),
   "{{GOOD_EXPENSES}}":str(dashboard_data["kpis"]['good']),
    "{{BAD_EXPENSES}}":str(dashboard_data["kpis"]['bad']),
    "{{DEBT}}":str(dashboard_data["kpis"]['debt']),
    
    
    
    "{{EXECUTIVE_SUMMARY}}": gemini_report["executive_summary"],
    "{{FINANCIAL_OVERVIEW}}": gemini_report["financial_overview"],
    "{{SPENDING_PATTERNS}}": gemini_report["spending_patterns"],
    "{{DISCRETIONARY_ANALYSIS}}": gemini_report["discretionary_analysis"],
    "{{FOOD_HEALTH_AUDIT}}": gemini_report["food_health_audit"],
    "{{AREAS_ATTENTION}}": gemini_report["areas_attention"],
    "{{RECOMMENDATIONS}}": gemini_report["recommendations"],
    "{{CONCLUSION}}": gemini_report["conclusion"],
}


# # 4. DRIVE FILE COPY & DOCS UPDATE

template_id = "1LZnwQ7SXSVfPBB8K1nrwZuBmrU4BbIAM9EobqKJXDVk"

new_document = (
    drive_service.files()
    .copy(
        fileId=template_id,
        body={
            "name": "September Report 2026",
            "parents": [
                "16SiUBJxfJNMIC_pNFFoLQEo9TJYEBPO8"
            ],  # Directs file to your shared folder
        },
    )
    .execute()
)

document_id = new_document["id"]
# print("NEW document ID:", document_id)

requests = []
for placeholder, text in report_data.items():
    requests.append(
        {
            "replaceAllText": {
                "containsText": {"text": placeholder, "matchCase": True},
                "replaceText": text,
            }
        }
    )

docs_service.documents().batchUpdate(
    documentId=document_id, body={"requests": requests}
).execute()

pdf = drive_service.files().export(
    fileId=document_id,
    mimeType="application/pdf"
).execute()

# 7. UPLOAD PDF DIRECTLY TO GOOGLE DRIVE FOLDER
media = MediaIoBaseUpload(io.BytesIO(pdf), mimetype="application/pdf")
pdf_metadata = {"name": pdf_title, "parents": ["16SiUBJxfJNMIC_pNFFoLQEo9TJYEBPO8"]}

uploaded_pdf = (
    drive_service.files()
    .create(body=pdf_metadata, media_body=media, fields="id")
    .execute()
)

print(
    f"PDF report successfully generated and saved to Drive! File ID:"
    f" {uploaded_pdf.get('id')}"
)

# 8. CLEANUP: DELETE TEMPORARY GOOGLE DOC FROM DRIVE
drive_service.files().delete(fileId=document_id).execute()
print("Temporary Google Doc copy cleaned up from Drive.")


print("PDF successfully created!")
print("Report is successfully added to  pdf!")
