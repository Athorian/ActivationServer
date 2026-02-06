import requests

url = "http://127.0.0.1:5000/activate"
payload = {
    "key": "KJP-0385-2180-7115-ADE9",
    "machine_id": "TEST-PC"
}

response = requests.post(url, json=payload)
print(response.text)
