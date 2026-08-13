"""Tests for sentence splitter."""
from backend.app.core.nlp.sentence_splitter import split_sentences

def test_split_sentences():
    text = "This is the first sentence. And here is the second one! What about a third sentence? Finally, the fourth one ends here."
    sentences = split_sentences(text)
    
    assert len(sentences) == 4
    assert sentences[0].startswith("This is")
    assert sentences[1].startswith("And here")
    assert sentences[2].startswith("What about")
    assert sentences[3].startswith("Finally")

def test_short_sentences_filtered():
    text = "This is long enough to be kept. Short! Too tiny. This one is also long enough to stay."
    sentences = split_sentences(text)
    assert len(sentences) == 2
