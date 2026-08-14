def precision_at_k(predicted_ids: list[str], true_ids: set[str], k: int) -> float:
    """
    Computes precision at k.
    """
    if not predicted_ids or k <= 0:
        return 0.0
    
    top_k = predicted_ids[:k]
    relevant_in_top_k = sum(1 for pid in top_k if pid in true_ids)
    
    return relevant_in_top_k / len(top_k)

def recall_at_k(predicted_ids: list[str], true_ids: set[str], k: int) -> float:
    """
    Computes recall at k.
    """
    if not true_ids or k <= 0:
        return 0.0
        
    top_k = predicted_ids[:k]
    relevant_in_top_k = sum(1 for pid in top_k if pid in true_ids)
    
    return relevant_in_top_k / len(true_ids)

def f1(precision: float, recall: float) -> float:
    """
    Computes the F1 score.
    """
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)

def inter_annotator_agreement_simple(labels1: dict, labels2: dict) -> dict:
    """
    Computes simple percent agreement between two sets of labels.
    Expected dict format: { "item_id": True/False }
    """
    common_keys = set(labels1.keys()).intersection(set(labels2.keys()))
    if not common_keys:
        return {"agreement": 0.0, "total_common": 0}
        
    matches = sum(1 for k in common_keys if labels1[k] == labels2[k])
    
    return {
        "agreement": matches / len(common_keys),
        "total_common": len(common_keys)
    }
