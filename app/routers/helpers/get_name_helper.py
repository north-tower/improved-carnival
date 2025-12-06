import pdfplumber as pr
import re

def extract_client_name(pdf_file):
    with pr.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"

    # Extract customer name and mobile number using regex
    name_match = re.search(r"Customer Name:\s+(.+)", text)
    number_match = re.search(r"Mobile Number:\s+(\d+)", text)

    customer_name = name_match.group(1) if name_match else "Not Found"
    mobile_number = number_match.group(1) if number_match else "Not Found"

    return {
        'customer_name': customer_name,
        'mobile_number': mobile_number
    }