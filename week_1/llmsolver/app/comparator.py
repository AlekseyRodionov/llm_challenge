def analyze_reasoning(text: str):
    lower = text.lower()
    contains_structure = "1." in text and "2." in text and "3." in text
    liar_detected = any(name in lower for name in ["алекс", "боб", "карл"])
    coffee_detected = "кофе" in lower
    word_count = len(text.split())
    return {
        "Есть структура 1-2-3": contains_structure,
        "Указан лжец": liar_detected,
        "Указан заказчик кофе": coffee_detected,
        "Количество слов": word_count
    }

def compare_responses(responses):
    analysis_results = []
    for idx, r in enumerate(responses, 1):
        analysis = analyze_reasoning(r["text"])
        analysis["Промт"] = f"Промт {idx}"
        analysis["Токены (входные)"] = r.get("input_tokens", 0)
        analysis["Токены (выходные)"] = r.get("output_tokens", 0)
        analysis["Токены (всего)"] = r.get("total_tokens", 0)
        analysis_results.append(analysis)
    return analysis_results
