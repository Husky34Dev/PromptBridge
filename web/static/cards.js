/**
 * Módulo para el renderizado de tarjetas de respuesta del chatbot
 * Separación de la lógica de presentación visual
 */

import { CARD_TYPES, TOOL_ICONS, FIELD_CONFIGS } from './cards-config.js';

/**
 * Formatea la respuesta de una herramienta.
 * @param {object} result - El resultado de la herramienta.
 * @returns {object} Los datos formateados.
 */
export function formatToolResponse(result) {
    const toolName = result.tool;
    const response = result.response;
    
    return {
        tool: toolName,
        data: response
    };
}

/**
 * Crea una tarjeta HTML para visualizar respuestas del backend.
 * @param {object} responseData - Los datos de respuesta formateados.
 * @returns {HTMLElement} El elemento de la tarjeta.
 */
export function createResponseCard(responseData) {
    const card = document.createElement('div');
    card.className = 'response-card';
    
    // Título de la herramienta con icono configurado
    const header = document.createElement('div');
    header.className = 'response-header';
    const toolIcon = TOOL_ICONS[responseData.tool] || TOOL_ICONS.default;
    header.innerHTML = `<span class="tool-icon">${toolIcon}</span><strong>${responseData.tool}</strong>`;
    card.appendChild(header);
    
    // Contenido de los datos
    const content = document.createElement('div');
    content.className = 'response-content';
    content.appendChild(renderResponseData(responseData.data));
    card.appendChild(content);
    
    return card;
}

/**
 * Renderiza los datos de respuesta con formato especial para datos de abonado.
 * @param {object} data - Los datos a renderizar.
 * @returns {HTMLElement} El elemento renderizado.
 */
export function renderResponseData(data) {
    const container = document.createElement('div');
    if (!data || typeof data !== 'object') {
        container.textContent = 'Sin datos para mostrar.';
        return container;
    }
    // Casos especiales para datos de abonado
    if (data.nombre || data.dni || data.direccion) {
        return createSubscriberCard(data);
    }
    
    // Casos especiales para facturas
    if (data.facturas && Array.isArray(data.facturas)) {
        return createFacturasCard(data.facturas);
    }

    // Casos especiales para incidencias
    if (data.incidencias && Array.isArray(data.incidencias)) {
        return createIncidenciasCard(data.incidencias);
    }

    // Casos especiales para el clima
    if (data.clima !== undefined) {
        return createWeatherCard(data);
    }
    if(data.deuda!==undefined){
        return createDeudaCard(data);
    }
    
    // Renderizado genérico
    return renderObject(data);
}

/**
 * Crea una tarjeta especial para datos de abonado.
 * @param {object} data - Los datos del abonado.
 * @returns {HTMLElement} La tarjeta del abonado.
 */
export function createSubscriberCard(data) {
    const card = document.createElement('div');
    card.className = 'subscriber-card';
    
    if (data.nombre) {
        const name = document.createElement('h3');
        name.className = 'subscriber-name';
        name.innerHTML = `👤 ${data.nombre}`;
        card.appendChild(name);
    }
    
    // Usar configuración de campos
    const fields = FIELD_CONFIGS.subscriber;
    
    fields.forEach(field => {
        if (data[field.key]) {
            const fieldDiv = document.createElement('div');
            fieldDiv.className = 'subscriber-field';
            const value = field.format ? field.format(data[field.key]) : data[field.key];
            fieldDiv.innerHTML = `
                <span class="field-icon">${field.icon}</span>
                <span class="field-label">${field.label}:</span>
                <span class="field-value">${value}</span>
            `;
            card.appendChild(fieldDiv);
        }
    });
    
    return card;
}

/**
 * Crea una tarjeta especial para facturas.
 * @param {Array} facturas - Array de facturas.
 * @returns {HTMLElement} La tarjeta de facturas.
 */
export function createFacturasCard(facturas) {
    const card = document.createElement('div');
    card.className = 'facturas-card';
    
    const header = document.createElement('h3');
    header.innerHTML = `📄 Facturas (${facturas.length})`;
    card.appendChild(header);
    
    facturas.forEach(factura => {
        const facturaDiv = document.createElement('div');
        facturaDiv.className = 'factura-item';

        const estadoClass = `estado-${factura.estado?.toLowerCase() || 'desconocido'}`;
        
        facturaDiv.innerHTML = `
            <div class="factura-info">
                <div class="factura-id">
                    <span class="field-icon">#</span>
                    <span>Factura ${factura.identificador || 'N/A'}</span>
                </div>
                <div class="factura-fecha">
                    <span class="field-icon">📅</span>
                    <span>${factura.fecha || 'Sin fecha'}</span>
                </div>
            </div>
            <div class="factura-details">
                <div class="factura-estado ${estadoClass}">${factura.estado || 'Sin estado'}</div>
                <div class="factura-importe">€${factura.importe || '0.00'}</div>
            </div>
        `;
        card.appendChild(facturaDiv);
    });
    
    return card;
}

