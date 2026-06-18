import requests

def get_mlbb_info(user_id: str, server_id: str):
    url = f"https://api.isan.eu.org/nickname/ml?id={user_id}&zone={server_id}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            return data.get("name")
        else:
            return "اکانت نامعتبره!"
    else:
        return f"Error {response.status_code}"

# تست
nickname = get_mlbb_info("393638382", "4050")
print("Nickname:", nickname)
