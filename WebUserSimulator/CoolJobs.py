import requests
from pathlib import Path

cv_path = Path(__file__).parent / "CVs" / "picture_ehub.png"

url = "https://www.cooljobs.eu/cz/pos/1001.html?action=SubmitApplication"

# formulářová data
data = {
    "jmeno": "ss",
    "email": "a.b@gmail.com",
    "telefon": "+420666444555",
    "poznamka": "fadfa",
    "souhlas": "on",
    "requestid": "41779",
}

# soubor CV
files = {
    "cv": ("cv.pdf", open(cv_path, "rb"), "application/pdf")
}

# session kvůli cookies (často nutné)
session = requests.Session()

response = session.post(url, data=data, files=files)

print("STATUS:", response.status_code)
print("OK:", response.ok)
print("RESPONSE TEXT PREVIEW:")
print(response.text[:500])
