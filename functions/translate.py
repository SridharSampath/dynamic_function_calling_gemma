import requests

def translate_text(text: str, target_language: str) -> str:
    """Translate text using MyMemory Translation API."""
    print("Translate text using Translation API from translate_text")
    try:
        source_language = "en"  # English

        url = f"https://api.mymemory.translated.net/get?q={text}&langpair={source_language}|{target_language}"

        response = requests.get(url)
        response.raise_for_status()

        result = response.json()

        return result["responseData"]["translatedText"]

    except Exception as e:
        return f"Translation Error: {str(e)}"