import re
from pathlib import Path

import structlog

logger = structlog.get_logger()


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Разбивает текст на чанки по предложениям с перекрытием."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= chunk_size:
            current = f"{current} {sentence}".strip()
        else:
            if current:
                chunks.append(current)
            current = sentence

    if current:
        chunks.append(current)

    if overlap > 0 and len(chunks) > 1:
        overlapped: list[str] = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_tail = chunks[i - 1][-overlap:]
            overlapped.append(f"{prev_tail} {chunks[i]}".strip())
        chunks = overlapped

    return chunks


def load_documents_from_folder(folder: str | Path) -> list[dict]:
    """Загружает все .txt и .md из папки."""
    folder = Path(folder)
    if not folder.exists():
        logger.warning("folder_not_found", folder=str(folder))
        return []

    documents: list[dict] = []
    for file_path in sorted(folder.glob("*")):
        if file_path.suffix.lower() not in {".txt", ".md"}:
            continue
        if file_path.name.startswith("."):
            continue

        try:
            content = file_path.read_text(encoding="utf-8").strip()
        except Exception as e:
            logger.error("read_file_failed", file=str(file_path), error=str(e))
            continue

        if not content:
            continue

        documents.append(
            {
                "title": file_path.stem,
                "content": content,
                "source": str(file_path),
            }
        )
        logger.info("document_loaded", file=file_path.name, chars=len(content))

    return documents
