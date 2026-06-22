import os
from wsgiref import headers
import requests
import pandas as pd
import gspread

from msal import ConfidentialClientApplication
from google.oauth2.service_account import Credentials

from extractor import extract_attendees, extract_tshirts


# =========================
# Create Google Credentials
# =========================

google_json = os.environ["GOOGLE_CREDENTIALS"]

with open("credentials.json", "w") as f:
    f.write(google_json)


# =========================
# Azure Credentials
# =========================

tenant_id = os.environ["AZURE_TENANT_ID"]
client_id = os.environ["AZURE_CLIENT_ID"]
client_secret = os.environ["AZURE_CLIENT_SECRET"]

authority = (
    f"https://login.microsoftonline.com/"
    f"{tenant_id}"
)

app = ConfidentialClientApplication(
    client_id,
    authority=authority,
    client_credential=client_secret
)

token_result = app.acquire_token_for_client(
    scopes=["https://graph.microsoft.com/.default"]
)

if "access_token" not in token_result:
    raise Exception(
        f"Unable to get token: {token_result}"
    )

access_token = token_result["access_token"]


# =========================
# Download Excel from OneDrive
# =========================

# user = os.environ["ONEDRIVE_USER"]

# FILE_PATH = "Documents/python_workspace/GCA_2026_Camp.xlsx"

# url = (
#     f"https://graph.microsoft.com/v1.0/"
#     f"users/{user}/drive/root:"
#     f"/{FILE_PATH}:/content"
# )
url = "https://1drv.ms/x/c/a70c056bed6b35d2/IQAMuXMp45_sToR3w6XA0zQKAQHmfSjqZM_NOG8VOuoJRsE?e=Lese5D&download=1"

response = requests.get(url, allow_redirects=True)

response.raise_for_status()

with open("camp.xlsx", "wb") as f:
    f.write(response.content)

print("Downloaded latest Excel file")


# =========================
# Process Excel
# =========================

df = pd.read_excel("camp.xlsx")

output_df = extract_attendees(df)
tshirt_df = extract_tshirts(output_df)

print(
    f"Processed {len(output_df)} rows"
)
print(f"Extracted {len(tshirt_df)} T-shirt entries")


# =========================
# Upload To Google Sheets
# =========================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

client = gspread.authorize(creds)

sheet_name = os.environ[
    "GOOGLE_SHEET_NAME"
]
workbook = client.open(sheet_name)
sheet = workbook.worksheet("Adults_Children")
sheet.clear()

sheet.update(
    [output_df.columns.tolist()]
    + output_df.values.tolist()
)
print("Adults_Children sheet updated successfully")

# --- T-Shirts sheet ---
try:
    tshirt_sheet = workbook.worksheet("T-Shirts")
except gspread.exceptions.WorksheetNotFound:
    tshirt_sheet = workbook.add_worksheet(
        title="T-Shirts",
        rows=len(tshirt_df) + 10,
        cols=10
    )
    print("Created new 'T-Shirts' worksheet")

tshirt_sheet.clear()
tshirt_sheet.update(
    [tshirt_df.columns.tolist()]
    + tshirt_df.values.tolist()
)
print("T-Shirts sheet updated successfully")

print(
    "Google Sheet updated successfully"
)