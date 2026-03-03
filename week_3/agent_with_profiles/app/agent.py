"""
Класс Agent - инкапсулирует логику LLM агента.
Управляет трёхслойной моделью памяти и взаимодействием с LLM.
"""
from app.llm_client import ask_llm
from app.memory_manager import (
    init_db,
    add_long_term_memory,
    add_working_memory,
    get_long_term_memory,
    get_working_memory,
    clear_working_memory,
    clear_all_memory,
    get_active_profile
)
from app.router import route_message


class Agent:
    """
    LLM агент с трёхслойной моделью памяти:
    - Short-term: текущий диалог (в памяти Python)
    - Working: данные текущей задачи (SQLite)
    - Long-term: устойчивые факты о пользователе (SQLite)
    """

    def __init__(self, model: str = None, temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.short_term_memory = []
        init_db()

    def _build_system_prompt(self) -> str:
        """Формирует системный prompt на основе памяти и профиля."""
        profile = get_active_profile()
        
        parts = [
            "You are an AI assistant.",
            f"\nUSER PROFILE:\n{profile['description']}",
            "\nAdapt your answer automatically according to this profile."
        ]

        long_term = get_long_term_memory()
        if long_term:
            parts.append("\nДолговременная память (факты о пользователе):")
            for item in long_term:
                parts.append(f"- {item['content']}")

        working = get_working_memory()
        if working:
            parts.append("\nРабочая память (текущая задача):")
            for item in working:
                parts.append(f"- {item['content']}")

        return "\n".join(parts)

    def _save_to_memory(self, user_message: str):
        """Сохраняет данные из сообщения в соответствующую память."""
        routes = route_message(user_message)

        for route in routes:
            text = route.get("text", "").strip()
            memory_type = route.get("memory_type", "")

            if not text:
                continue

            if memory_type == "long_term":
                add_long_term_memory(text)
            elif memory_type == "working":
                add_working_memory(text)

    def ask(self, user_message: str) -> dict:
        """
        Отправляет сообщение агенту и получает ответ.
        
        Args:
            user_message: Сообщение от пользователя
        
        Returns:
            Словарь с ответом и метриками от LLM
        """
        # Сохраняем в память через маршрутизатор
        self._save_to_memory(user_message)

        # Добавляем в short-term память
        self.short_term_memory.append({"role": "user", "content": user_message})

        # Формируем системный prompt с учётом памяти
        system_prompt = self._build_system_prompt()

        # Формируем полный контекст
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.short_term_memory)

        result = ask_llm(
            prompt="",
            model=self.model,
            temperature=self.temperature,
            messages=messages
        )

        # Добавляем ответ в short-term память
        self.short_term_memory.append({"role": "assistant", "content": result["text"]})

        return result

    def reset_history(self):
        """Очищает short-term память (текущий диалог)."""
        self.short_term_memory = []

    def clear_working(self):
        """Очищает рабочую память."""
        clear_working_memory()

    def clear_all(self):
        """Очищает всю память (кроме short-term)."""
        clear_all_memory()

    def get_short_term(self) -> list:
        """Возвращает short-term память."""
        return self.short_term_memory.copy()

    def get_long_term(self) -> list:
        """Возвращает long-term память из БД."""
        return get_long_term_memory()

    def get_working(self) -> list:
        """Возвращает working память из БД."""
        return get_working_memory()

    def get_all_memory(self) -> dict:
        """Возвращает все слои памяти."""
        return {
            "short_term": self.get_short_term(),
            "working": self.get_working(),
            "long_term": self.get_long_term()
        }
