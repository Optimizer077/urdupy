import torch
from transformers import BertConfig, BertModel

# صرف local config؛ نہ tokenizer چاہیے نہ pretrained checkpoint
CONFIG = BertConfig(vocab_size=16, hidden_size=8, num_hidden_layers=1,
    num_attention_heads=2, intermediate_size=16, max_position_embeddings=16,
    hidden_dropout_prob=0.0, attention_probs_dropout_prob=0.0)
MODEL = BertModel(CONFIG).cpu().eval()
IDS = torch.tensor([[1, 2, 3]], dtype=torch.long, device="cpu")
with torch.no_grad():
    RESULT = MODEL(input_ids=IDS, attention_mask=torch.ones_like(IDS)).last_hidden_state
print(list(RESULT.shape), bool(torch.isfinite(RESULT).all()))
