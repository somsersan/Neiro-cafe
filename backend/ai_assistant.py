import os
import requests
import uuid
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Загрузка переменных окружения
load_dotenv()

class AIAssistant:
    def __init__(self):
        # Ключи для GigaChat API
        self.auth_key = os.getenv("GIGACHAT_AUTH_KEY")
        self.token_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.api_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        
        # Ключи для Yandex GPT
        self.yandex_oauth_token = os.getenv("YANDEX_OAUTH_TOKEN")
        self.yandex_iam_url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
        self.yandex_gpt_url = "https://llm.api.cloud.yandex.net/llm/v1alpha/chat"
        self.yandex_folder_id = os.getenv("YANDEX_FOLDER_ID")

         # Токены и их время жизни
        self.gigachat_token = None
        self.gigachat_token_expires = None
        self.yandex_iam_token = None
        self.yandex_iam_token_expires = None

        # Системный промпт
        self.system_prompt = """
        Ты ИИ-ассистент в ресторане "Ikanam-cafe", помогающий гостям выбрать блюда.
        Твои задачи:
        1. Задавай уточняющие вопросы о предпочтениях (аллергии, диеты, кухни)
        2. Предлагай конкретные блюда из нашего меню
        3. Давай краткие, дружелюбные ответы (не более 2 предложений)
        4. Всегда предлагай ровно 3 варианта блюд с кратким описанием
        
        Меню ресторана:
        - Стейк Рибай (мясное, 320 ккал/100г): Говядина 300г, соус трюфельный - 1200 руб.
        - Веганская паста (веганское, 110 ккал/100г): Паста из цукини, песто из базилика - 780 руб.
        - Лосось на гриле (рыбное, 210 ккал/100г): Филе лосося с овощами - 950 руб.
        - Греческий салат (вегетарианское, 90 ккал/100г): Свежие овощи, фета, оливки - 650 руб.
        - Тирамису (десерт, 290 ккал/100г): Классический итальянский десерт - 480 руб.
        - Пицца Маргарита (вегетарианское, 270 ккал/100г): Тесто, томаты, моцарелла, базилик - 800 руб.
        - Суши с лососем (рыбное, 180 ккал/100г): Рис, лосось, нори - 350 руб.
        - Бургер Классический (мясное, 295 ккал/100г): Говяжья котлета, булочка, сыр, овощи - 690 руб.
        - Паста Карбонара (мясное, 320 ккал/100г): Спагетти, бекон, сливочный соус, пармезан - 790 руб.
        - Том Ям (рыбное, 90 ккал/100г): Кисло-острый суп с креветками и кокосовым молоком - 690 руб.
        - Лазанья (мясное, 160 ккал/100г): Слоеная паста с мясным соусом и сыром - 950 руб.
        - Паэлья с морепродуктами (рыбное, 140 ккал/100г): Рис, креветки, мидии, шафран - 1100 руб.
        - Рамен с курицей (мясное, 120 ккал/100г): Лапша, куриный бульон, яйцо, овощи - 680 руб.
        - Фо Бо (мясное, 60 ккал/100г): Говяжий бульон, рисовая лапша, зелень - 670 руб.
        - Тако с говядиной (мясное, 210 ккал/100г): Кукурузная лепешка, говядина, сальса - 420 руб.
        - Чизкейк Нью-Йорк (десерт, 320 ккал/100г): Сливочный сыр, песочное тесто - 430 руб.
        - Тирамису (десерт, 290 ккал/100г): Классический итальянский десерт - 480 руб.
        - Брауни (десерт, 410 ккал/100г): Шоколадный пирог с орехами - 390 руб.
        - Курица терияки (мясное, 150 ккал/100г): Курица в сладком соусе терияки с рисом - 720 руб.
        - Салат Цезарь (мясное, 180 ккал/100г): Курица, салат ромэн, пармезан, соус - 650 руб.
        - Греческий салат (вегетарианское, 90 ккал/100г): Свежие овощи, фета, оливки - 650 руб.
        - Хачапури по-аджарски (вегетарианское, 320 ккал/100г): Лепешка с сыром и яйцом - 650 руб.
        - Шашлык из баранины (мясное, 250 ккал/100г): Баранина, специи, лук - 950 руб.
        - Пад Тай (мясное, 160 ккал/100г): Лапша с курицей, арахисом и овощами - 720 руб.
        - Бифштекс по-татарски (мясное, 220 ккал/100г): Говядина, лук, специи - 780 руб.
        - Борщ (мясное, 50 ккал/100г): Свекольный суп с говядиной и сметаной - 490 руб.
        - Пельмени с говядиной (мясное, 210 ккал/100г): Тесто, говядина, специи - 540 руб.
        - Кимчи (веганское, 30 ккал/100г): Острая квашеная капуста с овощами - 350 руб.
        - Мусака (мясное, 140 ккал/100г): Баклажаны, фарш, соус бешамель - 850 руб.
        - Фалафель (веганское, 170 ккал/100г): Нутовые шарики, специи, соус тахини - 520 руб.
        - Хумус (веганское, 160 ккал/100г): Пюре из нута с тахини и оливковым маслом - 390 руб.
        - Баклава (десерт, 430 ккал/100г): Слоеное тесто, орехи, мед - 390 руб.
        - Венский шницель (мясное, 220 ккал/100г): Телятина в панировке, картофель - 950 руб.
        - Суп мисо (вегетарианское, 40 ккал/100г): Бульон, мисо-паста, тофу, водоросли - 390 руб.
        - Чуррос с шоколадом (десерт, 350 ккал/100г): Жареное тесто, шоколадный соус - 390 руб.
        """
        
        # Токен и время его истечения
        self.access_token = None
        self.token_expires = 0
    
    def get_access_token(self) -> str:
        """Получение или обновление access token для GigaChat API"""
        # Если токен действителен более 5 минут, используем существующий
        if self.access_token and time.time() < self.token_expires - 300:
            return self.access_token
        
        try:
            payload = {'scope': 'GIGACHAT_API_PERS'}
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'RqUID': str(uuid.uuid4()),
                'Authorization': f'Basic {self.auth_key}'
            }
            
            print("DEBUG: Получаю токен GigaChat...")
            response = requests.post(
                self.token_url,
                headers=headers,
                data=payload,
                verify=False
            )
            
            print("DEBUG: Ответ от сервера:", response.status_code, response.text)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                # Токен действителен 30 минут (1800 секунд)
                self.token_expires = time.time() + token_data['expires_at']
                return self.access_token
            else:
                raise Exception(f"Ошибка получения токена: {response.status_code} - {response.text}")
        
        except Exception as e:
            raise Exception(f"Ошибка аутентификации: {str(e)}")
    
    def get_recommendations(self, user_input: str) -> dict:
        """Получение рекомендаций от GigaChat"""
        try:
            access_token = self.get_access_token()
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            
            payload = {
                "model": "GigaChat",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                verify=False
            )
            
            if response.status_code != 200:
                return {
                    "reply": f"Ошибка API: {response.status_code} - {response.text}",
                    "dishes": []
                }
            
            ai_response = response.json()['choices'][0]['message']['content'].strip()
            
            # Парсинг блюд
            dishes = self.parse_dishes_from_response(ai_response)
            
            return {
                "reply": ai_response,
                "dishes": dishes
            }
            
        except Exception as e:
            return {
                "reply": f"Извините, произошла ошибка: {str(e)}",
                "dishes": []
            }
        
    def get_yandex_iam_token(self) -> str:
        """Получение и обновление IAM-токена для Yandex Cloud"""
        if self.yandex_iam_token and datetime.now() < self.yandex_iam_token_expires - timedelta(minutes=5):
            return self.yandex_iam_token
        
        try:
            payload = {
                "yandexPassportOauthToken": self.yandex_oauth_token
            }
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.yandex_iam_url,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.yandex_iam_token = token_data["iamToken"]
            # IAM-токен обычно действителен 12 часов
            self.yandex_iam_token_expires = datetime.now() + timedelta(seconds=token_data.get("expiresIn", 3600))
            
            return self.yandex_iam_token
            
        except Exception as e:
            raise Exception(f"Ошибка получения IAM-токена: {str(e)}")

    def get_yandexgpt_recommendations(self, user_input: str) -> dict:
        """Получение рекомендаций от Yandex GPT (новый endpoint)"""
        try:
            # Получение IAM-токена
            iam_token = self.get_yandex_iam_token()
            yandex_gpt_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
            headers = {
                "Authorization": f"Bearer {iam_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "modelUri": f"gpt://{self.yandex_folder_id}/yandexgpt/latest",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.7,
                    "maxTokens": 500
                },
                "messages": [
                    {"role": "system", "text": self.system_prompt},
                    {"role": "user", "text": user_input}
                ]
            }
            response = requests.post(
                yandex_gpt_url,
                headers=headers,
                json=payload
            )
            if response.status_code != 200:
                return {
                    "reply": f"Ошибка API: {response.status_code} - {response.text}",
                    "dishes": []
                }
            data = response.json()
            ai_response = data["result"]["alternatives"][0]["message"]["text"].strip()
            return {
                "reply": ai_response,
                "dishes": self.parse_dishes_from_response(ai_response)
            }
        except Exception as e:
            return {
                "reply": f"Yandex GPT error: {str(e)}",
                "dishes": []
            }

    def get_dual_responses(self, user_input: str) -> dict:
        """Получить ответы сразу от GigaChat и YandexGPT"""
        gigachat = self.get_recommendations(user_input)
        yandexgpt = self.get_yandexgpt_recommendations(user_input)
        return {
            "gigachat": gigachat,
            "yandexgpt": yandexgpt
        }
    
    def parse_dishes_from_response(self, response: str) -> list:
        """Парсинг блюд из ответа ИИ"""
        dishes = []
        menu_items = {
            "Стейк Рибай": {"description": "Говядина 300г, соус трюфельный", "price": 1200},
            "Веганская паста": {"description": "Паста из цукини, песто из базилика", "price": 780},
            "Лосось на гриле": {"description": "Филе лосося с овощами", "price": 950},
            "Греческий салат": {"description": "Свежие овощи, фета, оливки", "price": 650},
            "Тирамису": {"description": "Классический итальянский десерт", "price": 480},
            "Цезарь с курицей": {"description": "Классический салат с курицей, пармезаном и соусом цезарь", "price": 700},
            "Борщ": {"description": "Традиционный русский суп со сметаной и говядиной", "price": 550},
            "Пицца Маргарита": {"description": "Тонкое тесто, томаты, моцарелла, базилик", "price": 900},
            "Картофель фри": {"description": "Хрустящий картофель, соль", "price": 350},
            "Морс ягодный": {"description": "Освежающий напиток из лесных ягод", "price": 250},
            "Американо": {"description": "Классический черный кофе", "price": 200},
            "Капучино": {"description": "Кофе с молочной пеной", "price": 250},
            "Чизкейк Нью-Йорк": {"description": "Нежный сырный десерт на песочном корже", "price": 520}
        }
        
        # Ищем упоминания блюд в ответе
        for name, details in menu_items.items():
            if name.lower() in response.lower():
                dishes.append({
                    "name": name,
                    "description": details["description"],
                    "price": details["price"]
                })
                if len(dishes) >= 3:
                    break
        
        return dishes