import os
import requests
import tiktoken
import numpy as np
import json
with open('luxun.json','r') as f:
    luxun_data = json.load(f)

# download the tiny shakespeare dataset
# input_file_path = os.path.join(os.path.dirname(__file__), 'input.txt')
# assert os.path.exists(input_file_path), "Make sure input.txt is present in the directory."

# with open(input_file_path, 'r', encoding='utf-8') as f:
#     data = f.read()

data = ''.join([x[-1] for x in luxun_data])
n = len(data)
train_data = data[:int(n*0.9)]
val_data = data[int(n*0.9):]

# encode with tiktoken cl100k_base bpe
enc = tiktoken.get_encoding("cl100k_base")
train_ids = enc.encode_ordinary(train_data)
val_ids = enc.encode_ordinary(val_data)
print(f"train has {len(train_ids):,} tokens")
print(f"val has {len(val_ids):,} tokens")

# export to bin files
train_ids = np.array(train_ids, dtype=np.uint32)
val_ids = np.array(val_ids, dtype=np.uint32)
train_ids.tofile(os.path.join(os.path.dirname(__file__), 'train.bin'))
val_ids.tofile(os.path.join(os.path.dirname(__file__), 'val.bin'))

# save meta info
import pickle
meta = {
    'vocab_size': enc.n_vocab,
    'dtype': 'uint32',
}
with open(os.path.join(os.path.dirname(__file__), 'meta.pkl'), 'wb') as f:
    pickle.dump(meta, f)
print(f"Saved meta.pkl with vocab_size={enc.n_vocab}, dtype=uint32")

# train has 4,530,524 tokens
# val has 498,993 tokens
# python train.py config/train_shakespeare_char.py --dataset=luxun --compile=False --batch_size=32