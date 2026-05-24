from langdetect import detect, LangDetectException


def detect_language(text: str) -> str:
    if not text or len(text.strip()) < 10:
        return "en"
    try:
        lang = detect(text)
        if lang == "ar":
            return "ar"
        return "en"
    except LangDetectException:
        return "en"
