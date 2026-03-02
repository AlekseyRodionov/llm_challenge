"""
Класс Agent - инкапсулирует логику LLM агента.
Управляет историей сообщений и взаимодействием с LLM.
"""
from app.llm_client import ask_llm


class Agent:
    """
    LLM агент с поддержкой истории сообщений.
    
    Агент хранит контекст диалога и позволяет поддерживать
    беседу с учетом предыдущих сообщений.
    """
    
    def __init__(self, model: str = None, temperature: float = 0.7):
        """
        Инициализация агента.
        
        Args:
            model: Название модели для LLM (по умолчанию из .env)
            temperature: Параметр temperature (0-2)
        """
        self.model = model
        self.temperature = temperature
        self.messages = []
        self._add_system_prompt()

    def _add_system_prompt(self):
        """Добавляет системный промпт в начало истории."""
        self.messages.append({
            "role": "system",
            "content": "Ты полезный AI помощник."
        })

    def ask(self, user_message: str) -> dict:
        """
        Отправляет сообщение агенту и получает ответ.
        
        Args:
            user_message: Сообщение от пользователя
        
        Returns:
            Словарь с ответом и метриками от LLM
        """
        result = ask_llm(
            prompt=user_message,
            model=self.model,
            temperature=self.temperature,
            messages=self.messages
        )

        # Добавляем сообщение пользователя и ответ в историю
        self.messages.append({"role": "user", "content": user_message})
        self.messages.append({"role": "assistant", "content": result["text"]})

        return result

    def reset_history(self):
        """Очищает историю сообщений, сбрасывая системный промпт."""
        self.messages = []
        self._add_system_prompt()

    def get_history(self) -> list:
        """
        Возвращает копию истории сообщений.
        
        Returns:
            Список сообщений [{role, content}, ...]
        """
        return self.messages.copy()
