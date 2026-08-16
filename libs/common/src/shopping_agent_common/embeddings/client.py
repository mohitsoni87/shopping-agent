from functools import lru_cache

import voyageai

from shopping_agent_common.config import CommonSettings, get_common_settings


class EmbeddingClient:
    """Thin wrapper around the Voyage embeddings API. Document and query text
    use different `input_type`s because Voyage tunes its embeddings
    asymmetrically for retrieval (documents vs. queries)."""

    def __init__(self, settings: CommonSettings):
        self._client = voyageai.Client(api_key=settings.voyage_api_key)
        self._model = settings.voyage_model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        result = self._client.embed(texts, model=self._model, input_type="document")
        return result.embeddings

    def embed_query(self, text: str) -> list[float]:
        result = self._client.embed([text], model=self._model, input_type="query")
        return result.embeddings[0]


@lru_cache
def get_embedding_client() -> EmbeddingClient:
    return EmbeddingClient(get_common_settings())
