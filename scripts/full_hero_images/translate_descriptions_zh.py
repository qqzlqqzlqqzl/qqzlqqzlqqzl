#!/usr/bin/env python3
"""Translate project descriptions and keywords to Simplified Chinese locally.

Uses Helsinki-NLP/opus-mt-en-zh on the GitHub Actions runner. Existing Chinese
text remains unchanged. Non-English, non-Chinese text is preserved and marked
for later review rather than mistranslated by the English model.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import langid
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

MODEL_NAME = "Helsinki-NLP/opus-mt-en-zh"
TARGET_PREFIX = ">>cmn_Hans<< "
CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")


def has_chinese(text: str) -> bool:
    if not text:
        return False
    count = len(CJK_RE.findall(text))
    return count >= 2 or count / max(1, len(text)) >= 0.08


def normalize_text(text: str, max_chars: int) -> str:
    text = re.sub(r"\s+", " ", (text or "")).strip()
    return text[:max_chars]


def should_translate(text: str) -> tuple[bool, str]:
    if not text:
        return False, "empty"
    if has_chinese(text):
        return False, "already-zh"
    alpha = sum(ch.isalpha() for ch in text)
    if alpha < 3:
        return False, "low-text"
    language, confidence = langid.classify(text)
    if language == "en":
        return True, f"en:{confidence:.2f}"
    ascii_ratio = sum(ord(ch) < 128 for ch in text) / max(1, len(text))
    if ascii_ratio > 0.96 and len(text.split()) >= 3:
        return True, f"ascii-fallback:{language}:{confidence:.2f}"
    return False, f"keep-non-en:{language}:{confidence:.2f}"


def translate_batches(
    values: list[str],
    tokenizer: AutoTokenizer,
    model: AutoModelForSeq2SeqLM,
    batch_size: int,
    max_input_tokens: int,
) -> list[str]:
    outputs: list[str] = []
    model.eval()
    for start in range(0, len(values), batch_size):
        batch = values[start:start + batch_size]
        prefixed = [TARGET_PREFIX + item for item in batch]
        encoded = tokenizer(
            prefixed,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=max_input_tokens,
        )
        with torch.inference_mode():
            generated = model.generate(
                **encoded,
                max_new_tokens=256,
                num_beams=2,
                early_stopping=True,
            )
        decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
        outputs.extend(re.sub(r"\s+", " ", text).strip() for text in decoded)
        done = min(len(values), start + len(batch))
        print(f"translation batch {done}/{len(values)}", flush=True)
    return outputs


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-csv", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--batch-size", type=int, default=24)
    args = parser.parse_args()

    torch.set_num_threads(max(1, min(4, torch.get_num_threads())))
    source = Path(args.source_csv)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = read_rows(source)

    print(f"Loading translation model {MODEL_NAME}", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

    description_inputs: list[str] = []
    description_indices: list[int] = []
    keyword_inputs: list[str] = []
    keyword_indices: list[int] = []
    result_rows: list[dict[str, str]] = []

    for index, row in enumerate(rows):
        description = normalize_text(row.get("description", ""), 580)
        keywords = normalize_text(row.get("keywords", ""), 260)
        translate_description, description_status = should_translate(description)
        translate_keywords, keyword_status = should_translate(keywords)
        result_rows.append({
            "project_id": row.get("project_id", ""),
            "description_zh": description,
            "keywords_zh": keywords,
            "description_translation_status": description_status,
            "keywords_translation_status": keyword_status,
        })
        if translate_description:
            description_indices.append(index)
            description_inputs.append(description)
        if translate_keywords:
            keyword_indices.append(index)
            keyword_inputs.append(keywords)

    print(json.dumps({
        "rows": len(rows),
        "description_translate": len(description_inputs),
        "keywords_translate": len(keyword_inputs),
    }, ensure_ascii=False), flush=True)

    translated_descriptions = translate_batches(
        description_inputs, tokenizer, model, max(1, args.batch_size), 256
    )
    for index, translated in zip(description_indices, translated_descriptions):
        if translated:
            result_rows[index]["description_zh"] = translated
            result_rows[index]["description_translation_status"] = "translated-en-zh"

    translated_keywords = translate_batches(
        keyword_inputs, tokenizer, model, max(1, args.batch_size), 128
    )
    for index, translated in zip(keyword_indices, translated_keywords):
        if translated:
            result_rows[index]["keywords_zh"] = translated
            result_rows[index]["keywords_translation_status"] = "translated-en-zh"

    fields = [
        "project_id", "description_zh", "keywords_zh",
        "description_translation_status", "keywords_translation_status",
    ]
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(result_rows)

    summary = {
        "rows": len(result_rows),
        "translated_descriptions": sum(
            1 for row in result_rows
            if row["description_translation_status"] == "translated-en-zh"
        ),
        "translated_keywords": sum(
            1 for row in result_rows
            if row["keywords_translation_status"] == "translated-en-zh"
        ),
        "model": MODEL_NAME,
    }
    output.with_suffix(".summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
