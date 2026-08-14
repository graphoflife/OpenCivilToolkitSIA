import json, requests
with open('data/project.json') as f:
    data = json.load(f)
req = {
    "plate": data["plates"][0],
    "materials": data["materials"]
}
res = requests.post('http://localhost:8080/api/plates/calculate', json=req)
print(res.status_code)
if res.status_code != 200:
    print(res.text)
else:
    print("SUCCESS")
