import requests

API_URL = "http://localhost:5000"


def translate_text(text, language):
    params = {"q": text, "source": language, "target": "ja", "format": "text"}
    r = requests.post(f"{API_URL}/translate", data=params)
    if r.status_code == 200:
        return r.json()["translatedText"]
    else:
        print(f"Libretranslate translate_text error: {r.status_code}")


def get_language():
    r = requests.get(f"{API_URL}/languages")
    formatted_data = {'Auto': 'Auto'}
    for item in r.json():
        if 'ja' in item['targets']:
            formatted_data[item['name']] = item['code']
        else:
            pass

    if r.status_code == 200:
        return formatted_data
    else:
        print(f"Libretranslate get_language error: {r.status_code}")


def detect_language(text):
    params = {'q': text}
    r = requests.post(f"{API_URL}/detect", data=params).json()
    languages = get_language()
    language_code = r[0]['language']
    language = next((k for k, v in languages.items() if v == language_code), None)

    return language, language_code

