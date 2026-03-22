"""Test scenarios for Grounded Chat Agent."""
from app.agent import Agent


SCENARIO_MKDOCS = {
    "name": "MkDocs Deployment",
    "description": "Сценарий настройки и деплоя MkDocs на GitHub Pages",
    "questions": [
        "Хочу задеплоить MkDocs",
        "На GitHub Pages",
        "Проект уже есть",
        "Как настроить?",
        "Как обновлять?",
        "Где хранится конфиг?",
        "Как добавить поиск?",
        "Как изменить тему?",
        "Как собрать сайт?",
        "Как проверить локально?"
    ]
}


SCENARIO_FIRE = {
    "name": "Fire CLI",
    "description": "Сценарий создания CLI с Python Fire",
    "questions": [
        "Хочу CLI",
        "На Python",
        "Без argparse",
        "Как проще?",
        "Как передавать аргументы?",
        "Как вызвать функцию?",
        "Как обработать типы?",
        "Можно ли использовать классы?",
        "Как запускать из консоли?",
        "Как протестировать?"
    ]
}


def run_scenario(scenario: dict, agent: Agent):
    """
    Run a test scenario.
    
    Args:
        scenario: Dictionary with name, description, questions
        agent: Agent instance
    """
    print("\n" + "=" * 60)
    print(f"СЦЕНАРИЙ: {scenario['name']}")
    print(f"Описание: {scenario['description']}")
    print("=" * 60)
    
    results = {
        "total": len(scenario["questions"]),
        "fallback": 0,
        "has_sources": 0,
        "has_quotes": 0,
        "goal_captured": False,
        "constraints_captured": 0
    }
    
    initial_task_state = agent.get_task_state()
    
    for i, question in enumerate(scenario["questions"], 1):
        print(f"\n[{i}/{results['total']}] Вопрос: {question}")
        
        result = agent.ask(question)
        
        if result.get("fallback"):
            results["fallback"] += 1
            print("  ❌ Отступление")
        else:
            if "sources" in result:
                results["has_sources"] += 1
                print("  ✓ Источники")
            if "quotes" in result:
                results["has_quotes"] += 1
                print("  ✓ Цитаты")
    
    final_task_state = agent.get_task_state()
    
    if final_task_state.get("goal"):
        results["goal_captured"] = True
    
    results["constraints_captured"] = len(final_task_state.get("constraints", []))
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ:")
    print(f"  Всего вопросов: {results['total']}")
    print(f"  Отступлений: {results['fallback']} ({results['fallback']/results['total']*100:.0f}%)")
    print(f"  С источниками: {results['has_sources']} ({results['has_sources']/results['total']*100:.0f}%)")
    print(f"  С цитатами: {results['has_quotes']} ({results['has_quotes']/results['total']*100:.0f}%)")
    print(f"  Goal захвачен: {'✓' if results['goal_captured'] else '✗'}")
    print(f"  Constraints: {results['constraints_captured']}")
    print("=" * 60)
    
    return results


def run_all_scenarios():
    """Run all test scenarios."""
    print("\n" + "#" * 60)
    print("# ЗАПУСК ТЕСТОВЫХ СЦЕНАРИЕВ")
    print("#" * 60)
    
    agent = Agent(
        rag_enabled=True,
        use_filter=True,
        use_rewrite=True,
        debug_mode=True
    )
    
    results_mkdocs = run_scenario(SCENARIO_MKDOCS, agent)
    
    agent.reset()
    
    results_fire = run_scenario(SCENARIO_FIRE, agent)
    
    print("\n" + "#" * 60)
    print("# ИТОГО:")
    print("#" * 60)
    
    total_q = results_mkdocs["total"] + results_fire["total"]
    total_fallback = results_mkdocs["fallback"] + results_fire["fallback"]
    total_sources = results_mkdocs["has_sources"] + results_fire["has_sources"]
    total_quotes = results_mkdocs["has_quotes"] + results_fire["has_quotes"]
    
    print(f"  Всего вопросов: {total_q}")
    print(f"  Отступлений: {total_fallback} ({total_fallback/total_q*100:.0f}%)")
    print(f"  С источниками: {total_sources} ({total_sources/total_q*100:.0f}%)")
    print(f"  С цитатами: {total_quotes} ({total_quotes/total_q*100:.0f}%)")
    print("#" * 60 + "\n")


if __name__ == "__main__":
    run_all_scenarios()
