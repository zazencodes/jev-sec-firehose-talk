"""Build the stage sample from the Atticus Project's CUAD v1 JSON."""

import json
import sys
from collections import defaultdict
from pathlib import Path

LABELS = {
    "change_of_control": "Change Of Control",
    "non_compete": "Non-Compete",
    "uncapped_liability": "Uncapped Liability",
}

source = json.loads(Path(sys.argv[1]).read_text())
groups = defaultdict(list)
for contract in source["data"]:
    paragraph, = contract["paragraphs"]
    text = " ".join(paragraph["context"].split())
    if len(text.encode()) > 55_000:
        continue
    questions = {row["id"].rsplit("__", 1)[1]: row for row in paragraph["qas"]}
    evidence = {
        key: [" ".join(span["text"].split()) for span in questions[name]["answers"]]
        for key, name in LABELS.items()
    }
    gold = {key: bool(spans) for key, spans in evidence.items()}
    groups[tuple(gold.values())].append(
        {"title": contract["title"], "text": text, "gold": gold, "evidence": evidence}
    )

if len(groups) != 8:
    raise ValueError("Expected examples of all eight combinations of the three CUAD labels")

sample = []
for index, (_, contracts) in enumerate(sorted(groups.items()), 1):
    ordered = sorted(contracts, key=lambda row: (len(row["text"]), row["title"]))
    sample.append({"id": f"C{index}", **ordered[len(ordered) // 2]})

target = Path(__file__).with_name("data") / "cuad-sample.json"
target.write_text(json.dumps(sample, ensure_ascii=False, indent=2) + "\n")
print(f"Saved {len(sample)} contracts to {target}")
