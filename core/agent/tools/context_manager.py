import json
import re
from pathlib import Path

class ContextManager:
    """
    Clase para la gestión de contexto y extracción de entidades en las conversaciones.
    Permite cargar patrones y referencias, extraer entidades del texto y resolver referencias contextuales.
    """
    def __init__(self, patterns_path, reference_map_path=None):
        """
        Inicializa el gestor de contexto cargando patrones y referencias desde archivos JSON.
        
        Args:
            patterns_path (str): Ruta al archivo de patrones de entidades.
            reference_map_path (str, opcional): Ruta al archivo de referencias contextuales.
        """
        self.patterns = self._load_patterns(patterns_path)
        self.context = {}
        self.reference_map = self._load_reference_map(reference_map_path) if reference_map_path else {}

    def _load_patterns(self, path):
        """
        Carga los patrones de entidades desde un archivo JSON.
        Args:
            path (str): Ruta al archivo de patrones.
        Returns:
            dict: Diccionario de patrones de entidades.
        """
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_reference_map(self, path):
        """
        Carga el mapa de referencias desde un archivo JSON.
        Args:
            path (str): Ruta al archivo de referencias.
        Returns:
            dict: Diccionario de referencias.
        """
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def extract_and_update(self, text):
        """
        Extrae entidades usando los patrones y actualiza el contexto.
        La extracción de DNI es case-insensitive y se normaliza la letra a mayúscula.
        Args:
            text (str): Texto de entrada del usuario.
        Returns:
            dict: Contexto actualizado con las entidades extraídas.
        """
        for entity, pattern in self.patterns.items():
            flags = re.IGNORECASE if entity == "dni" else 0
            match = re.search(pattern, text, flags)
            if match:
                value = match.group()
                # Normalizar DNI: letra final en mayúscula
                if entity == "dni":
                    value = value[:-1] + value[-1].upper()
                self.context[entity] = value
        return self.context.copy()

    def resolve_reference(self, text):
        """
        Resuelve referencias usando patrones regex del reference_map.
        Args:
            text (str): Texto de entrada del usuario.
        Returns:
            dict: Entidad referenciada encontrada en el contexto, si existe.
        """
        for ref_pattern, entity in self.reference_map.items():
            if re.search(ref_pattern, text, re.IGNORECASE) and entity in self.context:
                return {entity: self.context[entity]}
        return {}

    def get_context(self):
        """
        Retorna una copia del contexto actual.
        Returns:
            dict: Contexto actual.
        """
        return self.context.copy()

    def clear_context(self):
        """
        Limpia el contexto almacenado.
        """
        self.context.clear()

# Ejemplo de uso:
# patterns_path = 'client_config/entity_patterns.json'
# reference_map_path = 'client_config/reference_map.json'
# cm = ContextManager(patterns_path, reference_map_path)
# cm.extract_and_update('facturas dni 12345678A')
# cm.resolve_reference('todos los datos de este abonado')
