import asyncio
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# noqa: E402 — импорты после sys.path.insert нужны для доступа к app.*
from app.agents.qa_agent import generate_answer  # noqa: E402
from app.db.session import async_session_maker  # noqa: E402
from app.rag.embeddings import embed_query, embed_texts  # noqa: E402
from app.rag.retriever import search_similar  # noqa: E402

# Стоп-слова — не считаем их в keyword-метриках
STOPWORDS = {
    "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а",
    "то", "все", "она", "так", "его", "но", "да", "ты", "к", "у", "же",
    "вы", "за", "бы", "по", "только", "ее", "мне", "было", "вот", "от",
    "меня", "еще", "нет", "о", "из", "ему", "теперь", "когда", "даже",
    "ну", "вдруг", "ли", "если", "уже", "или", "ни", "быть", "был",
    "него", "до", "вас", "нибудь", "опять", "уж", "вам", "ведь", "там",
    "потом", "себя", "ничего", "ей", "может", "они", "тут", "где",
    "есть", "надо", "ней", "для", "мы", "тебя", "их", "чем", "была",
    "сам", "чтоб", "без", "будто", "чего", "раз", "тоже", "себе",
    "под", "будет", "ж", "тогда", "кто", "этот", "того", "потому",
    "этого", "какой", "совсем", "ним", "здесь", "этом", "один",
    "почти", "мой", "тем", "чтобы", "нее", "были", "куда", "зачем",
    "всех", "никогда", "можно", "при", "наконец", "два", "об",
    "другой", "хоть", "после", "над", "больше", "тот", "через",
    "эти", "нас", "про", "всего", "них", "какая", "много", "разве",
    "три", "эту", "моя", "впрочем", "хорошо", "свою", "этой",
    "перед", "иногда", "лучше", "чуть", "том", "нельзя", "такой",
    "им", "более", "всегда", "конечно", "всю", "между",
}


def tokenize(text: str) -> set[str]:
    """Приводит текст к нижнему регистру, убирает пунктуацию и стоп-слова."""
    words = re.findall(r"\b[а-яёa-z0-9]+\b", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Косинусное сходство двух векторов."""
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


async def evaluate() -> None:
    with open("data/golden_set.json", encoding="utf-8") as f:
        golden_set = json.load(f)

    print(f"Загружено {len(golden_set)} вопросов\n")

    results = []

    async with async_session_maker() as session:
        for i, item in enumerate(golden_set):
            question = item["question"]
            ground_truth = item["ground_truth"]
            expected_contexts = item.get("contexts", [])

            print(f"[{i + 1}/{len(golden_set)}] {question[:60]}...")

            # 1. Поиск в векторной БД
            query_emb = embed_query(question)
            candidates = await search_similar(session, query_emb, top_k=5)
            found_contexts = [c["content"] for c in candidates]

            # 2. Генерация ответа
            context_text = "\n\n".join(found_contexts)
            answer = await generate_answer(question, context_text)

            # ===== МЕТРИКА 1: Semantic similarity =====
            embs = embed_texts([answer, ground_truth], is_query=False)
            semantic_sim = cosine_similarity(embs[0], embs[1])

            # ===== МЕТРИКА 2: Keyword Recall =====
            gt_words = tokenize(ground_truth)
            answer_words = tokenize(answer)
            recall = (
                len(gt_words & answer_words) / len(gt_words) if gt_words else 0.0
            )

            # ===== МЕТРИКА 3: Keyword Precision =====
            precision = (
                len(gt_words & answer_words) / len(answer_words)
                if answer_words
                else 0.0
            )

            # ===== МЕТРИКА 4: Retrieval Hit Rate =====
            expected_words = tokenize(" ".join(expected_contexts))
            found_words = tokenize(" ".join(found_contexts))
            hit = 1.0 if expected_words & found_words else 0.0

            results.append(
                {
                    "question": question,
                    "answer": answer,
                    "ground_truth": ground_truth,
                    "semantic_similarity": round(semantic_sim, 4),
                    "keyword_recall": round(recall, 4),
                    "keyword_precision": round(precision, 4),
                    "retrieval_hit": hit,
                }
            )

    # ===== ИТОГОВЫЕ МЕТРИКИ =====
    n = len(results)
    avg_sem = sum(r["semantic_similarity"] for r in results) / n
    avg_recall = sum(r["keyword_recall"] for r in results) / n
    avg_precision = sum(r["keyword_precision"] for r in results) / n
    avg_hit = sum(r["retrieval_hit"] for r in results) / n

    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ОЦЕНКИ RAG")
    print("=" * 60)
    print(f"Semantic Similarity:  {avg_sem:.4f}")
    print(f"Keyword Recall:       {avg_recall:.4f}")
    print(f"Keyword Precision:    {avg_precision:.4f}")
    print(f"Retrieval Hit Rate:   {avg_hit:.4f}")
    print("=" * 60)

    output_path = "data/rag_evaluation_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "summary": {
                    "semantic_similarity": round(avg_sem, 4),
                    "keyword_recall": round(avg_recall, 4),
                    "keyword_precision": round(avg_precision, 4),
                    "retrieval_hit_rate": round(avg_hit, 4),
                    "total_questions": n,
                },
                "details": results,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"\nДетальные результаты → {output_path}")

    # Разбор провалов
    print("\nПровальные случаи (semantic_similarity < 0.75):")
    fails = [r for r in results if r["semantic_similarity"] < 0.75]
    if not fails:
        print("  Нет провалов — все вопросы отвечены корректно")
    else:
        for r in fails:
            print(f"  - {r['question'][:60]}")
            print(f"    sim={r['semantic_similarity']}, recall={r['keyword_recall']}")


if __name__ == "__main__":
    asyncio.run(evaluate())
