from backend.app.core.eval.metrics import precision_at_k, recall_at_k, f1, inter_annotator_agreement_simple

def test_precision_at_k():
    predicted = ["A", "B", "C", "D"]
    true_ids = {"B", "D", "E"}
    
    # p@2 (A, B) -> B is relevant -> 1/2
    assert precision_at_k(predicted, true_ids, 2) == 0.5
    
    # p@4 (A, B, C, D) -> B, D relevant -> 2/4
    assert precision_at_k(predicted, true_ids, 4) == 0.5
    
    # Empty
    assert precision_at_k([], true_ids, 2) == 0.0

def test_recall_at_k():
    predicted = ["A", "B", "C", "D"]
    true_ids = {"B", "D", "E"}
    
    # r@2 (A, B) -> B relevant -> 1 out of 3 true
    assert recall_at_k(predicted, true_ids, 2) == 1/3
    
    # r@4 (A, B, C, D) -> B, D relevant -> 2 out of 3 true
    assert recall_at_k(predicted, true_ids, 4) == 2/3

def test_f1():
    assert f1(1.0, 1.0) == 1.0
    assert f1(0.0, 1.0) == 0.0
    assert f1(0.5, 0.5) == 0.5

def test_inter_annotator_agreement_simple():
    l1 = {"item1": True, "item2": False, "item3": True}
    l2 = {"item1": True, "item2": True, "item3": True}
    
    res = inter_annotator_agreement_simple(l1, l2)
    assert res["total_common"] == 3
    assert res["agreement"] == 2/3
