def load():
    import torch
    torch.set_num_threads(1)
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device='cpu')
    return model

model = load()
print('success')
