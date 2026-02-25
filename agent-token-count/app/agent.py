"""
Класс Agent - инкапсулирует логику LLM агента.
Управляет историей сообщений и взаимодействием с LLM.
"""
from app.llm_client import ask_llm, get_history_tokens, get_request_tokens, check_token_limit, get_max_tokens
from app.storage import MessageStorage


class Agent:
    """
    LLM агент с поддержкой истории сообщений.
    
    Агент хранит контекст диалога и позволяет поддерживать
    беседу с учетом предыдущих сообщений.
    """
    
    def __init__(self, model: str = None, temperature: float = 0.7, load_history: bool = False):
        """
        Инициализация агента.
        
        Args:
            model: Название модели для LLM (по умолчанию из .env)
            temperature: Параметр temperature (0-2)
            load_history: Загружать ли историю из БД
        """
        self.model = model
        self.temperature = temperature
        self.storage = MessageStorage()
        self.messages = []
        
        if load_history and self.storage.has_history():
            loaded = self.storage.load_messages()
            self._add_system_prompt()
            self.messages.extend(loaded)
        else:
            self._add_system_prompt()

    def save_history(self):
        """Сохраняет историю сообщений в БД (без system message)."""
        if self.messages:
            messages_to_save = [m for m in self.messages if m.get("role") != "system"]
            self.storage.clear_history()
            self.storage.save_messages(messages_to_save)

    def _add_system_prompt(self):
        """Добавляет системный промпт в начало истории."""
        self.messages.append({
            "role": "system",
            "content": "Ты полезный AI помощник."
        })

    def check_limit(self, user_message: str = "") -> dict:
        """Проверяет лимит токенов перед запросом."""
        history_tokens = get_history_tokens(self.messages, self.model)
        request_tokens = get_request_tokens(user_message, self.model)
        return check_token_limit(history_tokens, request_tokens, self.model)

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

        self.messages.append({"role": "user", "content": user_message})
        self.messages.append({"role": "assistant", "content": result["text"]})
        
        self.save_history()

        return result

    def reset_history(self):
        """Очищает историю сообщений, сбрасывая системный промпт."""
        self.messages = []
        self._add_system_prompt()
        self.storage.clear_history()

    def get_history(self) -> list:
        """
        Возвращает копию истории сообщений.
        
        Returns:
            Список сообщений [{role, content}, ...]
        """
        return self.messages.copy()
