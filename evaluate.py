"""Send the sample tickets to the n8n webhook and report how well they were triaged.

Usage:
  python evaluate.py <webhook-url>                 all tickets -> results.md
  python evaluate.py <webhook-url> --out NAME.md   all tickets -> NAME.md
  python evaluate.py <webhook-url> --first N       first N tickets, raw replies, nothing written
Standard library only.
"""

import argparse
import json
import time
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
PAUSE_SECONDS = 4  # stay under free-tier rate limits


def post(url: str, payload: dict) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def load_tickets() -> list[dict]:
    text = (HERE / "tickets.jsonl").read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def ratio(part: int, whole: int) -> str:
    return f"{part}/{whole}" + (f" ({100 * part / whole:.0f}%)" if whole else "")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--out", default="results.md")
    parser.add_argument("--first", type=int)
    parser.add_argument("--label", default="")
    args = parser.parse_args()
    tickets = load_tickets()

    if args.first:
        for ticket in tickets[: args.first]:
            reply = post(args.url, {"ticket_id": ticket["ticket_id"], "text": ticket["text"]})
            print(json.dumps(reply, ensure_ascii=False, indent=2))
        return 0

    rows = []
    for ticket in tickets:
        try:
            result = post(args.url, {"ticket_id": ticket["ticket_id"], "text": ticket["text"]})
        except Exception as error:  # keep going so one failure does not hide the rest
            result = {"problems": f"request_failed: {error}", "needs_review": True}
        rows.append((ticket, result))
        time.sleep(PAUSE_SECONDS)

    total = len(rows)
    cat_ok = sum(r.get("category") == t["expected_category"] for t, r in rows)
    pri_ok = sum(r.get("priority") == t["expected_priority"] for t, r in rows)
    reviewed = [(t, r) for t, r in rows if r.get("needs_review")]
    auto = [(t, r) for t, r in rows if not r.get("needs_review")]
    auto_ok = sum(r.get("category") == t["expected_category"] for t, r in auto)
    wrong = [(t, r) for t, r in rows if r.get("category") != t["expected_category"]]
    wrong_caught = sum(bool(r.get("needs_review")) for _, r in wrong)
    llm_failed = sum("llm_request_failed" in str(r.get("problems")) for _, r in rows)

    by_category, by_kind = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0])
    confusions = Counter()
    for ticket, result in rows:
        correct = result.get("category") == ticket["expected_category"]
        for bucket, key in ((by_category, ticket["expected_category"]),
                            (by_kind, ticket.get("kind", "plain"))):
            bucket[key][0] += correct
            bucket[key][1] += 1
        if not correct:
            confusions[(ticket["expected_category"], result.get("category") or "(none)")] += 1

    lines = [
        f"# Evaluation results{' - ' + args.label if args.label else ''}",
        "",
        f"- Tickets: {total}",
        f"- Category correct: {ratio(cat_ok, total)}",
        f"- Priority correct: {ratio(pri_ok, total)}",
        f"- Sent to human review: {ratio(len(reviewed), total)}",
        f"- Category correct among auto-routed tickets: {ratio(auto_ok, len(auto))}",
        f"- Wrong categories caught by review: {ratio(wrong_caught, len(wrong))}",
        f"- LLM call failures: {llm_failed}",
        "",
        "## Category accuracy by expected category",
        "",
        "| Category | Correct |",
        "|---|---|",
        *[f"| {k} | {ratio(*v)} |" for k, v in sorted(by_category.items())],
        "",
        "## Category accuracy by ticket kind",
        "",
        "| Kind | Correct |",
        "|---|---|",
        *[f"| {k} | {ratio(*v)} |" for k, v in sorted(by_kind.items())],
        "",
        "## Confusions (expected -> got)",
        "",
        *([f"- {a} -> {b}: {n}" for (a, b), n in confusions.most_common()] or ["- none"]),
        "",
        "## All tickets",
        "",
        "| Ticket | Kind | Expected | Got | OK | Exp. priority | Got | OK | Route | Problems |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for ticket, result in rows:
        cat = result.get("category") == ticket["expected_category"]
        pri = result.get("priority") == ticket["expected_priority"]
        lines.append(
            f"| {ticket['ticket_id']} | {ticket.get('kind', 'plain')} "
            f"| {ticket['expected_category']} | {result.get('category') or '-'} "
            f"| {'yes' if cat else 'NO'} | {ticket['expected_priority']} "
            f"| {result.get('priority') or '-'} | {'yes' if pri else 'NO'} "
            f"| {result.get('route')} | {result.get('problems') or '-'} |"
        )
    lines.append("")
    (HERE / args.out).write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:9]))
    print("details written to", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
