import os
from wsgiref import headers
import requests
import pandas as pd
import gspread

from msal import ConfidentialClientApplication
from google.oauth2.service_account import Credentials

from extractor import extract_attendees


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
#https://1drv.ms/x/c/a70c056bed6b35d2/IQAMuXMp45_sToR3w6XA0zQKAQHmfSjqZM_NOG8VOuoJRsE?e=hAuHne

# urls = f"https://graph.microsoft.com/v1.0/users/{user}/drive/root/search(q='GCA_2026_Camp.xlsx')"
# response = requests.get(urls, headers=headers)
# for item in response.json().get("value", []):
#     print(item["name"], "→", item["parentReference"]["path"])

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

print(
    f"Processed {len(output_df)} rows"
)


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

sheet = client.open(sheet_name).worksheet(
    "Adults_Children"
)

sheet.clear()

sheet.update(
    [output_df.columns.tolist()]
    + output_df.values.tolist()
)

print(
    "Google Sheet updated successfully"
)