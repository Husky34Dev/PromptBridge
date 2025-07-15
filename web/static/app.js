// Importar funciones de renderizado de tarjetas
import { createResponseCard, formatToolResponse } from './cards.js';

document.addEventListener('DOMContentLoaded', () => {
    // --- Referencias a elementos del DOM ---
    const chatWindow = document.getElementById('chat-window');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const userRoleSelect = document.getElementById('user-role');
    const clearChatButton = document.getElementById('clear-chat');

    // --- Estado de la aplicación ---
    let currentMode = "rígido"; // Modo inicial

    // --- Manejador del botón limpiar chat ---
    clearChatButton.addEventListener('click', () => {
        if (confirm('¿Estás seguro de que quieres limpiar todo el chat?')) {
            clearChat();
        }
    });

    // --- Manejador del envío del formulario ---
    messageForm.addEventListener('submit', event => {
        event.preventDefault();
        const messageText = messageInput.value.trim();
        if (messageText) {
            displayMessage(messageText, 'user');
            messageInput.value = '';
            showBotTyping();
            getBotResponse(messageText);
        }
    });

    /**
     * Añade un mensaje a la ventana del chat.
     * @param {string | HTMLElement} content - El texto o elemento HTML del mensaje.
     * @param {'user' | 'bot'} sender - Quién envía el mensaje.
     */
    function displayMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        if (typeof content === 'string') {
            bubble.textContent = content;
        } else {
            bubble.appendChild(content);
        }

        messageDiv.appendChild(bubble);
        chatWindow.appendChild(messageDiv);
        scrollToBottom();
    }
    
    /**
     * Muestra el indicador de "escribiendo...".
     */
    function showBotTyping() {
        const existingTyping = document.getElementById('typing-indicator');
        if (existingTyping) existingTyping.remove();
        
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'message bot';
        typingDiv.innerHTML = `
            <div class="message-bubble typing-indicator">
                <span></span><span></span><span></span>
            </div>
        `;
        chatWindow.appendChild(typingDiv);
        scrollToBottom();
    }
    
    /**
     * Elimina el indicador de "escribiendo...".
     */
    function hideBotTyping() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    /**
     * Obtiene una respuesta del backend.
     * @param {string} userMessage - El mensaje del usuario.
     */
    async function getBotResponse(userMessage) {
        try {
            const selectedRole = userRoleSelect.value;
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage,
                    user_role: selectedRole,
                    mode: currentMode // Enviamos el modo actual al backend
                })
            });

            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }

            const data = await response.json();
            hideBotTyping();
            handleResponse(data);

        } catch (error) {
            console.error('Error enviando mensaje:', error);
            hideBotTyping();
            displayMessage('❌ Error conectando con el servidor. Por favor, inténtalo de nuevo.', 'bot');
        }
    }

    /**
     * Maneja la respuesta del backend.
     * @param {object} data - Los datos de respuesta del servidor.
     */
    function handleResponse(data) {
        if (data.type === 'chat') {
            displayMessage(data.response || 'No se recibió respuesta', 'bot');
        } else if (data.type === 'tool_calls') {
            handleToolCallsResponse(data);
        } else if (data.type === 'error') {
            displayMessage(`❌ Error: ${data.error}`, 'bot');
        } else {
            displayMessage('🤔 Respuesta inesperada del servidor', 'bot');
        }
    }

    /**
     * Maneja respuestas de llamadas a herramientas.
     * @param {object} data - Los datos de tool_calls.
     */
    function handleToolCallsResponse(data) {
        if (data.results && data.results.length > 0) {
            data.results.forEach(result => {
                if (result.error) {
                    displayMessage(`❌ Error en ${result.tool}: ${result.error}`, 'bot');
                } else if (result.response) {
                    const card = createResponseCard(formatToolResponse(result));
                    displayMessage(card, 'bot');
                }
            });
        } else {
            displayMessage('✅ Operación completada', 'bot');
        }
    }

    /**
     * Desplaza la ventana del chat hasta el final.
     */
    function scrollToBottom() {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    /**
     * Limpia todo el contenido del chat.
     */
    function clearChat() {
        chatWindow.innerHTML = '';
        setTimeout(() => {
            displayMessage('🧹 Chat limpiado correctamente', 'bot');
        }, 100);
    }

    // --- Event listener para cambio de rol ---
    userRoleSelect.addEventListener('change', () => {
        const selectedRole = userRoleSelect.value;
        const roleText = selectedRole.charAt(0).toUpperCase() + selectedRole.slice(1);
        displayMessage(`🔄 Rol cambiado a: ${roleText}`, 'bot');
    });

    // --- LÓGICA DEL INTERRUPTOR DE MODO ---
    const modeToggles = document.querySelectorAll('.mode-toggle');

    function updateModeToggleUI() {
        modeToggles.forEach(el => {
            // Comprueba si el texto del botón coincide con el modo actual
            if (el.textContent.trim().toLowerCase() === currentMode) {
                el.classList.add('active-mode');
            } else {
                el.classList.remove('active-mode');
            }
        });
    }

    modeToggles.forEach(el => {
        el.addEventListener('click', () => {
            const clickedMode = el.textContent.trim().toLowerCase();
            if (currentMode !== clickedMode) {
                currentMode = clickedMode;
                updateModeToggleUI();
                 // Opcional: notificar al usuario del cambio
                displayMessage(`Modo cambiado a: ${currentMode}`, 'bot');
            }
        });
    });

    // --- CÓDIGO NUEVO Y ESENCIAL ---
    // Añade los atributos de datos ('data-mode') para que el CSS pueda aplicar los colores.
    modeToggles.forEach(el => {
        const modeName = el.textContent.trim().toLowerCase();
        el.dataset.mode = modeName; // Esto crea el atributo -> data-mode="rígido"
    });

    // --- INICIALIZACIÓN ---
    // Muestra el estado inicial del interruptor de modo
    updateModeToggleUI();

    // Muestra un mensaje inicial del bot
    setTimeout(() => {
        const initialRole = userRoleSelect.value;
        const roleText = initialRole.charAt(0).toUpperCase() + initialRole.slice(1);
        displayMessage(`¡Bienvenido! Soy tu asistente especializado en gestión de abonados. Estás conectado como: ${roleText}. Puedes preguntarme sobre datos de abonados, facturas, incidencias o el clima.`, 'bot');
    }, 500);
});