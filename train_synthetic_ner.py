"""
Optional: Fine-tune a lightweight token classification model (DistilRoBERTa)
on synthetic PII generated with Faker. This script is minimal and CPU-friendly
for demo purposes (few epochs).

Usage:
  python train_synthetic_ner.py --outdir models/pii-ner-mini
"""
import os
import random
import argparse
from typing import List, Dict
from faker import Faker
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer, DataCollatorForTokenClassification
import numpy as np

fake = Faker()

LABELS = ["O", "B-EMAIL", "I-EMAIL", "B-PHONE", "I-PHONE", "B-NAME", "I-NAME"]
label2id = {l:i for i,l in enumerate(LABELS)}
id2label = {i:l for l,i in label2id.items()}

def gen_sentence() -> str:
    name = fake.name()
    email = fake.email()
    phone = fake.phone_number()
    templates = [
        f"Contact {name} at {email} or call {phone}.",
        f"{name} can be reached via {email}.",
        f"Phone for {name} is {phone}. Email: {email}.",
    ]
    return random.choice(templates)

def tokenize_and_align_labels(tokenizer, texts: List[str]) -> Dict:
    tokenized = tokenizer(texts, truncation=True, padding=True, return_offsets_mapping=True)
    labels = []
    for i, text in enumerate(texts):
        ents = []
        # naive span finding (demo only)
        name = next((w for w in text.split() if "@" not in w and any(c.isalpha() for c in w)), None)
        email = next((w for w in text.split() if "@" in w), None)
        phone = next((w for w in text.split() if any(c.isdigit() for c in w) and "-" in w or "(" in w), None)
        ents = []
        if email:
            start = text.find(email); end = start + len(email); ents.append(("EMAIL", start, end))
        if phone:
            start = text.find(phone); end = start + len(phone); ents.append(("PHONE", start, end))
        if name:
            start = text.find(name); end = start + len(name); ents.append(("NAME", start, end))

        word_ids = tokenized.word_ids(i)
        offsets = tokenized["offset_mapping"][i]
        example_labels = []
        for idx, w_id in enumerate(word_ids):
            if w_id is None:
                example_labels.append(-100); continue
            start, end = offsets[idx]
            tag = "O"
            for ent, s, e in ents:
                if start >= s and end <= e:
                    prefix = "B" if start == s else "I"
                    tag = f"{prefix}-{ent}"
                    break
            example_labels.append(label2id.get(tag, 0))
        labels.append(example_labels)
    tokenized.pop("offset_mapping")
    tokenized["labels"] = labels
    return tokenized

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=str, default="models/pii-ner-mini")
    args = parser.parse_args()

    texts = [gen_sentence() for _ in range(500)]
    tokenizer = AutoTokenizer.from_pretrained("distilroberta-base")
    tokenized = tokenize_and_align_labels(tokenizer, texts)

    model = AutoModelForTokenClassification.from_pretrained(
        "distilroberta-base",
        num_labels=len(LABELS),
        id2label=id2label,
        label2id=label2id,
    )

    collator = DataCollatorForTokenClassification(tokenizer)
    args_tr = TrainingArguments(
        output_dir=args.outdir,
        per_device_train_batch_size=8,
        num_train_epochs=1,
        learning_rate=5e-5,
        logging_steps=20,
        save_steps=200,
        report_to=[],
    )

    trainer = Trainer(
        model=model,
        args=args_tr,
        train_dataset=Dataset.from_dict(tokenized),
        data_collator=collator,
        tokenizer=tokenizer,
    )
    trainer.train()
    trainer.save_model(args.outdir)
    tokenizer.save_pretrained(args.outdir)

if __name__ == "__main__":
    main()
