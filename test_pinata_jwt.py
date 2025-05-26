import os, requests
from dotenv import load_dotenv

load_dotenv()
jwt = os.getenv("PINATA_JWT")
headers = {
    "Authorization": f"Bearer {jwt}",
    "Content-Type": "application/json"
}
resp = requests.post(
    "https://api.pinata.cloud/pinning/pinJSONToIPFS",
    headers=headers,
    json={"hello": "world"}
)
print("Status:", resp.status_code)
print("Body:", resp.text)
