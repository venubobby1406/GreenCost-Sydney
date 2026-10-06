from html import escape
import json
from backend.app.services.explanation import money


def report_html(result, years):
    r = result["periods"][str(years)]

    def table(headers, rows):
        return (
            "<table><thead><tr>"
            + "".join("<th>" + escape(str(h)) + "</th>" for h in headers)
            + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join("<td>" + escape(str(v)) + "</td>" for v in row) + "</tr>" for row in rows)
            + "</tbody></table>"
        )

    max_y = max(x["cumulative_pv"] for s in ("conventional", "sustainable") for x in r[s]["cashflows"])
    min_y = min(0, min(x["cumulative_pv"] for s in ("conventional", "sustainable") for x in r[s]["cashflows"]))

    def line(s, color):
        points = " ".join(
            f"{30 + 640 * x['year'] / years:.2f},{220 - 180 * (x['cumulative_pv'] - min_y) / max(max_y - min_y, 1):.2f}"
            for x in r[s]["cashflows"]
        )
        return f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>'

    chart = f'<svg viewBox="0 0 700 260" role="img" aria-label="Cumulative discounted costs"><path d="M30 20V220H670" fill="none" stroke="#aaa"/>{line("conventional", "#827664")}{line("sustainable", "#38604b")}<text x="30" y="245">Year 0</text><text x="610" y="245">Year {years}</text><text x="35" y="18">Cumulative PV (AUD), top scale {money(max_y)}</text></svg>'
    colors = ["#38604b", "#827664", "#99ab8e", "#b3a686", "#87a3a0", "#cbbb9f", "#819079"]
    positive_keys = [k for k in r["conventional"]["components"] if k != "residual"]
    component_max = max(sum(r[s]["components"][k] for k in positive_keys) for s in ("conventional", "sustainable"))
    bars = []
    for n, scenario in enumerate(("conventional", "sustainable")):
        x, y = 120.0, 35 + n * 75
        bars.append(f'<text x="8" y="{y + 24}">{scenario.capitalize()}</text>')
        for i, key in enumerate(positive_keys):
            value = r[scenario]["components"][key]
            width = max(0.0, value) / max(component_max, 1) * 550
            bars.append(
                f'<rect x="{x:.2f}" y="{y}" width="{width:.2f}" height="36" fill="{colors[i]}" ><title>{key}: {money(value)}</title></rect>'
            )
            x += width
    legend = "".join(
        f'<rect x="{10 + i * 98}" y="190" width="9" height="9" fill="{colors[i]}"/><text x="{23 + i * 98}" y="199" font-size="10">{key}</text>'
        for i, key in enumerate(positive_keys)
    )
    component_chart = (
        '<svg viewBox="0 0 700 225" role="img" aria-label="Present value cost components">'
        + "".join(bars)
        + legend
        + "</svg>"
    )
    budget_section = ""
    if result.get("budget_scenarios"):
        budget_section = "<h2>Construction budget range</h2><p>Headline results use the midpoint.</p>" + table(["Case", "Conventional LCC", "Sustainable LCC", "Signed saving"], [[label, money(v[str(years)]["conventional"]), money(v[str(years)]["sustainable"]), money(v[str(years)]["savings_aud"])] for label, v in result["budget_scenarios"].items()])
    sections = [
        budget_section,
        "<p>" + escape(result["project"].get("cost_plan_note", "")) + "</p>",
        f'<h1>GreenCost Sydney</h1><p class="eyebrow">LIFE-CYCLE COST STUDY · {years} YEARS</p><h2>{escape(result["project"]["name"])}</h2>',
        f"<p>{escape(result['confidence'])} — {escape(result['confidence_reason'])}</p>",
        table(
            ["Measure", "Value"],
            [
                ["Conventional LCC", money(r["conventional"]["total_lcc"])],
                ["Sustainable LCC", money(r["sustainable"]["total_lcc"])],
                ["Sustainable equivalent annual cost", money(r["sustainable"]["eauc"])],
                ["Signed savings", money(r["savings_aud"])],
                [
                    "Savings percentage",
                    f"{r['savings_percent']:.2f}%" if r["savings_percent"] is not None else "Not defined",
                ],
                [
                    "First break-even year",
                    r["break_even_year"] if r["break_even_year"] is not None else "None within period",
                ],
            ],
        ),
        "<h2>Cumulative discounted cost</h2><p>Green: sustainable · Taupe: conventional</p>" + chart,
        "<h2>Cost components (present value)</h2>"
        + component_chart
        + "<p>Residual value is a credit and is shown separately in the table.</p>"
        + table(
            ["Component", "Conventional", "Sustainable"],
            [
                [k, money(v), money(r["sustainable"]["components"][k])]
                for k, v in r["conventional"]["components"].items()
            ],
        ),
        "<h2>Interpretation</h2>" + "".join("<p>" + escape(p) + "</p>" for p in r["explanation"]),
        "<h2>Assumptions and provenance</h2>"
        + table(
            ["Assumption", "Value", "Unit", "Source"],
            [[a[k] for k in ("name", "value", "unit", "source")] for a in result["assumptions"]],
        ),
        "<h2>Sensitivity (signed AUD savings)</h2>"
        + table(
            ["Years", "Discount", "Energy escalation", "Savings", "Break-even"],
            [
                [
                    s["years"],
                    f"{s['discount']:.0%}",
                    f"{s['energy_escalation']:.0%}",
                    money(s["savings_aud"]),
                    s["break_even_year"] if s["break_even_year"] is not None else "None",
                ]
                for s in result["sensitivity"]
            ],
        ),
        "<h2>Evidence and sources</h2>"
        + "".join(
            f'<p><strong>{escape(s["organisation"])}</strong> — {escape(s["title"])}<br><a href="{escape(s["url"], quote=True)}">{escape(s["url"])}</a><br>Effective {s["effective_from"]} to {s["effective_to"] or "reference period"}; retrieved {s["retrieved_at"]}. {escape(s["notes"])}</p>'
            for s in result["sources"]
        ),
        "<h2>PDF and web research</h2>"
        + "".join(
            f"<p>[S{i+1}] {escape(e['source'])} — {'page ' + str(e['page']) if e['page'] else 'web context'}, {escape(e['source_type'])}</p>"
            + (f'<p><a href="{escape(e["url"], quote=True)}">Source page</a></p>' if e.get("url") else "")
            + "<p>" + escape(e.get("text", "")) + "</p>" for i, e in enumerate(result["evidence"])
        ),
        "<h2>Limitations</h2><ul>" + "".join("<li>" + escape(x) + "</li>" for x in result["limitations"]) + "</ul>",
        "<h2>Complete input record</h2><pre>"
        + escape(json.dumps(result["project"], indent=2, ensure_ascii=False))
        + "</pre>",
        f"<p>Analysis {escape(result['id'])} · {escape(result['created_at'])}. Generated from saved deterministic results. Browser Print → Save as PDF.</p>",
    ]
    sections.insert(1, f"<p>Mode: {escape(result['project'].get('mode', 'literature'))} · Assumption version {escape(str(result.get('assumption_version')))} · Price reference {escape(str(result.get('price_snapshot_date')))}</p>")
    details = ""
    if result.get("measures"):
        details += "<h2>Selected upgrades: installed differences including GST</h2>" + table(
            ["Upgrade", "Quantity / basis", "Premium", "Source / status"],
            [[m["name"], f"{m['quantity']:.2f} {m['quantity_driver'].replace('_', ' ')}", money(m["premium"]),
              f"{m['badge']}: {m['source']} ({m['price_date']})"] for m in result["measures"]])
        details += "<h2>Marginal upgrade contributions</h2><p>Measures are added in catalogue order; interactions reconcile standalone and combined savings.</p>" + table(
            ["Upgrade", "Marginal savings", "Standalone savings", "Interaction"],
            [[m["name"], money(m["marginal_savings"]), money(m["standalone_savings"]), money(m["interaction_adjustment"])]
             for m in result["measure_contributions"][str(years)]])
        details += "<h2>Indicative price uncertainty</h2>" + table(["Prices", "Signed savings", "Break-even"],
            [[level, money(value[str(years)]["savings_aud"]), value[str(years)]["break_even_year"] or "Not reached"]
             for level, value in result["price_sensitivity"].items()])
    elif result.get("literature_scenarios"):
        details += "<h2>Literature-parameter scenarios</h2>" + table(["Scenario", "Signed savings", "Break-even"],
            [[level, money(value[str(years)]["savings_aud"]), value[str(years)]["break_even_year"] or "Not reached"]
             for level, value in result["literature_scenarios"].items()])
    sections.insert(7, details)
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8"><title>GreenCost Sydney report</title><style>body{font:14px/1.6 Arial,sans-serif;color:#253b30;max-width:960px;margin:40px auto;padding:0 24px}h1{font-size:40px}h2{margin-top:32px}.eyebrow{letter-spacing:3px}table{width:100%;border-collapse:collapse;font-size:12px}td,th{border-bottom:1px solid #ddd;padding:8px;text-align:left;overflow-wrap:anywhere}th{background:#e9eee9}svg{width:100%}pre{white-space:pre-wrap;font-size:11px}a{color:#38604b;overflow-wrap:anywhere}@media print{body{margin:0}tr,svg{break-inside:avoid}h2{break-after:avoid}thead{display:table-header-group}@page{size:A4;margin:16mm}}</style><body>'
        + "".join(sections)
        + "</body></html>"
    )
