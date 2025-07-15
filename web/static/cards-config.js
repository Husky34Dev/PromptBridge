/**
 * Configuración de tipos de tarjetas para el chatbot
 * Define qué función de renderizado usar para cada tipo de datos
 */

// Mapeo de tipos de datos a funciones de renderizado
export const CARD_TYPES = {
    // Datos de abonado - se detecta por la presencia de campos específicos
    SUBSCRIBER: {
        detect: (data) => data.nombre || data.dni || data.direccion,
        render: 'createSubscriberCard'
    },
    
    // Facturas - se detecta por la presencia del array 'facturas'
    FACTURAS: {
        detect: (data) => data.facturas && Array.isArray(data.facturas),
        render: 'createFacturasCard'
    },
    
    // Clima - se detecta por campos específicos del clima
    WEATHER: {
        detect: (data) => data.clima !== undefined,
        render: 'createWeatherCard'
    },
    
    // Incidencias - se detecta por campos específicos
    INCIDENCIA: {
        detect: (data) => data.estado && data.prioridad && data.descripcion,
        render: 'createIncidenciaCard'
    },
    
    // Deuda total - se detecta por la presencia del campo 'deuda'
    DEUDA: {
        detect: (data) => data.deuda !== undefined,
        render: 'createDeudaCard'
    }
};

// Configuración de iconos para herramientas
export const TOOL_ICONS = {
    'buscar_abonado': '👤',
    'obtener_facturas': '📄',
    'consultar_clima': '🌤️',
    'crear_incidencia': '🚨',
    'buscar_incidencia': '🔍',
    'deuda_total': '💰',
    'default': '🔧'
};

// Configuración de colores para estados
export const STATUS_COLORS = {
    'pagado': '#28a745',
    'pendiente': '#ffc107',
    'alta': '#dc3545',
    'media': '#fd7e14',
    'baja': '#6c757d',
    'abierta': '#17a2b8',
    'cerrada': '#28a745'
};

// Configuración de campos para diferentes tipos de datos
export const FIELD_CONFIGS = {
    subscriber: [
        { key: 'dni', label: 'DNI', icon: '🆔' },
        { key: 'direccion', label: 'Dirección', icon: '📍' },
        { key: 'correo', label: 'Email', icon: '📧' },
        { key: 'telefono', label: 'Teléfono', icon: '📞' },
        { key: 'poliza', label: 'Póliza', icon: '📋' }
    ],
    
    incidencia: [
        { key: 'estado', label: 'Estado', icon: '📊' },
        { key: 'prioridad', label: 'Prioridad', icon: '⚡' },
        { key: 'descripcion', label: 'Descripción', icon: '📝' },
        { key: 'fecha_creacion', label: 'Creada', icon: '📅' },
        { key: 'asignado_a', label: 'Asignado a', icon: '👨‍💼' }
    ],
    
    weather: [
        { key: 'temperatura', label: 'Temperatura', icon: '🌡️', format: (val) => `${val}°C` },
        { key: 'descripcion', label: 'Condición', icon: '☁️' },
        { key: 'humedad', label: 'Humedad', icon: '💧', format: (val) => `${val}%` },
        { key: 'viento', label: 'Viento', icon: '💨', format: (val) => `${val} km/h` }
    ],
    
    deuda: [
        { key: 'deuda', label: 'Deuda Total', icon: '💰', format: (val) => `${val} €` }
    ]
};
