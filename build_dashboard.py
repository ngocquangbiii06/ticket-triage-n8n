"""Build a Power BI project (PBIP) from the evaluation result files.

Run:  python build_dashboard.py
Writes dashboard/TicketTriage.pbip (+ report and semantic model folders) and
dashboard/ticket_results.csv. Open the .pbip in Power BI Desktop and press Refresh.
The data is embedded in the model, so the project has no external data source.
"""

import base64
import csv
import hashlib
import json
import shutil
import uuid
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "dashboard"
NAME = "TicketTriage"

# (label shown in charts, results file). Labels sort alphabetically in run order.
RUNS = [
    ("1 · v1 baseline", "results_v1_60tickets.md"),
    ("2 · v2 run 1", "results_v2_60tickets.md"),
    ("3 · v2 run 2", "results_v2_60tickets_run2.md"),
    ("4 · v3 rejected", "results_v3_60tickets.md"),
]
CURRENT_RUN = "3 · v2 run 2"
PRIORITY_RANK = {"low": 0, "medium": 1, "high": 2}

NAVY, SLATE, BORDER = "#142D4E", "#334155", "#D9E2EC"
TEAL, RED, AMBER, BLUE = "#087F72", "#B54734", "#B7791F", "#2B6CB0"


# ---------------------------------------------------------------- data


def parse_results(path: Path) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("| Ticket |"))
    rows = []
    for line in lines[start + 2 :]:
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        ticket, kind, expected, got, cat_ok, exp_pri, got_pri, pri_ok, route, problems = cells
        rows.append(
            {
                "ticket_id": ticket,
                "kind": kind,
                "expected_category": expected,
                "got_category": got,
                "category_ok": int(cat_ok == "yes"),
                "expected_priority": exp_pri,
                "got_priority": got_pri,
                "priority_ok": int(pri_ok == "yes"),
                "route": route,
                "problems": "" if problems == "-" else problems,
            }
        )
    return rows


def load_rows() -> list[dict]:
    texts = {
        t["ticket_id"]: t["text"]
        for t in map(
            json.loads,
            filter(str.strip, (HERE / "tickets.jsonl").read_text(encoding="utf-8").splitlines()),
        )
    }
    out = []
    for run, filename in RUNS:
        for row in parse_results(HERE / filename):
            needs_review = int(row["route"] == "human_review")
            reason = row["problems"].split(",")[0].split(":")[0].strip() if needs_review else ""
            got, exp = PRIORITY_RANK.get(row["got_priority"]), PRIORITY_RANK[row["expected_priority"]]
            if got is None or got == exp:
                priority_error = "correct" if got == exp else "no answer"
            else:
                priority_error = "over-escalated" if got > exp else "under-escalated"
            if row["category_ok"]:
                outcome = "correct, reviewed" if needs_review else "correct, auto-routed"
            else:
                outcome = "wrong, caught by review" if needs_review else "wrong, auto-routed"
            out.append(
                {
                    "run": run,
                    **row,
                    "needs_review": needs_review,
                    "review_reason": reason,
                    "priority_error": priority_error,
                    "outcome": outcome,
                    "ticket_text": texts.get(row["ticket_id"], ""),
                }
            )
    return out


# ---------------------------------------------------------------- semantic model (TMDL)

# (model column, source key, type)
RESULT_COLUMNS = [
    ("Run", "run", "text"),
    ("Ticket", "ticket_id", "text"),
    ("Kind", "kind", "text"),
    ("Expected Category", "expected_category", "text"),
    ("Predicted Category", "got_category", "text"),
    ("CategoryOK", "category_ok", "int"),
    ("Expected Priority", "expected_priority", "text"),
    ("Predicted Priority", "got_priority", "text"),
    ("PriorityOK", "priority_ok", "int"),
    ("Priority Error", "priority_error", "text"),
    ("Route", "route", "text"),
    ("NeedsReview", "needs_review", "int"),
    ("Review Reason", "review_reason", "text"),
    ("Outcome", "outcome", "text"),
    ("Problems", "problems", "text"),
    ("Ticket Text", "ticket_text", "text"),
]
ATTENTION_COLUMNS = [
    ("Ticket", "ticket_id", "text"),
    ("Kind", "kind", "text"),
    ("Expected", "expected_category", "text"),
    ("Predicted", "got_category", "text"),
    ("Exp. priority", "expected_priority", "text"),
    ("Pred. priority", "got_priority", "text"),
    ("Outcome", "outcome", "text"),
    ("Why flagged", "problems", "text"),
    ("Ticket Text", "ticket_text", "text"),
]

