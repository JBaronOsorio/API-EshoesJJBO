"""
Servicio de integración con la API de Google Gemini.

Este módulo implementa la comunicación con el modelo de lenguaje Gemini
para generar respuestas conversacionales. Usa el SDK oficial google-genai
(reemplazo del legacy google-generativeai, descontinuado en noviembre 2025).

El servicio recibe el contexto de la conversación y el inventario de
productos para construir un prompt que permita al modelo responder con
información precisa y actualizada del catálogo.
"""

from google import genai

from src.config import settings
from src.domain.entities import ChatContext, Product


class GeminiService:
    """
    Servicio que encapsula la comunicación con la API de Google Gemini.

    Construye el prompt completo con el inventario de productos y el
    historial conversacional, envía la solicitud a Gemini y retorna
    la respuesta generada. Esta clase es la única en el proyecto que
    conoce los detalles de la API externa de IA.

    Attributes:
        client (genai.Client): Cliente autenticado del SDK de Google GenAI.
        model_name (str): Nombre del modelo de Gemini a utilizar.
    """

    MODEL_NAME = "gemini-2.5-flash"

    def __init__(self) -> None:
        """
        Inicializa el cliente de Gemini con la API key desde la configuración.

        Raises:
            ValueError: Si la GEMINI_API_KEY no está configurada en el entorno.
        """
        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY no está configurada. "
                "Agrégala al archivo .env antes de iniciar la aplicación."
            )

        self.client = genai.Client(api_key=settings.gemini_api_key)

    async def generate_response(
        self,
        user_message: str,
        products: list[Product],
        context: ChatContext,
    ) -> str:
        """
        Genera una respuesta conversacional usando el modelo Gemini.

        Construye un prompt estructurado que incluye las instrucciones del
        sistema, el inventario de productos disponibles, el historial reciente
        de la conversación y el mensaje actual del usuario. Envía todo esto
        a Gemini y retorna el texto de la respuesta generada.

        Args:
            user_message (str): Mensaje actual enviado por el usuario.
            products (list[Product]): Lista completa de productos del inventario.
            context (ChatContext): Contexto con el historial reciente de la sesión.

        Returns:
            str: Respuesta generada por el modelo de IA.

        Raises:
            Exception: Si ocurre un error al comunicarse con la API de Gemini.
        """
        products_info = self._format_products_info(products)
        conversation_history = context.format_for_prompt()

        prompt = self._build_prompt(user_message, products_info, conversation_history)

        response = self.client.models.generate_content(
            model=self.MODEL_NAME,
            contents=prompt,
        )

        return response.text.strip()

    def _build_prompt(
        self,
        user_message: str,
        products_info: str,
        conversation_history: str,
    ) -> str:
        """
        Construye el prompt completo para enviar al modelo de Gemini.

        Estructura el prompt en secciones claras: instrucciones del sistema,
        inventario disponible, historial de conversación y mensaje actual.
        Un prompt bien estructurado es determinante para la calidad
        de las respuestas del modelo.

        Args:
            user_message (str): Mensaje actual del usuario.
            products_info (str): Inventario formateado como texto.
            conversation_history (str): Historial reciente formateado.

        Returns:
            str: Prompt completo listo para enviar a Gemini.
        """
        history_section = ""
        if conversation_history:
            history_section = f"""
HISTORIAL DE LA CONVERSACIÓN:
{conversation_history}
"""

        prompt = f"""Eres un asistente virtual experto en ventas de zapatos para un e-commerce llamado ShoesAI.
Tu objetivo es ayudar a los clientes a encontrar el zapato perfecto según sus necesidades.

INSTRUCCIONES:
- Sé amigable, profesional y conciso en tus respuestas.
- Recomienda productos específicos del inventario cuando sea apropiado.
- Menciona siempre el precio, la talla y el stock disponible al recomendar un producto.
- Si el cliente pregunta por algo que no está en el inventario, sé honesto y ofrece alternativas.
- Usa el historial de la conversación para dar respuestas coherentes y no repetirte.
- Responde siempre en español.

INVENTARIO DISPONIBLE:
{products_info}
{history_section}
Usuario: {user_message}
Asistente:"""

        return prompt

    def _format_products_info(self, products: list[Product]) -> str:
        """
        Convierte la lista de productos a un texto estructurado para el prompt.

        Genera una línea por producto con los datos más relevantes para
        que el modelo pueda referenciarlos en sus respuestas.

        Args:
            products (list[Product]): Lista de productos del inventario.

        Returns:
            str: Inventario formateado como texto, una línea por producto.
                Retorna un mensaje informativo si el inventario está vacío.
        """
        if not products:
            return "No hay productos disponibles en este momento."

        lines = []
        for product in products:
            availability = "disponible" if product.is_available() else "agotado"
            lines.append(
                f"- {product.name} | Marca: {product.brand} | "
                f"Categoría: {product.category} | Talla: {product.size} | "
                f"Color: {product.color} | Precio: ${product.price:.2f} | "
                f"Stock: {product.stock} unidades ({availability})"
            )

        return "\n".join(lines)