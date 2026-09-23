from app.services.evaluation import EvaluationCase, evaluate_retrieval
from app.services.retrieval import RetrievalHit

def test_retrieval_evaluation_reports_recall_and_mrr() -> None:
    cases = [EvaluationCase("q1", {"b"}), EvaluationCase("q2", {"x"})]
    results = [
        [RetrievalHit("a", 1, "s", "d"), RetrievalHit("b", .8, "s", "d")],
        [RetrievalHit("x", 1, "s", "d")],
    ]
    result = evaluate_retrieval(cases, results)
    assert result.recall_at_k == 1.0
    assert result.mrr == .75
