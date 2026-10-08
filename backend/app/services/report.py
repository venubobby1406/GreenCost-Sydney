"""Readable browser-print report using the same content as the downloadable PDF."""

from html import escape
from backend.app.services.explanation import money
from backend.app.services.client_report import report_content, LABELS


def report_html(result, years):
    v = report_content(result, years)
    p, r = v["project"], v["period"]

    def text(value):
        return escape(str(value))

    def para(value):
        return "<p>" + text(value) + "</p>"

    def table(headers, rows):
        return (
            "<table><thead><tr>"
            + "".join("<th>" + text(h) + "</th>" for h in headers)
            + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join("<td>" + text(x) + "</td>" for x in row) + "</tr>" for row in rows)
            + "</tbody></table>"
        )

    maximum = max(1, max(row["cumulative_pv"] for s in ("conventional", "sustainable") for row in r[s]["cashflows"]))
    minimum = min(0, min(row["cumulative_pv"] for s in ("conventional", "sustainable") for row in r[s]["cashflows"]))
    chart = '<svg viewBox="0 0 700 225" role="img" aria-label="Total costs over time in today equivalent dollars">'
    for scenario, colour in (("conventional", "#8b8276"), ("sustainable", "#194b3a")):
        points = " ".join(
            f"{30 + 640 * row['year'] / years:.1f},{190 - 155 * (row['cumulative_pv'] - minimum) / max(maximum - minimum, 1):.1f}"
            for row in r[scenario]["cashflows"]
        )
        chart += f'<polyline points="{points}" fill="none" stroke="{colour}" stroke-width="3"/>'
    chart += f'<text x="30" y="218">Year 0</text><text x="610" y="218">Year {years}</text></svg>'
    body = (
        '<section><span class="brand">GREENCOST</span><h1>Your building cost comparison</h1><h2>'
        + text("Project: " + (p["name"] or "Untitled project"))
        + "</h2>"
        + para(f"{years}-year decision report | AUD")
        + '<p class="notice">'
        + text(v["warning"])
        + '</p><p class="verdict">'
        + text(v["verdict"])
        + "</p>"
    )
    body += table(
        ["Cost to compare", "Conventional building", "Sustainable building"],
        [
            [
                "Initial building cost",
                money(r["conventional"]["components"]["capital"]),
                money(r["sustainable"]["components"]["capital"]),
            ],
            [
                f"Routine maintenance over {years} years",
                money(r["conventional"]["components"]["maintenance"]),
                money(r["sustainable"]["components"]["maintenance"]),
            ],
            [
                f"TOTAL cost over {years} years",
                money(r["conventional"]["total_lcc"]),
                money(r["sustainable"]["total_lcc"]),
            ],
        ],
    )
    body += (
        para(
            "Maintenance is already included in the total. Future costs are converted to today's equivalent using the selected discount rate; these figures are not a sum of future invoices."
        )
        + "<h2>What this means for your decision</h2>"
        + "".join(para(t) for t in v["findings"])
        + "</section>"
    )
    body += (
        "<section><h1>Why the costs differ</h1><h2>"
        + text("Your project explained")
        + "</h2>"
        + "".join(para(t) for t in v["project_explanation"])
        + "<h2>Where your money goes</h2>"
    )
    body += table(
        [f"Cost over {years} years", "Conventional", "Sustainable"],
        [
            [LABELS.get(k, k), money(value), money(r["sustainable"]["components"][k])]
            for k, value in r["conventional"]["components"].items()
        ],
    )
    body += para(
        "All future costs show today's equivalent value. Recovered-material value is a credit. Electricity includes supply charges and any modelled solar export credit."
    )
    if result.get("measures"):
        body += (
            "<h2>The upgrades you selected</h2>"
            + table(
                ["Upgrade", "Extra initial cost", "Price basis"],
                [[m["name"] + " - " + m["description"], money(m["premium"]), m["badge"]] for m in v["upgrades"]],
            )
            + para(
                "Installed differences include GST. Indicative prices need builder quotes; already-included features have no additional cost or benefit."
            )
        )
    body += (
        "<h2>How total costs build over time</h2>"
        + para("Green: sustainable. Grey: conventional. Values are converted to today's equivalent.")
        + chart
        + "</section>"
    )
    body += (
        "<section><h1>How reliable is the comparison?</h1><h2>Your key inputs</h2>"
        + table(["Input", "Value / explanation"], v["inputs"])
        + para("End-of-period plan: " + p.get("terminal_basis", "Review your assumptions."))
        + "<h2>Could the answer change?</h2>"
        + para(v["robustness"])
    )
    body += (
        table(
            ["Study period", "Conventional total", "Sustainable total"],
            [
                [f"{n} years", money(val["conventional"]["total_lcc"]), money(val["sustainable"]["total_lcc"])]
                for n, val in result["periods"].items()
            ],
        )
        + "<h2>Before committing to the design</h2><ol>"
        + "".join("<li>" + text(t) + "</li>" for t in v["next_steps"])
        + "</ol>"
    )
    if p["building_type"] == "Apartment Building":
        body += para(
            "Whole-building budgets must cover relevant lifts, car parks, central plant, fire systems and common services. The generic model does not automatically price these systems. Occupancy is an estimate, not a legal capacity."
        )
    if result.get("budget_scenarios"):
        body += "<h2>Your construction budget range</h2>" + table(
            ["Budget case", "Conventional total", "Sustainable total"],
            [
                [label.title(), money(val[str(years)]["conventional"]), money(val[str(years)]["sustainable"])]
                for label, val in result["budget_scenarios"].items()
            ],
        )
    body += "</section><section><h1>Evidence and report notes</h1><h2>Utility and cost references</h2>"
    for s in result.get("sources", []):
        body += (
            "<h3>"
            + text(s["organisation"] + " - " + s["title"])
            + "</h3>"
            + para(s["url"])
            + para(
                f"Reference: {s.get('effective_from')} to {s.get('effective_to') or 'not specified'}. Checked: {s.get('retrieved_at')}."
            )
        )
    body += "<h2>Supporting research</h2>"
    for i, e in enumerate(result.get("evidence", [])[:8], 1):
        body += para(f"[S{i}] {e['source']} - " + (f"page {e['page']}" if e.get("page") else "web context")) + (
            para(e["url"]) if e.get("url") else ""
        )
    body += (
        "<h2>What this report can and cannot tell you</h2>"
        + para(
            "This financial comparison does not certify BASIX, NatHERS, structural design or building compliance. Indicative quantities, demonstration values and research assumptions require applicable quotes, bills and plans. Environmental and comfort benefits are not fully measured by this financial model."
        )
        + para("For a complete input record, save your project JSON. Download the cash-flow CSV for each year's costs.")
        + "</section>"
    )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>GreenCost decision report</title><style>body{font:15px/1.65 Arial,sans-serif;color:#26382f;max-width:900px;margin:35px auto;padding:0 24px}h1{font-size:32px;color:#194b3a}h2{font-size:21px;color:#194b3a;margin-top:26px}.brand{font-weight:bold;letter-spacing:3px}.notice{background:#f5f2e8;padding:12px}.verdict{font-size:23px;font-weight:bold;color:#194b3a}table{width:100%;border-collapse:collapse;font-size:13px}td,th{padding:10px;border-bottom:1px solid #dce5df;text-align:left;overflow-wrap:anywhere}th{background:#edf4ef}svg{width:100%}p{overflow-wrap:anywhere}section{padding-bottom:24px}@media print{body{margin:0;font-size:11px}section{break-before:page}section:first-child{break-before:auto}tr,svg{break-inside:avoid}h1,h2,h3{break-after:avoid}thead{display:table-header-group}@page{size:A4;margin:16mm}}</style></head><body>'
        + body
        + "</body></html>"
    )
