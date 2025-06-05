import os
import openai
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class AIAssistant:
    def __init__(self):
        # Инициализация API ключа
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Системный промпт для специализации помощника
        self.system_prompt = """
        Ты ИИ-ассистент в ресторане "Neuro-cafe", помогающий гостям выбрать блюда.
        Твои задачи:
        1. Задавай уточняющие вопросы о предпочтениях (аллергии, диеты, кухни)
        2. Предлагай конкретные блюда из нашего меню
        3. Давай краткие, дружелюбные ответы (не более 2 предложений)
        4. Всегда предлагай ровно 3 варианта блюд с кратким описанием
        
        Меню ресторана:
        - Стейк Рибай (мясное): Говядина 300г, соус трюфельный - 1200 руб.
        - Веганская паста (веганское): Паста из цукини, песто из базилика - 780 руб.
        - Лосось на гриле (рыбное): Филе лосося с овощами - 950 руб.
        - Греческий салат (вегетарианское): Свежие овощи, фета, оливки - 650 руб.
        - Тирамису (десерт): Классический итальянский десерт - 480 руб.
        """
    
    def get_recommendations(self, user_input: str) -> dict:
        """Получение рекомендаций от ИИ"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message['content'].strip()
            
            # Парсинг ответа для извлечения блюд
            dishes = self.parse_dishes_from_response(ai_response)
            
            return {
                "reply": ai_response,
                "dishes": dishes
            }
        except Exception as e:
            return {
                "reply": "Извините, произошла ошибка. Попробуйте еще раз.",
                "dishes": []
            }
    
    def parse_dishes_from_response(self, response: str) -> list:
        """Парсинг блюд из ответа ИИ (упрощенная версия)"""
        # В реальном проекте здесь должна быть более сложная логика парсинга
        # или лучше попросить ИИ возвращать данные в JSON формате
        
        dishes = []
        menu_items = [
            "Стейк Рибай", "Веганская паста", "Лосось на гриле", 
            "Греский салат", "Тирамису"
        ]
        
        for item in menu_items:
            if item in response:
                dishes.append({
                    "name": item,
                    "description": "Вкусное блюдо из нашего меню",
                    "price": 0  # Можно добавить реальные цены
                })
                if len(dishes) >= 3:
                    break
        
        return dishes