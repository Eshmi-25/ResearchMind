from dataclasses import dataclass
import json
from pathlib import Path
"""
Loads an evaluation dataset and give us a consistent structure.
"""

@dataclass
class EvaluationSample:
    question: str
    answer: str
    relevant_chunks: list[dict]


def load_dataset(
    file_path: str
) -> list[EvaluationSample]:

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Evaluation dataset not found: {file_path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    samples = []

    for item in data:

        samples.append(
            EvaluationSample(
                question=item["question"],
                answer=item["answer"],
                relevant_chunks=item.get(
                    "relevant_chunks",
                    []
                )
            )
        )

    return samples