"""
Multi-Server MCP Orchestrator
Управляет pipeline с несколькими MCP серверами.
Поддерживает Interactive Agent с LLM анализом запросов.
"""
import json
from app.mcp_client import MCPClient

TOOL_TRANSLATIONS = {
    "fetch_recent_reports": "получить последние отчёты из БД",
    "analyze_reports": "проанализировать отчёты",
    "generate_summary": "создать сводку с анализом",
    "save_summary": "сохранить сводку в файл",
    "fetch_productivity_tips": "получить советы по продуктивности",
    "schedule_report": "запустить периодический сбор отчётов",
    "stop_reports": "остановить сбор отчётов",
    "get_reports_summary": "получить статистику по отчётам",
    "get_last_reports": "получить последние сохранённые отчёты",
    "current_time": "получить текущее время",
    "get_mock_issues": "получить демо-задачи",
    "mock_random_tip": "получить случайный совет",
}


class MultiServerOrchestrator:
    """Оркестратор для управления multi-server MCP pipeline."""
    
    def __init__(self):
        self.demo_client = MCPClient()
        self.external_client = MCPClient()
        self.tools_description = self._get_tools_description()
    
    def _get_tools_description(self) -> str:
        """Возвращает описание доступных инструментов для LLM"""
        return """- fetch_recent_reports: получить последние отчёты из БД
- analyze_reports: проанализировать отчёты (принимает данные от fetch_recent_reports)
- generate_summary: создать summary с анализом и рекомендациями (принимает analysis и tips)
- save_summary: сохранить summary в файл memory/monitoring_summary.txt
- fetch_productivity_tips: получить советы по продуктивности с внешнего API (adviceslip.com)
- schedule_report: запустить периодический сбор отчётов
- stop_reports: остановить сбор отчётов
- get_reports_summary: получить статистику по отчётам
- get_last_reports: получить последние отчёты
- current_time: получить текущее время
- get_mock_issues: получить демо-задачи
- mock_random_tip: получить случайный совет"""
    
    def _analyze_request_with_llm(self, user_request: str) -> dict:
        """LLM анализирует запрос и решает что делать"""
        from app.llm_client import ask_llm
        
        prompt = f"""
Пользователь: "{user_request}"

Доступные инструменты:
{self.tools_description}

СТРОГИЕ ПРАВИЛА:
1. Система ПОДДЕРЖИВАЕТ только эти запросы:
   - "анализируй/проанализируй данные/отчёты" → план: fetch_recent_reports → analyze_reports → generate_summary → save_summary
   - "совет/советы по продуктивности" → fetch_productivity_tips
   - "текущее время/время" → current_time
   - "демо-задачи/задачи" → get_mock_issues
   - "случайный совет" → mock_random_tip
   - "статистика/отчёты" → get_reports_summary

2. Всё остальное → can_do: false + alternatives из списка выше

3. НЕ придумывай план если запрос не подходит точно

Верни ЧИСТЫЙ JSON без форматирования:
{{"can_do": true/false, "plan": [{{"tool": "название", "params": {{}}}}] или null, "alternatives": ["инструмент1", "инструмент2"] или null}}
"""
        
        try:
            response = ask_llm(prompt)
            
            # ask_llm возвращает dict с полем 'text' содержащим JSON
            if isinstance(response, dict):
                text = response.get('text', '')
                if text:
                    try:
                        result = json.loads(text)
                        return result
                    except json.JSONDecodeError:
                        pass
                
                # Может быть can_do на верхнем уровне
                if 'can_do' in response:
                    return response
            
            return {"can_do": False, "plan": None, "alternatives": None, "error": "No 'text' field in response"}
        except Exception as e:
            return {"can_do": False, "plan": None, "alternatives": None, "error": str(e)}
    
    def run_interactive(self) -> str:
        """Запустить интерактивный режим с LLM анализом"""
        print("=== Interactive MCP Agent ===")
        print("\nПодключено! Введите ваш запрос (или 'exit' для выхода):\n")
        if not self.demo_client.connect_to_demo_server():
            return "Error: Failed to connect to demo_server"
        
        print("Connecting to external_api_server...")
        if not self.external_client.connect_to_external_server():
            self.demo_client.close()
            return "Error: Failed to connect to external_api_server"
        
        print("\nПодключено! Введите ваш запрос (или 'exit' для выхода):\n")
        
        while True:
            user_input = input("Вы: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "выход", "quit"]:
                print("До свидания!")
                break
            
            # Анализируем запрос через LLM
            print("\nАнализирую запрос...")
            analysis = self._analyze_request_with_llm(user_input)
            
            if "error" in analysis:
                print(f"Ошибка анализа: {analysis['error']}")
                print()
                continue
            
            if not analysis.get("can_do", False):
                # Запрос не поддерживается
                message = "Я не могу выполнить этот запрос."
                
                print(f"\nAI Agent: {message}")
                print()
                continue
            
            # Выполняем план
            plan = analysis.get("plan", [])
            if not plan:
                print("\nAI Agent: Не могу составить план выполнения.")
                print()
                continue
            
            # Показываем план пользователю
            print(f"\nAI Agent: Составил план из {len(plan)} шагов:\n")
            for i, step in enumerate(plan, 1):
                tool = step.get("tool", "")
                translation = TOOL_TRANSLATIONS.get(tool, "")
                print(f"  {i}. {tool} - {translation}")
            
            # Запускаем подтверждение
            print("\nЗапустить? (да/нет): ", end="")
            confirm = input().strip().lower()
            
            if confirm in ["да", "yes", "y", "д", "lf"]:
                # Запускаем фиксированный pipeline
                print("\n" + "="*50)
                result = self.run_pipeline()
                print(result)
            else:
                print("\nОтменено. Введите новый запрос.")
            
            print()
        
        # Отключаемся
        self.demo_client.close()
        self.external_client.close()
        
        return "Interactive session ended"
    
    def run_pipeline(self) -> str:
        """Запустить multi-server pipeline (автоматический режим)."""
        
        # Подключаемся к серверам
        print("Connecting to demo_server...")
        if not self.demo_client.connect_to_demo_server():
            return "Error: Failed to connect to demo_server"
        
        print("Connecting to external_api_server...")
        if not self.external_client.connect_to_external_server():
            self.demo_client.close()
            return "Error: Failed to connect to external_api_server"
        
        print("\n=== MULTI MCP PIPELINE START ===\n")
        
        # Шаг 1: Получаем отчёты
        print("Step 1: Fetch reports from local DB")
        reports = self.demo_client.call_tool("fetch_recent_reports")
        
        # Шаг 2: Получаем советы
        print("\nStep 2: Fetch productivity tips from external API")
        tips = self.external_client.call_tool("fetch_productivity_tips")
        
        # Очищаем от лишнего текста
        if isinstance(tips, str):
            tips = tips.replace("Вот перевод на русский язык:\n", "")
            tips = tips.replace("Вот перевод на русский язык:", "")
            tips = tips.replace("Вот переводы на русский язык:\n", "")
            tips = tips.replace("Вот переводы на русский язык:", "")
            tips = tips.strip()
        
        # Шаг 3: Анализируем
        print("\nStep 3: Analyze reports")
        analysis = self.demo_client.call_tool("analyze_reports", {"reports": reports})
        
        # Проверяем, что analysis - словарь
        if not isinstance(analysis, dict):
            print(f"  ERROR: analysis is not a dict, it's {type(analysis)}")
            return f"Error: analyze_reports returned {type(analysis)} instead of dict"
        
        # Шаг 4: Формируем summary с LLM
        print("\nStep 4: Generate summary (with LLM)")
        summary = self.demo_client.call_tool("generate_summary", {
            "analysis": analysis,
            "tips": tips
        })
        
        # Шаг 5: Сохраняем
        print("\nStep 5: Save summary")
        path = self.demo_client.call_tool("save_summary", {"summary": summary})
        
        print("\n=== PIPELINE COMPLETE ===\n")
        
        # Отключаемся
        self.demo_client.close()
        self.external_client.close()
        
        return f"Pipeline complete. Summary saved to: {path}"
