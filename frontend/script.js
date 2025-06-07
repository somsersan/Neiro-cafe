document.addEventListener('DOMContentLoaded', () => {
    const sendButton = document.getElementById('send-button');
    const userInput = document.getElementById('user-input');
    const messagesContainer = document.getElementById('messages');
    let currentSessionId = null;  // Добавлено здесь

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // Обработчики голосования (перенесено в начало)
    document.querySelectorAll('.vote-button').forEach(button => {
        button.addEventListener('click', handleVote);
    });

    // Единая функция отправки сообщения
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        addMessage('Вы', message);
        userInput.value = '';

        try {
            // Добавлен индикатор загрузки
            const loadingIndicator = document.createElement('div');
            loadingIndicator.className = 'loading';
            loadingIndicator.textContent = 'AI думает...';
            messagesContainer.appendChild(loadingIndicator);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;

            const response = await fetch('http://localhost:8000/sbs/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ message })
            });

            // Убираем индикатор загрузки
            loadingIndicator.remove();

            const data = await response.json();
            console.log("Ответ от сервера:", data);  // Для отладки
            currentSessionId = data.session_id;
            
            // Отображаем оба ответа
            document.querySelector('#response-1 .response-text').textContent = data.response_1;
            document.querySelector('#response-2 .response-text').textContent = data.response_2;
            
            // Показываем контейнер с ответами
            document.querySelector('.responses-container').style.display = 'flex';
            
            // Добавляем блюда
            if (data.dishes && data.dishes.length > 0) {
                renderDishes(data.dishes);
            }
            
        } catch (error) {
            document.querySelector('.loading')?.remove();
            addMessage('Система', 'Ошибка соединения с сервером');
            console.error('Ошибка:', error);
        }
    }

    // Функция обработки голосования
    async function handleVote(e) {
        const responseOption = e.target.closest('.response-option');
        if (!responseOption) return;
        
        const responseId = responseOption.id;
        const selectedModel = responseId === 'response-1' ? 'model_1' : 'model_2';
        
        try {
            await fetch('http://localhost:8000/sbs/vote', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    session_id: currentSessionId,
                    selected_model: selectedModel
                })
            });
            
            // Показываем выбранный ответ в чате
            const selectedText = responseOption.querySelector('.response-text').textContent;
            addMessage('AI', selectedText);
            
            // Скрываем контейнер с выбором
            document.querySelector('.responses-container').style.display = 'none';
            
        } catch (error) {
            console.error('Ошибка голосования:', error);
            addMessage('Система', 'Ошибка при сохранении выбора');
        }
    }

    // Функция добавления сообщения в чат
    function addMessage(sender, text) {
        const messageElement = document.createElement('div');
        messageElement.innerHTML = `<strong>${sender}:</strong> ${text}`;
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Функция отображения блюд
    function renderDishes(dishes) {
        const dishContainer = document.querySelector('.dish-gallery');
        dishContainer.innerHTML = '<h2>Рекомендуемые блюда</h2>';
        
        dishes.forEach(dish => {
            const dishCard = document.createElement('div');
            dishCard.className = 'dish-card';
            dishCard.innerHTML = `
                <p><strong>${dish.name}</strong></p>
                <p>${dish.description}</p>
                <p>${dish.price} руб.</p>
            `;
            dishContainer.appendChild(dishCard);
        });
    }

    // Получаем элементы модального окна
    const modal = document.getElementById('winner-modal');
    const showWinnerBtn = document.getElementById('show-winner-btn');
    const closeBtn = document.querySelector('.close');
    const winnerModel = document.getElementById('winner-model');
    const winnerStats = document.getElementById('winner-stats');
    
    // Обработчики открытия/закрытия модального окна
    showWinnerBtn.addEventListener('click', openWinnerModal);
    closeBtn.addEventListener('click', closeModal);
    
    // Закрытие при клике вне окна
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });
    
    function openWinnerModal() {
        modal.style.display = 'block';
        loadWinnerData();
    }
    
    function closeModal() {
        modal.style.display = 'none';
    }
    
    async function loadWinnerData() {
        winnerModel.textContent = "Загрузка...";
        winnerStats.textContent = "";
        
        try {
            const response = await fetch('http://localhost:8000/sbs/stats');
            const stats = await response.json();
            
            if (!stats.leader) {
                winnerModel.textContent = "Пока нет победителя!";
                winnerStats.textContent = "Проголосуйте за лучшую модель";
                return;
            }
            
            let modelName;
            if (stats.leader === "model_1") {
                modelName = "GIGACHAT";
            } else if (stats.leader === "model_2") {
                modelName = "YANDEXGPT";
            } else if (stats.leader === "tie") {
                modelName = "Ничья!";
            } else {
                modelName = stats.leader;
            }
            
            winnerModel.textContent = modelName;
            
            // Форматируем статистику
            let statsText = "";
            if (stats.total_votes) {
                statsText = `Всего голосов: ${stats.total_votes}`;
            }
            
            if (stats.models) {
                const modelsText = Object.entries(stats.models)
                    .map(([model, votes]) => `${model === 'model_1' ? 'GIGACHAT' : 'YANDEXGPT'}: ${votes}`)
                    .join(' | ');
                
                if (statsText) statsText += "\n";
                statsText += modelsText;
            }
            
            winnerStats.textContent = statsText;
            
        } catch (error) {
            console.error('Ошибка при получении статистики:', error);
            winnerModel.textContent = "Ошибка загрузки";
            winnerStats.textContent = "Попробуйте позже";
        }
    }
});