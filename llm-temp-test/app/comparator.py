from rich.table import Table
from rich.console import Console
import re

console = Console()

def analyze_temperature_response(resp: str):
    words = resp.split()
    unique_words = len(set(words))

    # Простая метрика разнообразия
    diversity = round(unique_words / len(words), 2) if words else 0

    # Эвристика креативности
    creative_markers = ["например", "представь", "вообрази", "как будто", "метафора"]
    creativity_score = sum(resp.lower().count(w) for w in creative_markers)

    # Эвристика точности (наличие определений)
    precision_markers = ["это", "называется", "определяется", "характеризуется"]
    precision_score = sum(resp.lower().count(w) for w in precision_markers)

    return {
        "words": len(words),
        "diversity": diversity,
        "creativity_score": creativity_score,
        "precision_score": precision_score
    }


def display_temperature_comparison(results):
    table = Table(title="Сравнение temperature")

    table.add_column("Temperature")
    table.add_column("Слова")
    table.add_column("Разнообразие")
    table.add_column("Креативность")
    table.add_column("Точность")

    for temp, data in results.items():
        table.add_row(
            str(temp),
            str(data["words"]),
            str(data["diversity"]),
            str(data["creativity_score"]),
            str(data["precision_score"]),
        )

    console.print(table)
