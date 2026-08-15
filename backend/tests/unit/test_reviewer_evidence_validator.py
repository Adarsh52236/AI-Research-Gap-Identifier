from backend.app.core.reviewer.evidence_validator import validate_and_filter_issues
from backend.app.db.schemas import ReviewLLMOutput, ReviewIssue, ReviewEvidence

def test_evidence_validator_drops_hallucinations():
    extracted_text = "This paper introduces a novel approach to graph neural networks. We use a dataset of 100k nodes."
    
    # 2 issues: one valid, one hallucinated
    valid_evidence = ReviewEvidence(
        evidence_id="e1",
        anchor_phrase="novel approach to graph neural networks",
        quote="This paper introduces a novel approach to graph neural networks."
    )
    invalid_evidence = ReviewEvidence(
        evidence_id="e2",
        anchor_phrase="transformers are all you need",
        quote="We use a dataset of 100k nodes and transformers are all you need."
    )
    
    issue1 = ReviewIssue(
        issue_id="i1", severity="minor", issue="none", solution="none", evidence=valid_evidence, issue_type="writing"
    )
    issue2 = ReviewIssue(
        issue_id="i2", severity="major", issue="none", solution="none", evidence=invalid_evidence, issue_type="novelty"
    )
    
    llm_output = ReviewLLMOutput(
        issues=[issue1, issue2],
        overall_issues=[],
        overall_solutions=[]
    )
    
    filtered_output, dropped = validate_and_filter_issues(llm_output, extracted_text)
    
    assert dropped == 1
    assert len(filtered_output.issues) == 1
    assert filtered_output.issues[0].issue_id == "i1"
