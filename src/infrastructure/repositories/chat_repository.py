"""
Implementación concreta del repositorio de chat con SQLAlchemy.

Este módulo implementa la interfaz IChatRepository definida en el dominio,
usando SQLAlchemy para persistir y recuperar mensajes de la tabla chat_memory.
El orden cronológico de los mensajes es crítico para que el contexto
conversacional sea coherente.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from src.domain.entities import ChatMessage
from src.domain.repositories import IChatRepository
from src.infrastructure.db.models import ChatMemoryModel


class SQLChatRepository(IChatRepository):
    """
    Repositorio de mensajes de chat que persiste en SQLite con SQLAlchemy.

    Implementa todos los métodos de IChatRepository. El manejo correcto
    del orden de los mensajes es la responsabilidad más importante de esta
    clase: los mensajes deben retornarse siempre en orden cronológico
    (más antiguo primero) para que el modelo de IA los interprete bien.

    Attributes:
        db (Session): Sesión activa de SQLAlchemy inyectada por FastAPI.
    """

    def __init__(self, db: Session) -> None:
        """
        Inicializa el repositorio con una sesión de base de datos.

        Args:
            db (Session): Sesión de SQLAlchemy activa para este request.
        """
        self.db = db

    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Persiste un mensaje de chat en la base de datos.

        Args:
            message (ChatMessage): Entidad de mensaje a guardar.

        Returns:
            ChatMessage: El mensaje guardado con su ID asignado por la BD.
        """
        model = self._entity_to_model(message)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._model_to_entity(model)

    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """
        Recupera el historial de mensajes de una sesión en orden cronológico.

        Args:
            session_id (str): Identificador de la sesión.
            limit (Optional[int]): Máximo de mensajes a retornar.
                Si es None, retorna el historial completo.

        Returns:
            List[ChatMessage]: Mensajes ordenados del más antiguo al más reciente.
        """
        query = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(ChatMemoryModel.timestamp.asc())
        )

        if limit is not None:
            query = query.limit(limit)

        models = query.all()
        return [self._model_to_entity(m) for m in models]

    def delete_session_history(self, session_id: str) -> int:
        """
        Elimina todos los mensajes de una sesión conversacional.

        Args:
            session_id (str): Identificador de la sesión a limpiar.

        Returns:
            int: Número de mensajes eliminados.
        """
        deleted_count = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .delete()
        )
        self.db.commit()
        return deleted_count

    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """
        Recupera los últimos N mensajes de una sesión en orden cronológico.

        Obtiene los mensajes más recientes ordenando de forma descendente
        y luego invierte la lista para retornarlos del más antiguo al más
        reciente. Este orden es el que espera ChatContext.format_for_prompt().

        Args:
            session_id (str): Identificador de la sesión.
            count (int): Número de mensajes recientes a recuperar.

        Returns:
            List[ChatMessage]: Últimos N mensajes en orden cronológico
                (más antiguo primero).
        """
        models = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(ChatMemoryModel.timestamp.desc())
            .limit(count)
            .all()
        )

        models.reverse()
        return [self._model_to_entity(m) for m in models]

    def _model_to_entity(self, model: ChatMemoryModel) -> ChatMessage:
        """
        Convierte un modelo ORM ChatMemoryModel a una entidad ChatMessage.

        Args:
            model (ChatMemoryModel): Modelo ORM recuperado de la base de datos.

        Returns:
            ChatMessage: Entidad del dominio con los datos del modelo.
        """
        return ChatMessage(
            id=model.id,
            session_id=model.session_id,
            role=model.role,
            message=model.message,
            timestamp=model.timestamp,
        )

    def _entity_to_model(self, message: ChatMessage) -> ChatMemoryModel:
        """
        Convierte una entidad ChatMessage a un modelo ORM ChatMemoryModel.

        Args:
            message (ChatMessage): Entidad del dominio a convertir.

        Returns:
            ChatMemoryModel: Modelo ORM listo para ser persistido.
        """
        return ChatMemoryModel(
            id=message.id,
            session_id=message.session_id,
            role=message.role,
            message=message.message,
            timestamp=message.timestamp,
        )