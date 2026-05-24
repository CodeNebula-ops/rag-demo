import re
import unicodedata


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Cc" or ch in "\n\t\r")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def remove_headers_footers(pages: list[str]) -> list[str]:
    if len(pages) < 3:
        return pages

    first_lines = [p.split("\n")[0].strip() for p in pages if p.strip()]
    last_lines = [p.split("\n")[-1].strip() for p in pages if p.strip()]

    repeated_first = _find_repeated(first_lines)
    repeated_last = _find_repeated(last_lines)

    cleaned = []
    for page in pages:
        lines = page.split("\n")
        if lines and lines[0].strip() in repeated_first:
            lines = lines[1:]
        if lines and lines[-1].strip() in repeated_last:
            lines = lines[:-1]
        cleaned.append("\n".join(lines))

    return cleaned


def _find_repeated(lines: list[str], threshold: float = 0.5) -> set[str]:
    from collections import Counter
    counts = Counter(lines)
    total = len(lines)
    return {line for line, count in counts.items() if line and count / total >= threshold}
