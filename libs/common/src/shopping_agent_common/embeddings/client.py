import logging
from functools import lru_cache

import voyageai

from shopping_agent_common.config import CommonSettings, get_common_settings
from shopping_agent_common.exceptions import EmbeddingError

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """Thin wrapper around the Voyage embeddings API. Document and query text
    use different `input_type`s because Voyage tunes its embeddings
    asymmetrically for retrieval (documents vs. queries)."""

    def __init__(self, settings: CommonSettings):
        self._client = voyageai.Client(api_key=settings.voyage_api_key)
        self._model = settings.voyage_model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        try:
            result = self._client.embed(texts, model=self._model, input_type="document")
        except Exception as exc:
            logger.error(
                "Voyage embed_documents failed: model=%s count=%d error=%s",
                self._model,
                len(texts),
                exc,
            )
            raise EmbeddingError(
                f"Failed to embed {len(texts)} document(s): {exc}", cause=exc
            ) from exc
        return result.embeddings

    def embed_query(self, text: str) -> list[float]:
        try:
            result = self._client.embed([text], model=self._model, input_type="query")
        except Exception as exc:
            logger.error("Voyage embed_query failed: model=%s error=%s", self._model, exc)
            raise EmbeddingError(f"Failed to embed query: {exc}", cause=exc) from exc
        return result.embeddings[0]


@lru_cache
def get_embedding_client() -> EmbeddingClient:
    return EmbeddingClient(get_common_settings())
