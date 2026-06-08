import pandas as pd
import re


def extract_attendees(df):

    results = []

    for _, row in df.iterrows():

        phone = row.get("Phone Number", "")
        email = row.get("Email", "")
        allergies = row.get(
            "If yes, please specify your dietary allergies",
            ""
        )

        attendee_text = str(
            row.get("Attendee Information", "") or ""
        )

        children_text = str(
            row.get("Children's Information", "") or ""
        )

        # Adults
        adult_pattern = re.findall(
            r"First Name:\s*(.*?)\s*,\s*Last Name:\s*(.*?)\s*,\s*T-shirt Size:\s*(.*?)(?:\n|$)",
            attendee_text,
            re.IGNORECASE
        )

        # Children
        child_pattern = re.findall(
            r"Child's Full Name:\s*(.*?)\s*,\s*Age:\s*(.*?)\s*,\s*T-shirt Size:\s*(.*?)(?:\n|$)",
            children_text,
            re.IGNORECASE
        )

        for first_name, last_name, tshirt in adult_pattern:

            results.append({
                "Type": "Adult",
                "First Name": first_name.strip(),
                "Last Name": last_name.strip(),
                "Phone Number": phone,
                "Email": email,
                "T-Shirt Size": tshirt.strip(),
                "Child Name": "",
                "Child Age": "",
                "Child T-Shirt Size": "",
                "Allergies": allergies
            })

        for child_name, age, tshirt in child_pattern:

            results.append({
                "Type": "Child",
                "First Name": "",
                "Last Name": "",
                "Phone Number": phone,
                "Email": email,
                "T-Shirt Size": "",
                "Child Name": child_name.strip(),
                "Child Age": age.strip(),
                "Child T-Shirt Size": tshirt.strip(),
                "Allergies": allergies
            })

    output_df = pd.DataFrame(results)

    output_df.insert(
        0,
        "S.No",
        range(1, len(output_df) + 1)
    )

    return output_df