import pandas as pd
import re


def extract_attendees(df):

    results = []

    for _, row in df.iterrows():

     phone = row.get("Phone Number", "")
     email = row.get("Email", "")
     allergies = row.get("If yes, please specify your dietary allergies", "")
     kayaking = row.get("Please indicate the number of participants for kayaking", "")
     boat = row.get("Please indicate the number of participants for Boat Tour", "")
     attendee_text = str(row.get("Attendee Information", "") or "")
     children_text = str(row.get("Children's Information", "") or "")

    # Extract adults
     main_pattern = re.search(r"First Name:\s*(.*?)\s*,\s*Last Name:\s*(.*?)\s*,\s*T-shirt Size:\s*(.*?)(?:\n|$)",
                              attendee_text,
                                re.IGNORECASE)

    # Extract additional adults (if any)
     adult_pattern = re.findall(
        r"First Name:\s*(.*?)\s*,\s*Last Name:\s*(.*?)\s*,\s*T-shirt Size:\s*(.*?)(?:\n|$)",
        attendee_text,
        re.IGNORECASE
    )

     remaining = adult_pattern[1:]

    # Extract children
     child_pattern = re.findall(
        r"Child's Full Name:\s*(.*?)\s*,\s*Age:\s*(.*?)\s*,\s*T-shirt Size:\s*(.*?)(?:\n|$)",
        children_text,
        re.IGNORECASE
    )

    # Add main adult (first one)
     results.append({
        "Type": "Adult",
        "Name": main_pattern.group(1).strip() + " " + main_pattern.group(2).strip(),
        "T-Shirt Size": main_pattern.group(3).strip(),
        "Child Age": "",
        "Kayaking": kayaking,
        "Boat Tour": boat,
        "Allergies": allergies,
        "Phone Number": phone,
        "Email": email

    })

    # Add additional adults
     for first_name, last_name, tshirt in remaining:
        results.append({
            "Type": "Adult",
            "Name": first_name.strip() + " " + last_name.strip(),
            "T-Shirt Size": tshirt.strip(),
            "Child Age": "",
            "Kayaking": "",
            "Boat Tour": "",
            "Allergies": "",
            "Phone Number": "",
            "Email": ""
        })

    # Add children
     for child_name, age, child_tshirt in child_pattern:
        results.append({
            "Type": "Child",
            "Name": child_name.strip(),
            "T-Shirt Size": child_tshirt.strip(),
            "Child Age": age.strip(),
            "Kayaking": "",
            "Boat Tour": "",
            "Allergies": "",
            "Phone Number": "",
            "Email": ""
        })

    output_df = pd.DataFrame(results)

    output_df.insert(
        0,
        "S.No",
        range(1, len(output_df) + 1)
    )

    return output_df