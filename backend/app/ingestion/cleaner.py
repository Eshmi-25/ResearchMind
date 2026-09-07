import re


def clean_text(text: str) -> str:
    """
    Clean extracted document text.
    """

    # Replace multiple whitespace characters with a single space
    text = re.sub(r"\s+", " ", text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text