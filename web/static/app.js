// Importar funciones de renderizado de tarjetas
import { createResponseCard, formatToolResponse } from './cards.js';

document.addEventListener('DOMContentLoaded', () => {
    // --- Referencias a elementos del DOM ---
    const chatWindow = document.getElementById('chat-window');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const userRoleSelect = document.getElementById('user-role');
    const clearChatButton = document.getElementById('clear-chat');

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
            // Muestra el mensaje del usuario y limpia el input
            displayMessage(messageText, 'user');
            messageInput.value = '';
            
            // Muestra el indicador de "escribiendo..." y obtiene la respuesta del bot
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
        // Elimina cualquier indicador previo
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
                    user_role: selectedRole
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
                    const formattedResponse = formatToolResponse(result);
                    const jsonCard = createResponseCard(formattedResponse);
                    displayMessage(jsonCard, 'bot');
                }
            });
        } else {
            displayMessage('✅ Operación completada', 'bot');
        }
    }

    /**
     * Formatea la respuesta de una herramienta.
     * @param {object} result - El resultado de la herramienta.
     * @returns {object} Los datos formateados.
     */
    function formatToolResponse(result) {
        const toolName = result.tool;
        const response = result.response;
        
        return {
            tool: toolName,
            data: response
        };
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
        // Mostrar mensaje de confirmación
        setTimeout(() => {
            displayMessage('🧹 Chat limpiado correctamente', 'bot');
        }, 100);
    }

    // --- Event listeners adicionales ---
    userRoleSelect.addEventListener('change', () => {
        const selectedRole = userRoleSelect.value;
        const roleText = selectedRole.charAt(0).toUpperCase() + selectedRole.slice(1);
        displayMessage(`🔄 Rol cambiado a: ${roleText}`, 'bot');
    });

    // Muestra un mensaje inicial del bot
    setTimeout(() => {
        const initialRole = userRoleSelect.value;
        const roleText = initialRole.charAt(0).toUpperCase() + initialRole.slice(1);
        displayMessage(`¡Bienvenido! Soy tu asistente especializado en gestión de abonados. Estás conectado como: ${roleText}. Puedes preguntarme sobre datos de abonados, facturas, incidencias o el clima.`, 'bot');
    }, 500);
});