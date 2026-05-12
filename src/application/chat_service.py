"""
Servicio de aplicación para el chat conversacional con IA.

Este módulo orquesta el flujo completo de procesamiento de mensajes:
recupera el contexto conversacional, consulta el inventario de productos,
delega la generación de respuesta al servicio de IA y persiste el
intercambio en la base de datos.
"""

from datetime import datetime, timezone
from typing import List, Optional

from src.application.dtos import ChatHistoryDTO, ChatMessageRequestDTO, ChatMessageResponseDTO
from src.domain.entities import ChatContext, ChatMessage
from src.domain.exceptions import ChatServiceError
from src.domain.repositories import IChatRepository, IProductRepository


class ChatService:
    """
    Servicio que implementa el caso de uso de chat conversacional con IA.

    Coordina tres dependencias: el repositorio de productos (para informar
    al modelo sobre el inventario), el repositorio de chat (para mantener
    el historial) y el servicio de IA (para generar respuestas). Ninguna
    de estas dependencias se crea aquí, se reciben por inyección.

    Attributes:
        product_repo (IProductRepository): Repositorio de productos.
        chat_repo (IChatRepository): Repositorio de mensajes de chat.
        ai_service: Servicio de IA para generación de respuestas (GeminiService).
    """

    def __init__(
        self,
        product_repo: IProductRepository,
        chat_repo: IChatRepository,
        ai_service,
    ) -> None:
        """
        Inicializa el servicio con sus tres dependencias.

        Args:
            product_repo (IProductRepository): Repositorio de productos.
            chat_repo (IChatRepository): Repositorio de historial de chat.
            ai_service: Instancia del servicio de IA. Se tipea como Any
                para evitar dependencia circular con la capa de infraestructura.
        """
        self.product_repo = product_repo
        self.chat_repo = chat_repo
        self.ai_service = ai_service

    async def process_message(
        self, request: ChatMessageRequestDTO
    ) -> ChatMessageResponseDTO:
        """
        Procesa un mensaje del usuario y genera una respuesta con IA.

        Ejecuta el flujo completo de una interacción de chat:
        1. Recupera los productos disponibles para informar al modelo.
        2. Obtiene los últimos 6 mensajes de la sesión como contexto.
        3. Construye un ChatContext con el historial reciente.
        4. Solicita al servicio de IA una respuesta contextualizada.
        5. Persiste el mensaje del usuario y la respuesta del asistente.
        6. Retorna el DTO con ambos mensajes y el timestamp.

        Args:
            request (ChatMessageRequestDTO): Mensaje del usuario con su session_id.

        Returns:
            ChatMessageResponseDTO: Respuesta del asistente junto con el
                mensaje original y metadatos de la sesión.

        Raises:
            ChatServiceError: Si ocurre un error al comunicarse con la IA
                o al persistir los mensajes.
        """
        try:
            products = self.product_repo.get_all()

            recent_messages = self.chat_repo.get_recent_messages(
                session_id=request.session_id,
                count=6,
            )

            context = ChatContext(messages=recent_messages)

            assistant_response = await self.ai_service.generate_response(
                user_message=request.message,
                products=products,
                context=context,
            )

            timestamp = datetime.now(timezone.utc)

            user_message_entity = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="user",
                message=request.message,
                timestamp=timestamp,
            )

            assistant_message_entity = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="assistant",
                message=assistant_response,
                timestamp=timestamp,
            )

            self.chat_repo.save_message(user_message_entity)
            self.chat_repo.save_message(assistant_message_entity)

            return ChatMessageResponseDTO(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=assistant_response,
                timestamp=timestamp,
            )

        except ChatServiceError:
            raise
        except Exception as e:
            raise ChatServiceError(
                f"Error al procesar el mensaje: {str(e)}"
            ) from e

    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[ChatHistoryDTO]:
        """
        Recupera el historial de mensajes de una sesión conversacional.

        Args:
            session_id (str): Identificador de la sesión a consultar.
            limit (Optional[int]): Número máximo de mensajes a retornar.
                Si es None, retorna el historial completo.

        Returns:
            List[ChatHistoryDTO]: Lista de mensajes en orden cronológico.
        """
        messages = self.chat_repo.get_session_history(
            session_id=session_id,
            limit=limit,
        )

        return [
            ChatHistoryDTO(
                id=msg.id,
                role=msg.role,
                message=msg.message,
                timestamp=msg.timestamp,
            )
            for msg in messages
        ]

    def clear_session_history(self, session_id: str) -> int:
        """
        Elimina todo el historial de mensajes de una sesión.

        Útil para reiniciar una conversación sin cambiar el session_id,
        o para cumplir solicitudes de borrado de datos del usuario.

        Args:
            session_id (str): Identificador de la sesión a limpiar.

        Returns:
            int: Número de mensajes eliminados.
        """
        return self.chat_repo.delete_session_history(session_id)