/**
 * Crea una tarjeta especial para una lista de incidencias.
 * @param {Array} incidencias - Array de incidencias.
 * @returns {HTMLElement} La tarjeta de incidencias.
 */
function createIncidenciasCard(incidencias) {
    const card = document.createElement('div');
    card.className = 'incidencias-card';
    
    const header = document.createElement('h3');
    header.innerHTML = `🚨 Incidencias (${incidencias.length})`;
    card.appendChild(header);
    
    incidencias.forEach(incidencia => {
        const incidenciaDiv = document.createElement('div');
        incidenciaDiv.className = 'incidencia-item';

        const estadoClass = `estado-${incidencia.estado?.toLowerCase() || 'desconocido'}`;
        
        incidenciaDiv.innerHTML = `
            <div class="incidencia-location">
                <span class="field-icon">📍</span>
                <span>${incidencia.ubicacion || 'Ubicación no especificada'}</span>
            </div>
            <div class="incidencia-description">
                ${incidencia.descripcion || 'Sin descripción.'}
            </div>
            <div class="incidencia-status">
                <span class="estado ${estadoClass}">${incidencia.estado || 'Sin estado'}</span>
            </div>
        `;
        card.appendChild(incidenciaDiv);
    });
    
    return card;
}

/**
 * Renderiza un objeto genérico como HTML.
 * @param {object} obj - El objeto a renderizar.
 * @returns {HTMLElement} El elemento renderizado.
 */
export function renderObject(obj) {
    const container = document.createElement('div');
    for (const key in obj) {
        if (Object.prototype.hasOwnProperty.call(obj, key)) {
            const entry = document.createElement('div');
            entry.className = 'json-entry';
            
            const keySpan = document.createElement('span');
            keySpan.className = 'json-key';
            keySpan.textContent = `${key}: `;
            entry.appendChild(keySpan);
            
            const value = obj[key];
            
            if (typeof value === 'object' && value !== null) {
                const nestedContainer = document.createElement('div');
                nestedContainer.className = 'json-nested-object';
                nestedContainer.appendChild(Array.isArray(value) ? renderArray(value) : renderObject(value));
                entry.appendChild(nestedContainer);
            } else {
                const valueSpan = document.createElement('span');
                valueSpan.className = 'json-value';
                valueSpan.textContent = JSON.stringify(value);
                entry.appendChild(valueSpan);
            }
            container.appendChild(entry);
        }
    }
    return container;
}

/**
 * Renderiza un array genérico como HTML.
 * @param {Array} arr - El array a renderizar.
 * @returns {HTMLElement} El elemento renderizado.
 */
export function renderArray(arr) {
    const list = document.createElement('div');
    arr.forEach((item, index) => {
        const itemEntry = document.createElement('div');
        itemEntry.className = 'json-entry';
        itemEntry.textContent = `[${index}]: `;
        
        const nestedContainer = document.createElement('div');
        nestedContainer.className = 'json-nested-object';
        
        if (typeof item === 'object' && item !== null) {
            nestedContainer.appendChild(renderObject(item));
        } else {
            nestedContainer.textContent = JSON.stringify(item);
        }
        itemEntry.appendChild(nestedContainer);
        list.appendChild(itemEntry);
    });
    return list;
}

// --- Funciones para tipos de tarjetas futuras ---

/**
 * Crea una tarjeta para datos del clima (ejemplo extensible).
 * @param {object} weatherData - Los datos del clima.
 * @returns {HTMLElement} La tarjeta del clima.
 */
