import re


def normalize_text(text: str) -> str:

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def token_set(text: str) -> set[str]:

    return set(
        normalize_text(text).split()
    )


def token_precision(
    answer: str,
    reference: str
) -> float:

    answer_tokens = token_set(answer)
    reference_tokens = token_set(reference)

    if not answer_tokens:
        return 0.0

    return len(
        answer_tokens & reference_tokens
    ) / len(answer_tokens)


def token_recall(
    answer: str,
    reference: str
) -> float:

    answer_tokens = token_set(answer)
    reference_tokens = token_set(reference)

    if not reference_tokens:
        return 0.0

    return len(
        answer_tokens & reference_tokens
    ) / len(reference_tokens)


def token_f1(
    answer: str,
    reference: str
) -> float:

    precision = token_precision(
        answer,
        reference
    )

    recall = token_recall(
        answer,
        reference
    )

    if precision + recall == 0:
        return 0.0

    return (
        2 * precision * recall
        / (precision + recall)
    )


def exact_match(
    answer: str,
    reference: str
) -> float:

    return float(
        normalize_text(answer)
        == normalize_text(reference)
    )