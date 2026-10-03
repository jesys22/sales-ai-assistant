from functools import lru_cache

import structlog

logger = structlog.get_logger()

MODEL_NAME = "intfloat/multilingual-e5-large"


@lru_cache(maxsize=1)
def get_model():
    # Импорт внутри функции — чтобы не грузить sentence-transformers при импорте модуля
    from sentence_transformers import SentenceTransformer

    logger.info("loading_embedding_model", model=MODEL_NAME)
    model = SentenceTransformer(MODEL_NAME)
    logger.info("embedding_model_loaded", dim=model.get_embedding_dimension())
    return model


def embed_texts(texts: list[str], is_query: bool = False) -> list[list[float]]:
    model = get_model()
    prefix = "query: " if is_query else "passage: "
    prefixed = [f"{prefix}{t}" for t in texts]

    embeddings = model.encode(
        prefixed,
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True,
    )
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    return embed_texts([query], is_query=True)[0]