T = "'TicketResults'"
CUR = f'{T}[Run] = "{CURRENT_RUN}"'
MEASURES = [
    ("Tickets", f"COUNTROWS({T})", "0"),
    ("Category Accuracy", f"DIVIDE(SUM({T}[CategoryOK]), [Tickets])", "0%"),
    ("Priority Accuracy", f"DIVIDE(SUM({T}[PriorityOK]), [Tickets])", "0%"),
    ("Review Rate", f"DIVIDE(SUM({T}[NeedsReview]), [Tickets])", "0%"),
    (
        "Wrong Not Reviewed",
        f"COALESCE(CALCULATE([Tickets], {T}[CategoryOK] = 0, {T}[NeedsReview] = 0), 0)",
        "0",
    ),
    (
        "Wrong Caught",
        f"COALESCE(CALCULATE([Tickets], {T}[CategoryOK] = 0, {T}[NeedsReview] = 1), 0)",
        "0",
    ),
    (
        "Over-escalated",
        f'COALESCE(CALCULATE([Tickets], {T}[Priority Error] = "over-escalated"), 0)',
        "0",
    ),
    (
        "Under-escalated",
        f'COALESCE(CALCULATE([Tickets], {T}[Priority Error] = "under-escalated"), 0)',
        "0",
    ),
    ("Tickets (current)", f"CALCULATE([Tickets], {CUR})", "0"),
    ("Category Accuracy (current)", f"CALCULATE([Category Accuracy], {CUR})", "0%"),
    ("Priority Accuracy (current)", f"CALCULATE([Priority Accuracy], {CUR})", "0%"),
    ("Review Rate (current)", f"CALCULATE([Review Rate], {CUR})", "0%"),
    ("Wrong Not Reviewed (current)", f"CALCULATE([Wrong Not Reviewed], {CUR})", "0"),
    (
        "Reviewed (current)",
        f"VAR n = CALCULATE(SUM({T}[NeedsReview]), {CUR}) RETURN IF(n = 0, BLANK(), n)",
        "0",
    ),
]


def tag() -> str:
    return str(uuid.uuid4())


def m_partition(table: str, columns: list, rows: list[dict]) -> str:
    data = [[str(row[key]) for _, key, _ in columns] for row in rows]
    blob = base64.b64encode(json.dumps(data, ensure_ascii=False).encode("utf-8")).decode("ascii")
    names = ", ".join(f'"{name}"' for name, _, _ in columns)
    types = ", ".join(
        f'{{"{name}", {"Int64.Type" if kind == "int" else "type text"}}}' for name, _, kind in columns
    )
    return (
        f"\tpartition {table} = m\n"
        "\t\tmode: import\n"
        "\t\tsource =\n"
        "\t\t\t\tlet\n"
        f'\t\t\t\t    Rows = Json.Document(Binary.FromText("{blob}", BinaryEncoding.Base64)),\n'
        f"\t\t\t\t    Source = Table.FromRows(Rows, {{{names}}}),\n"
        f'\t\t\t\t    Typed = Table.TransformColumnTypes(Source, {{{types}}}, "en-US")\n'
        "\t\t\t\tin\n"
        "\t\t\t\t    Typed\n"
    )


def quote(name: str) -> str:
    return f"'{name}'" if any(ch in name for ch in " .()-%") else name


