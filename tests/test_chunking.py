from app.rag.chunking import chunk_text, load_documents_from_folder


def test_chunk_text_short():
    text = "Первое предложение. Второе предложение."
    chunks = chunk_text(text, chunk_size=200, overlap=0)
    assert len(chunks) == 1
    assert "Первое" in chunks[0]


def test_chunk_text_splits_long():
    text = ". ".join([f"Предложение номер {i}" for i in range(50)])
    chunks = chunk_text(text, chunk_size=100, overlap=0)
    assert len(chunks) > 1


def test_chunk_text_empty():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_text_overlap_applied():
    text = ". ".join([f"Предложение номер {i}" for i in range(20)])
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) >= 2


def test_load_documents_from_folder(tmp_path):
    (tmp_path / "a.txt").write_text("Текст A", encoding="utf-8")
    (tmp_path / "b.md").write_text("Текст B", encoding="utf-8")
    (tmp_path / "ignore.png").write_text("ignore", encoding="utf-8")
    (tmp_path / ".hidden.txt").write_text("hidden", encoding="utf-8")

    docs = load_documents_from_folder(tmp_path)
    assert len(docs) == 2
    titles = {d["title"] for d in docs}
    assert titles == {"a", "b"}


def test_load_documents_missing_folder(tmp_path):
    docs = load_documents_from_folder(tmp_path / "nonexistent")
    assert docs == []