export function createWeatherCard(weatherData) {
    const card = document.createElement('div');
    card.className = 'weather-card';

    // Parsear la cadena de clima
    const { ciudad, temperatura, descripcion } = parseWeatherString(weatherData.clima);

    const header = document.createElement('h3');
    header.innerHTML = `🌤️ Clima en ${ciudad || 'Desconocido'}`;
    card.appendChild(header);

    const content = document.createElement('div');
    content.className = 'weather-content';

    if (temperatura) {
        const tempDiv = document.createElement('div');
        tempDiv.className = 'weather-temp';
        tempDiv.innerHTML = `🌡️ ${temperatura}°C`;
        content.appendChild(tempDiv);
    }

    if (descripcion) {
        const descDiv = document.createElement('div');
        descDiv.className = 'weather-desc';
        descDiv.innerHTML = `${getWeatherIcon(descripcion)} ${descripcion}`;
        content.appendChild(descDiv);
    }

    card.appendChild(content);
    return card;
}

/**
 * Parsea una cadena de texto sobre el clima para extraer datos.
 * @param {string} weatherString - La cadena de texto del clima.
 * @returns {object} Objeto con ciudad, temperatura y descripción.
 */
function parseWeatherString(weatherString) {
    if (typeof weatherString !== 'string') {
        return {};
    }

    const weatherData = {};

    // Extraer temperatura
    const tempMatch = weatherString.match(/(\d+)\s*grados/i);
    if (tempMatch) {
        weatherData.temperatura = parseInt(tempMatch[1], 10);
    }

    // Extraer ciudad
    const cityMatch = weatherString.match(/en\s+([a-záéíóúñ\s]+)/i);
    if (cityMatch) {
        weatherData.ciudad = cityMatch[1].trim();
    }

    // Extraer descripción (lo que queda)
    let description = weatherString
        .replace(tempMatch ? tempMatch[0] : '', '')
        .replace(cityMatch ? cityMatch[0] : '', '')
        .replace(/Clima:/i, '')
        .trim();
    weatherData.descripcion = description.charAt(0).toUpperCase() + description.slice(1);

    return weatherData;
}

/**
 * Obtiene un icono basado en la descripción del clima.
 * @param {string} description - La descripción del clima.
 * @returns {string} El emoji del icono.
 */
function getWeatherIcon(description) {
    const lowerDesc = description.toLowerCase();
    if (lowerDesc.includes('sol') || lowerDesc.includes('despejado')) return '☀️';
    if (lowerDesc.includes('nube') || lowerDesc.includes('nublado')) return '☁️';
    if (lowerDesc.includes('lluvia')) return '🌧️';
    if (lowerDesc.includes('tormenta')) return '⛈️';
    if (lowerDesc.includes('nieve')) return '❄️';
    return '🌍'; // Icono por defecto
}

/**
 * Crea una tarjeta para incidencias (ejemplo extensible).
 * @param {object} incidenciaData - Los datos de la incidencia.
 * @returns {HTMLElement} La tarjeta de incidencia.
 */
export function createIncidenciaCard(incidenciaData) {
    const card = document.createElement('div');
    card.className = 'incidencia-card';
    
    const header = document.createElement('h3');
    header.innerHTML = `🚨 Incidencia - ${incidenciaData.id || 'Sin ID'}`;
    card.appendChild(header);
    
    // Usar configuración de campos
    const fields = FIELD_CONFIGS.incidencia;
    
    fields.forEach(field => {
        if (incidenciaData[field.key]) {
            const fieldDiv = document.createElement('div');
            fieldDiv.className = 'incidencia-field';
            fieldDiv.innerHTML = `
                <span class="field-icon">${field.icon}</span>
                <span class="field-label">${field.label}:</span>
                <span class="field-value">${incidenciaData[field.key]}</span>
            `;
            card.appendChild(fieldDiv);
        }
    });
    
    return card;
}

/**
 * Crea una tarjeta para mostrar la deuda total de un abonado.
 * @param {object} deudaData - Los datos de la deuda.
 * @returns {HTMLElement} La tarjeta de deuda.
 */
export function createDeudaCard(deudaData) {
    const card = document.createElement('div');
    card.className = 'deuda-card';

    const header = document.createElement('h3');
    header.innerHTML = `💰 Deuda Total`;
    card.appendChild(header);

    // Usar configuración de campos
    const fields = FIELD_CONFIGS.deuda;
    fields.forEach(field => {
        if (deudaData[field.key] !== undefined) {
            const fieldDiv = document.createElement('div');
            fieldDiv.className = 'deuda-field';
            const value = field.format ? field.format(deudaData[field.key]) : deudaData[field.key];
            fieldDiv.innerHTML = `
                <span class="field-icon">${field.icon}</span>
                <span class="field-label">${field.label}:</span>
                <span class="field-value deuda-value">${value}</span>
            `;
            card.appendChild(fieldDiv);
        }
    });

    return card;
}