def table_tmdl(table: str, columns: list, rows: list[dict], measures=()) -> str:
    parts = [f"table {table}\n\tlineageTag: {tag()}\n"]
    for name, expression, fmt in measures:
        parts.append(
            f"\tmeasure {quote(name)} = {expression}\n"
            f"\t\tformatString: {fmt}\n"
            f"\t\tlineageTag: {tag()}\n"
        )
    for name, _, kind in columns:
        hidden = "\t\tisHidden\n" if kind == "int" else ""
        parts.append(
            f"\tcolumn {quote(name)}\n"
            f"\t\tdataType: {'int64' if kind == 'int' else 'string'}\n"
            f"{hidden}"
            f"\t\tlineageTag: {tag()}\n"
            "\t\tsummarizeBy: none\n"
            f"\t\tsourceColumn: {name}\n"
        )
    parts.append(m_partition(table, columns, rows))
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------- report (PBIR)

VISUAL_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/"
    "visualContainer/2.1.0/schema.json"
)


def lit(value: str) -> dict:
    return {"expr": {"Literal": {"Value": value}}}


def colour(hex_code: str) -> dict:
    return {"solid": {"color": lit(f"'{hex_code}'")}}


def container(title: str | None) -> dict:
    title_props = {"show": lit("false")}
    if title:
        title_props = {
            "show": lit("true"),
            "text": lit("'" + title.replace("'", "''") + "'"),
            "fontSize": lit("13D"),
            "fontColor": colour(NAVY),
        }
    return {
        "title": [{"properties": title_props}],
        "background": [
            {"properties": {"show": lit("true"), "color": colour("#FFFFFF"), "transparency": lit("0D")}}
        ],
        "border": [
            {
                "properties": {
                    "show": lit("true"),
                    "color": colour(BORDER),
                    "radius": lit("8D"),
                    "width": lit("1D"),
                }
            }
        ],
    }


def measure_field(name: str, fmt: str | None = None) -> dict:
    field = {
        "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "TicketResults"}}, "Property": name}},
        "queryRef": f"TicketResults.{name}",
        "nativeQueryRef": name,
    }
    if fmt:
        field["format"] = fmt
    return field


def column_field(table: str, name: str) -> dict:
    return {
        "field": {"Column": {"Expression": {"SourceRef": {"Entity": table}}, "Property": name}},
        "queryRef": f"{table}.{name}",
        "nativeQueryRef": name,
    }


def visual_id(seed: str) -> str:
    return hashlib.sha1(seed.encode()).hexdigest()[:20]


def base(seed: str, x: int, y: int, w: int, h: int, body: dict) -> dict:
    return {
        "$schema": VISUAL_SCHEMA,
        "name": visual_id(seed),
        "position": {"x": x, "y": y, "z": 0, "height": h, "width": w, "tabOrder": 0},
        "visual": {**body, "drillFilterOtherVisuals": False},
    }


def textbox(seed, x, y, w, h, heading, sub) -> dict:
    def run(text, size, weight, color):
        return {
            "textRuns": [
                {
                    "value": text,
                    "textStyle": {
                        "fontFamily": "Segoe UI",
                        "fontSize": size,
                        "fontWeight": weight,
                        "color": color,
                    },
                }
            ],
            "horizontalTextAlignment": "left",
        }

    paragraphs = [run(heading, "20pt", "bold", NAVY), run(sub, "10pt", "normal", SLATE)]
    return base(
        seed, x, y, w, h,
        {
            "visualType": "textbox",
            "objects": {"general": [{"properties": {"paragraphs": paragraphs}}]},
            "visualContainerObjects": container(None),
        },
    )


def card(seed, x, y, w, h, title, measure, fmt) -> dict:
    return base(
        seed, x, y, w, h,
        {
            "visualType": "cardVisual",
            "query": {"queryState": {"Data": {"projections": [measure_field(measure, fmt)]}}},
            "visualContainerObjects": container(title),
            "objects": {
                "value": [
                    {
                        "selector": {"id": "default"},
                        "properties": {
                            "fontSize": lit("28D"),
                            "labelDisplayUnits": lit("'0'"),
                            "customFormatString": lit(f"'{fmt}'"),
                        },
                    }
                ],
                # The container title already names the card; hide the measure-name label.
                "label": [{"selector": {"id": "default"}, "properties": {"show": lit("false")}}],
            },
        },
    )


