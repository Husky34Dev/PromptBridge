# Sistema de Tarjetas del Chatbot

Este módulo maneja el renderizado de tarjetas para mostrar las respuestas de las herramientas del chatbot de manera visual y estructurada.

## Estructura de Archivos

- `cards.js` - Funciones principales de renderizado
- `cards-config.js` - Configuración de tipos, iconos y campos
- `app.js` - Lógica principal del chatbot (importa de cards.js)

## Agregar Nuevos Tipos de Tarjetas

### 1. Configurar el Tipo en `cards-config.js`

```javascript
export const CARD_TYPES = {
    // ... tipos existentes ...
    
    // Nuevo tipo
    MI_NUEVO_TIPO: {
        detect: (data) => data.campo_especifico || data.otro_campo,
        render: 'createMiNuevoTipoCard'
    }
};
```

### 2. Agregar Icono de Herramienta

```javascript
export const TOOL_ICONS = {
    // ... iconos existentes ...
    
    'mi_herramienta': '🎯',  // Icono para tu herramienta
};
```

### 3. Configurar Campos (opcional)

```javascript
export const FIELD_CONFIGS = {
    // ... configuraciones existentes ...
    
    miNuevoTipo: [
        { key: 'campo1', label: 'Campo 1', icon: '📋' },
        { key: 'campo2', label: 'Campo 2', icon: '📊', format: (val) => `${val}%` },
        // ...más campos
    ]
};
```

### 4. Crear Función de Renderizado en `cards.js`

```javascript
export function createMiNuevoTipoCard(data) {
    const card = document.createElement('div');
    card.className = 'mi-nuevo-tipo-card';
    
    // Header
    const header = document.createElement('h3');
    header.innerHTML = `🎯 Mi Nuevo Tipo - ${data.titulo}`;
    card.appendChild(header);
    
    // Usar configuración de campos si existe
    const fields = FIELD_CONFIGS.miNuevoTipo || [];
    
    fields.forEach(field => {
        if (data[field.key]) {
            const fieldDiv = document.createElement('div');
            fieldDiv.className = 'field';
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
```

### 5. Actualizar `renderResponseData`

```javascript
export function renderResponseData(data) {
    // Casos especiales para datos de abonado
    if (data.nombre || data.dni || data.direccion) {
        return createSubscriberCard(data);
    }
    
    // Facturas
    if (data.facturas && Array.isArray(data.facturas)) {
        return createFacturasCard(data.facturas);
    }
    
    // Tu nuevo tipo
    if (data.campo_especifico || data.otro_campo) {
        return createMiNuevoTipoCard(data);
    }
    
    // Renderizado genérico
    return renderObject(data);
}
```

## Estilos CSS

Asegúrate de agregar los estilos correspondientes en `styles.css`:

```css
.mi-nuevo-tipo-card {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 16px;
    margin: 8px 0;
    background: #f9f9f9;
}

.mi-nuevo-tipo-card .field {
    display: flex;
    align-items: center;
    margin: 8px 0;
}

.mi-nuevo-tipo-card .field-icon {
    margin-right: 8px;
    font-size: 1.1em;
}

.mi-nuevo-tipo-card .field-label {
    font-weight: 600;
    margin-right: 8px;
    color: #666;
}

.mi-nuevo-tipo-card .field-value {
    color: #333;
}
```

## Tipos de Tarjetas Existentes

1. **Tarjetas de Abonado** (`createSubscriberCard`)
   - Detecta: `data.nombre`, `data.dni`, `data.direccion`
   - Muestra: información personal del abonado

2. **Tarjetas de Facturas** (`createFacturasCard`)
   - Detecta: `data.facturas` (array)
   - Muestra: lista de facturas con estado, fecha, importe

3. **Tarjetas de Clima** (`createWeatherCard`)
   - Detecta: `data.temperatura`, `data.ciudad`, `data.descripcion`
   - Muestra: información meteorológica

4. **Tarjetas de Incidencias** (`createIncidenciaCard`)
   - Detecta: `data.estado`, `data.prioridad`, `data.descripcion`
   - Muestra: detalles de incidencias técnicas

## Renderizado Genérico

Para datos que no coinciden con ningún tipo específico, se usa `renderObject()` que crea una visualización JSON estructurada.

## Configuración Avanzada

### Formateo de Valores

Puedes usar la propiedad `format` en la configuración de campos:

```javascript
{ key: 'temperatura', label: 'Temp', icon: '🌡️', format: (val) => `${val}°C` }
```

### Detección Condicional

Las funciones de detección pueden ser más complejas:

```javascript
detect: (data) => {
    return data.tipo === 'producto' && data.precio && data.categoria;
}
```

### Iconos Dinámicos

Los iconos pueden depender del contenido:

```javascript
const getStatusIcon = (estado) => {
    const icons = {
        'abierto': '🟢',
        'cerrado': '🔴',
        'pendiente': '🟡'
    };
    return icons[estado] || '⚪';
};
```
