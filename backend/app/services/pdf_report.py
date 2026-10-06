"""Portable A4 report built from computed results, with repeatable tables."""
import io
import json
from html import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.graphics.shapes import Drawing, PolyLine, String, Line
from backend.app.services.explanation import money


def pdf_report(result, years):
    out = io.BytesIO()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SmallText", fontName="Helvetica", fontSize=8, leading=11, spaceAfter=5, wordWrap="CJK"))
    styles["Normal"].fontSize = 10
    styles["Normal"].leading = 15
    styles["Heading2"].keepWithNext = True
    styles["Heading3"].keepWithNext = True
    story = []
    r = result["periods"][str(years)]

    def plain(text):
        return str(text).replace("–", "-").replace("—", "-").replace("→", "to").replace("²", "2").replace("Σ", "Sum").replace("−", "-").replace("’", "'").replace("“", '"').replace("”", '"').encode("latin-1", "replace").decode("latin-1")

    def paragraph(text, style="Normal"):
        return Paragraph(escape(plain(text)), styles[style])

    def heading(text):
        story.append(paragraph(text, "Heading2"))

    def table(headers, rows, widths):
        values = [[paragraph(x, "SmallText") for x in headers]] + [[paragraph(x, "SmallText") for x in row] for row in rows]
        t = Table(values, colWidths=widths, repeatRows=1, hAlign="LEFT")
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8efdf")),
                               ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                               ("TOPPADDING", (0, 0), (-1, -1), 7),
                               ("LINEBELOW", (0, 0), (-1, -1), .4, colors.HexColor("#d9e1d4"))]))
        story.append(t)

    story.extend([paragraph("GREENCOST SYDNEY", "Title"), paragraph(result["project"]["name"], "Heading1"),
                  paragraph(f"{years}-year life-cycle cost comparison | AUD, present value"),
                  paragraph(f"Mode: {result['project'].get('mode', 'literature')} | Preset: {result['project'].get('preset', 'code_minimum_7star')}"),
                  paragraph(f"Assumption set {result.get('assumption_version')} | Price reference {result.get('price_snapshot_date')}"),
                  Spacer(1, 15)])
    table(["Result", "Value"], [["Conventional LCC", money(r["conventional"]["total_lcc"])],
                                 ["Sustainable LCC", money(r["sustainable"]["total_lcc"])],
                                 ["Signed saving", money(r["savings_aud"])],
                                 ["Saving relative to conventional", f"{r['savings_percent']:.2f}%"],
                                 ["First discounted break-even", "Not reached" if r["break_even_year"] is None else f"Year {r['break_even_year']}"],
                                 ["Equivalent annual sustainable cost", money(r["sustainable"]["eauc"])]], [300, 205])
    story.append(paragraph(f"Under the stated assumptions, the sustainable case has a {abs(r['savings_percent']):.2f}% {'lower' if r['savings_aud'] >= 0 else 'higher'} modelled whole-life cost. Indicative inputs are not verified quotations."))
    if result.get("budget_scenarios"):
        heading("Construction budget range")
        story.append(paragraph("Headline results use the midpoint. Each case recalculates the same upgrade package and financial assumptions."))
        table(["Budget case", "Conventional LCC", "Sustainable LCC", "Signed saving"],
              [[label, money(v[str(years)]["conventional"]), money(v[str(years)]["sustainable"]), money(v[str(years)]["savings_aud"])] for label, v in result["budget_scenarios"].items()], [110, 135, 135, 125])
    if result["project"].get("cost_plan_note"):
        story.append(paragraph("Cost breakdown basis: " + result["project"]["cost_plan_note"], "SmallText"))
    heading("Cumulative discounted cost")
    drawing = Drawing(505, 185)
    maximum = max(max(row["cumulative_pv"] for row in r[s]["cashflows"]) for s in ("conventional", "sustainable"))
    minimum = min(0, min(min(row["cumulative_pv"] for row in r[s]["cashflows"]) for s in ("conventional", "sustainable")))
    drawing.add(Line(5, 20, 495, 20, strokeColor=colors.grey))
    for scenario, colour in (("conventional", "#9b8c77"), ("sustainable", "#31533f")):
        points = [v for row in r[scenario]["cashflows"] for v in (5 + 490 * row["year"] / years, 25 + 125 * (row["cumulative_pv"] - minimum) / max(maximum - minimum, 1))]
        drawing.add(PolyLine(points, strokeColor=colors.HexColor(colour), strokeWidth=2))
    drawing.add(String(5, 6, "Year 0", fontSize=8))
    drawing.add(String(455, 6, f"Year {years}", fontSize=8))
    drawing.add(String(5, 170, "Green: sustainable | Taupe: conventional | cumulative present value", fontSize=8))
    story.append(drawing)
    heading("Cost categories and contributions")
    table(["Category", "Conventional", "Sustainable", "Signed saving"],
          [[k, money(v), money(r["sustainable"]["components"][k]), money(r["component_savings"][k])] for k, v in r["conventional"]["components"].items()], [130, 125, 125, 125])
    heading("Interpretation")
    story.extend(paragraph(p) for p in r["explanation"])
    if result.get("measures"):
        heading("Selected upgrades (installed differences, including GST)")
        table(["Upgrade", "Quantity / basis", "Net premium", "Source / status"],
              [[m["name"], f"{m['quantity']:.2f} {m['quantity_driver'].replace('_', ' ')}", money(m["premium"]), f"{m['badge']} - {m['source']} ({m['price_date']})"] for m in result["measures"]], [140, 120, 90, 155])
        heading("Marginal upgrade contributions")
        story.append(paragraph("Upgrades are added in catalogue order. Interactions are the difference from modelling each upgrade alone; contributions reconcile to total signed savings."))
        table(["Upgrade", "Marginal saving", "Standalone saving", "Interaction"],
              [[m["name"], money(m["marginal_savings"]), money(m["standalone_savings"]), money(m["interaction_adjustment"])]
               for m in result["measure_contributions"][str(years)]], [160, 115, 115, 115])
        heading("Price uncertainty (indicative ranges)")
        table(["Price scenario", "Signed saving", "Break-even"],
              [[label, money(v[str(years)]["savings_aud"]), v[str(years)]["break_even_year"] or "Not reached"]
               for label, v in result["price_sensitivity"].items()], [165, 170, 170])
    heading("Sensitivity: signed savings")
    cells = [c for c in result["sensitivity"] if c["years"] == years]
    table(["Discount / energy growth", "2%", "3%", "4%", "5%"],
          [[f"{d}%"] + [money(next(c["savings_aud"] for c in cells if round(c["discount"] * 100) == d and round(c["energy_escalation"] * 100) == e)) for e in (2, 3, 4, 5)] for d in (4, 5, 6, 7)], [165, 85, 85, 85, 85])
    if result.get("literature_scenarios"):
        heading("Literature-parameter scenarios")
        table(["Scenario", "Signed saving", "Saving %", "Break-even"],
              [[label, money(v[str(years)]["savings_aud"]), f"{v[str(years)]['savings_percent']:.2f}%", v[str(years)]["break_even_year"] or "Not reached"] for label, v in result["literature_scenarios"].items()], [125, 145, 100, 135])
    story.append(PageBreak())
    heading("Assumptions and provenance")
    def display(value):
        return f"{value:,.4f}".rstrip('0').rstrip('.') if isinstance(value, float) else str(value)
    table(["Assumption", "Value / unit", "Source"], [[a["name"].replace('_', ' '), f"{display(a['value'])} {a['unit']}", a["source"]] for a in result["assumptions"]], [155, 130, 220])
    heading("Sources")
    for s in result["sources"]:
        story.extend([paragraph(s["organisation"] + " - " + s["title"], "Heading3"), paragraph(s["url"], "SmallText"),
                      paragraph(f"Effective {s['effective_from']} to {s['effective_to'] or 'reference period'}. Accessed {s['retrieved_at']}. {s['notes']}", "SmallText")])
    heading("Research evidence")
    for i, evidence in enumerate(result["evidence"]):
        story.extend([paragraph(f"[S{i + 1}] {evidence['source']} | page {evidence['page']} | {evidence['source_type']}", "Heading3"),
                      paragraph(evidence.get("text", ""), "SmallText")])
    heading("Limitations")
    story.extend(paragraph(x) for x in result["limitations"])
    heading("Complete input record")
    records = []
    for key, value in result["project"].items():
        if isinstance(value, list) and value:
            records.extend([f"{key.replace('_', ' ')} #{i + 1}", json.dumps(item, ensure_ascii=False)] for i, item in enumerate(value))
        elif isinstance(value, dict) and value:
            records.extend([f"{key.replace('_', ' ')} / {name}", json.dumps(item, ensure_ascii=False)] for name, item in value.items())
        else:
            records.append([key.replace('_', ' '), json.dumps(value, ensure_ascii=False)])
    table(["Input", "Recorded value"],
          records,
          [155, 350])

    def footer(canvas, doc):
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#53634c"))
        canvas.drawString(45, 25, "GreenCost Sydney | Indicative scenario, not a compliance assessment")
        canvas.drawRightString(A4[0] - 45, 25, f"Page {doc.page}")
    SimpleDocTemplate(out, pagesize=A4, rightMargin=45, leftMargin=45, topMargin=40, bottomMargin=45,
                      title="GreenCost Sydney life-cycle report", author="GreenCost Sydney").build(story, onFirstPage=footer, onLaterPages=footer)
    return out.getvalue()