def chart(seed, x, y, w, h, title, kind, category, measures, fmt, fill) -> dict:
    return base(
        seed, x, y, w, h,
        {
            "visualType": kind,
            "query": {
                "queryState": {
                    "Category": {"projections": [column_field("TicketResults", category)]},
                    "Y": {"projections": [measure_field(m, fmt) for m in measures]},
                }
            },
            "visualContainerObjects": container(title),
            "objects": {
                "labels": [
                    {
                        "properties": {
                            "show": lit("true"),
                            "labelDisplayUnits": lit("'0'"),
                            "valueCustomFormatString": lit(f"'{fmt}'"),
                        }
                    }
                ],
                "dataPoint": [{"properties": {"fill": colour(fill)}}],
            },
        },
    )


def table(seed, x, y, w, h, title, entity, columns) -> dict:
    wrap = [{"properties": {"wordWrap": lit("true")}}]
    return base(
        seed, x, y, w, h,
        {
            "visualType": "tableEx",
            "query": {
                "queryState": {"Values": {"projections": [column_field(entity, c) for c in columns]}}
            },
            "visualContainerObjects": container(title),
            "objects": {"columnHeaders": wrap, "values": wrap},
        },
    )


def pages() -> list[tuple[str, str, list[dict]]]:
    c = CURRENT_RUN.split("·")[1].strip()
    p1 = [
        textbox(
            "p1-title", 24, 16, 1232, 80,
            "Ticket triage: prompt versions compared",
            "60 synthetic fulfilment tickets per run · model openai/gpt-oss-20b on Groq · "
            f"cards show the deployed version ({c}) · expected labels written by hand",
        ),
        card("p1-c1", 24, 108, 232, 104, "Tickets per run", "Tickets (current)", "0"),
        card("p1-c2", 274, 108, 232, 104, "Category correct", "Category Accuracy (current)", "0%"),
        card("p1-c3", 524, 108, 232, 104, "Priority correct", "Priority Accuracy (current)", "0%"),
        card("p1-c4", 774, 108, 232, 104, "Sent to human review", "Review Rate (current)", "0%"),
        card("p1-c5", 1024, 108, 232, 104, "Wrong and not reviewed", "Wrong Not Reviewed (current)", "0"),
        chart("p1-cat", 24, 228, 608, 268, "Category accuracy by version", "columnChart",
              "Run", ["Category Accuracy"], "0%", TEAL),
        chart("p1-pri", 648, 228, 608, 268, "Priority accuracy by version", "columnChart",
              "Run", ["Priority Accuracy"], "0%", BLUE),
        chart("p1-wrong", 24, 512, 608, 268,
              "Wrong category that reached a team without review (lower is better)",
              "columnChart", "Run", ["Wrong Not Reviewed"], "0", RED),
        chart("p1-review", 648, 512, 608, 268, "Share of tickets sent to human review",
              "columnChart", "Run", ["Review Rate"], "0%", AMBER),
    ]
    p2 = [
        textbox(
            "p2-title", 24, 16, 1232, 80,
            f"Deployed version in detail ({c})",
            "Where the workflow is right, where it is wrong, and what the validator sent to a person",
        ),
        chart("p2-cat", 24, 108, 400, 300, "Category accuracy by expected category", "barChart",
              "Expected Category", ["Category Accuracy (current)"], "0%", TEAL),
        chart("p2-kind", 440, 108, 400, 300, "Category accuracy by ticket kind", "barChart",
              "Kind", ["Category Accuracy (current)"], "0%", TEAL),
        chart("p2-reason", 856, 108, 400, 300, "Why tickets went to human review", "barChart",
              "Review Reason", ["Reviewed (current)"], "0", AMBER),
        table("p2-table", 24, 424, 1232, 356,
              "Tickets needing attention: reviewed, wrong category, or wrong priority",
              "Attention", [name for name, _, _ in ATTENTION_COLUMNS]),
    ]
    return [("Version comparison", "p-versions", p1), ("Deployed version", "p-detail", p2)]


