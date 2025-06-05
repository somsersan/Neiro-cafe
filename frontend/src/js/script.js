document.getElementById('send-button').addEventListener('click', sendMessage);

async function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    if (!userInput.trim()) return;
    
    addMessage('Вы', userInput);
    document.getElementById('user-input').value = '';
    
    try {
        // Показать индикатор загрузки
        const loader = document.createElement('div');
        loader.id = "loader";
        loader.textContent = "ИИ выбирает лучшие блюда...";
        document.getElementById('messages').appendChild(loader);
        
        // Отправка запроса на бэкенд
        const response = await fetch('http://localhost:8000/api/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userInput })
        });
        
        const data = await response.json();
        
        // Убрать индикатор загрузки
        document.getElementById('loader').remove();
        
        // Показать ответ
        addMessage('Нейро-официант', data.reply);
        
        // Показать рекомендации
        if (data.dishes && data.dishes.length > 0) {
            showDishSuggestions(data.dishes);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        addMessage('Система', 'Ошибка соединения с сервером');
    }
}

function addMessage(sender, text) {
    let messageDiv = document.createElement('div');
    messageDiv.textContent = `${sender}: ${text}`;
    document.getElementById('messages').appendChild(messageDiv);
}
