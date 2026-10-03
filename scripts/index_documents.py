import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import delete

from app.db.models import Document
from app.db.session import async_session_maker, engine
from app.rag.chunking import chunk_text, load_documents_from_folder
from app.rag.embeddings import embed_texts


async def index_documents():
    documents = load_documents_from_folder("data/docs")
    print(f"Loaded {len(documents)} documents")

    all_chunks: list[dict] = []
    for doc in documents:
        chunks = chunk_text(doc["content"])
        for i, chunk in enumerate(chunks):
            all_chunks.append(
                {
                    "title": f"{doc['title']} (part {i + 1})",
                    "content": chunk,
                    "source": doc["source"],
                }
            )

    print(f"Total chunks: {len(all_chunks)}")

    if not all_chunks:
        print("Nothing to index")
        return

    print("Computing embeddings (this may take a while on first run)...")
    texts = [c["content"] for c in all_chunks]
    embeddings = embed_texts(texts, is_query=False)

    print(f"Got {len(embeddings)} embeddings, dim={len(embeddings[0])}")

    async with async_session_maker() as session:
        await session.execute(delete(Document))
        await session.commit()
        print("Cleared old documents")

        for chunk, emb in zip(all_chunks, embeddings):
            doc = Document(
                title=chunk["title"],
                content=chunk["content"],
                source=chunk["source"],
                embedding=emb,
            )
            session.add(doc)

        await session.commit()
        print(f"Indexed {len(all_chunks)} chunks")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(index_documents())