# ---------------------------------------------------------------- write


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def platform(kind: str) -> dict:
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/"
        "platformProperties/2.0.0/schema.json",
        "metadata": {"type": kind, "displayName": NAME},
        "config": {"version": "2.0", "logicalId": str(uuid.uuid4())},
    }


def main() -> None:
    rows = load_rows()
    attention = [
        r for r in rows
        if r["run"] == CURRENT_RUN and (r["needs_review"] or not r["category_ok"] or not r["priority_ok"])
    ]

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    with (OUT / "ticket_results.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    write_json(
        OUT / f"{NAME}.pbip",
        {"version": "1.0", "artifacts": [{"report": {"path": f"{NAME}.Report"}}], "settings": {}},
    )
    (OUT / ".gitignore").write_text("**/.pbi/localSettings.json\n**/.pbi/cache.abf\n", encoding="utf-8")

    model = OUT / f"{NAME}.SemanticModel"
    write_json(model / ".platform", platform("SemanticModel"))
    write_json(model / "definition.pbism", {"version": "4.2", "settings": {}})
    definition = model / "definition"
    (definition / "tables").mkdir(parents=True)
    (definition / "database.tmdl").write_text("database\n\tcompatibilityLevel: 1606\n\n", encoding="utf-8")
    (definition / "model.tmdl").write_text(
        "model Model\n"
        "\tculture: en-US\n"
        "\tdefaultPowerBIDataSourceVersion: powerBI_V3\n"
        "\tsourceQueryCulture: en-US\n"
        "\tdataAccessOptions\n"
        "\t\tlegacyRedirects\n"
        "\t\treturnErrorValuesAsNull\n\n"
        'annotation PBI_QueryOrder = ["TicketResults", "Attention"]\n\n'
        "annotation __PBI_TimeIntelligenceEnabled = 0\n\n"
        'annotation PBI_ProTooling = ["DevMode"]\n\n'
        "ref table TicketResults\n"
        "ref table Attention\n\n",
        encoding="utf-8",
    )
    (definition / "tables" / "TicketResults.tmdl").write_text(
        table_tmdl("TicketResults", RESULT_COLUMNS, rows, MEASURES), encoding="utf-8"
    )
    (definition / "tables" / "Attention.tmdl").write_text(
        table_tmdl("Attention", ATTENTION_COLUMNS, attention), encoding="utf-8"
    )

    report = OUT / f"{NAME}.Report"
    write_json(report / ".platform", platform("Report"))
    write_json(
        report / "definition.pbir",
        {"version": "4.0", "datasetReference": {"byPath": {"path": f"../{NAME}.SemanticModel"}}},
    )
    schema_root = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/"
    write_json(
        report / "definition" / "report.json",
        {
            "$schema": schema_root + "report/3.3.0/schema.json",
            "themeCollection": {},
            "settings": {"useEnhancedTooltips": False},
        },
    )
    write_json(
        report / "definition" / "version.json",
        {"$schema": schema_root + "versionMetadata/1.0.0/schema.json", "version": "2.0.0"},
    )
    page_ids = []
    for display, seed, visuals in pages():
        page_id = visual_id(seed)
        page_ids.append(page_id)
        folder = report / "definition" / "pages" / page_id
        write_json(
            folder / "page.json",
            {
                "$schema": schema_root + "page/2.0.0/schema.json",
                "name": page_id,
                "displayName": display,
                "displayOption": "FitToPage",
                "width": 1280,
                "height": 800,
            },
        )
        for visual in visuals:
            write_json(folder / "visuals" / visual["name"] / "visual.json", visual)
    write_json(
        report / "definition" / "pages" / "pages.json",
        {
            "$schema": schema_root + "pagesMetadata/1.0.0/schema.json",
            "pageOrder": page_ids,
            "activePageName": page_ids[0],
        },
    )
    print(f"{len(rows)} rows, {len(attention)} attention rows -> {OUT / (NAME + '.pbip')}")


if __name__ == "__main__":
    main()
