"""Readable A4 decision report; detailed input records remain in JSON/CSV exports."""
import io
from html import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from backend.app.services.explanation import money
from backend.app.services.client_report import report_content, LABELS


def pdf_report(result, years):
    out = io.BytesIO()
    view = report_content(result, years)
    p, r = view["project"], view["period"]
    green, pale, ink = map(colors.HexColor, ("#194b3a", "#edf4ef", "#26382f"))
    styles = getSampleStyleSheet()
    styles["Normal"].fontName = "Helvetica"
    styles["Normal"].fontSize = 10
    styles["Normal"].leading = 15
    styles["Normal"].spaceAfter = 9
    styles["Normal"].textColor = ink
    for name in ("Heading1", "Heading2", "Heading3"):
        styles[name].textColor = green
        styles[name].keepWithNext = True
    styles.add(ParagraphStyle(name="SmallText", fontName="Helvetica", fontSize=8, leading=11, spaceAfter=5, textColor=ink, wordWrap="CJK"))
    styles.add(ParagraphStyle(name="Verdict", fontName="Helvetica-Bold", fontSize=17, leading=23, textColor=green, spaceAfter=12))
    story = []
    def plain(value):
        return str(value).translate(str.maketrans({"–":"-","—":"-","→":"to","²":"2","³":"3","×":"x","Σ":"Sum","−":"-","’":"'","“":'"',"”":'"'})).encode("latin-1", "replace").decode("latin-1")
    def para(text, style="Normal"):
        return Paragraph(escape(plain(text)), styles[style])
    def add(text, style="Normal"):
        story.append(para(text,style))
    def heading(text):
        add(text,"Heading2")
    def table(headers, rows, widths, highlight_last=False):
        data=[[para(x,"SmallText") for x in headers]]+[[para(x,"SmallText") for x in row] for row in rows]
        t=Table(data,colWidths=widths,repeatRows=1,hAlign="LEFT")
        commands=[("BACKGROUND",(0,0),(-1,0),pale),("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),("LINEBELOW",(0,0),(-1,-1),.4,colors.HexColor("#dce5df"))]
        if highlight_last: commands.append(("BACKGROUND",(0,-1),(-1,-1),pale))
        t.setStyle(TableStyle(commands));story.extend([t,Spacer(1,10)])
    def page(title,subtitle):
        if story: story.append(PageBreak())
        add(title,"Heading1");add(subtitle,"SmallText");story.append(Spacer(1,8))

    page("Your building cost comparison",f"GREENCOST | {years}-year decision report | All amounts in Australian dollars")
    add("Project: " + (p["name"] or "Untitled project"),"Heading2")
    add(view["warning"],"SmallText")
    add(view["verdict"],"Verdict")
    table(["Cost to compare","Conventional building","Sustainable building"],[
        ["Initial building cost",money(r["conventional"]["components"]["capital"]),money(r["sustainable"]["components"]["capital"])],
        [f"Routine maintenance over {years} years",money(r["conventional"]["components"]["maintenance"]),money(r["sustainable"]["components"]["maintenance"])],
        [f"TOTAL cost over {years} years",money(r["conventional"]["total_lcc"]),money(r["sustainable"]["total_lcc"])],
    ],[195,155,155],True)
    add("The maintenance row is already included in the total. Future bills, repairs, equipment replacements and end-of-period costs are converted to today's equivalent value using your discount rate. These totals are not a sum of future invoices.","SmallText")
    heading("What this means for your decision")
    for text in view["findings"]: add(text)
    add(f"Scope: {p['building_type']} | Postcode {p['postcode']} | {p['area']*(.092903 if p['area_unit']=='ft²' else 1):,.1f} m2 total floor area | {p['floors']} floor(s).","SmallText")
    add("Annual water: " + f"{p['water_kl']*1000:,.0f} L ({p['water_kl']/1000:g} million litres).","SmallText")

    page("Why the costs differ","Explain the result before reviewing the assumptions.")
    heading("Your project explained")
    for text in view["project_explanation"]: add(text)
    if result.get("measures"):
        heading("The upgrades you selected")
        table(["Upgrade","Extra initial cost","Price basis"],[[m["name"] + " - " + m["description"],money(m["premium"]),m["badge"]] for m in view["upgrades"]],[240,125,140])
        add("These are installed cost differences against the baseline, including GST. 'Indicative' means an estimate, not a builder's quotation. An already included feature has no additional cost or benefit.","SmallText")
    else:
        add("No individually priced upgrades were selected." if p.get("mode")=="itemised" else "This comparison uses a combined research package rather than individually priced upgrades.")

    page("Costs and decision checks","Future costs shown as today's equivalent value.")
    heading("Where your money goes")
    table([f"Cost over {years} years","Conventional","Sustainable"],[[LABELS.get(k,k),money(v),money(r["sustainable"]["components"][k])] for k,v in r["conventional"]["components"].items()],[195,155,155])
    add("All future-cost rows show today's equivalent value. Recovered-material value is a credit; a negative figure reduces total cost. Electricity includes supply charges and any modelled solar export credit.","SmallText")
    heading("Could the answer change?")
    add(view["robustness"])
    table(["Study period","Conventional total","Sustainable total"],[[f"{n} years",money(v["conventional"]["total_lcc"]),money(v["sustainable"]["total_lcc"])] for n,v in result["periods"].items()],[195,155,155])
    if result.get("budget_scenarios"):
        heading("Your construction budget range")
        table(["Budget case", "Conventional total", "Sustainable total"], [[label.title(), money(v[str(years)]["conventional"]), money(v[str(years)]["sustainable"])] for label,v in result["budget_scenarios"].items()], [195,155,155])
    page("Your assumptions and next steps","Check the inputs that could change the decision.")
    heading("Your key inputs")
    table(["Input","Value / explanation"],view["inputs"],[190,315])
    add("End-of-period plan: " + p.get("terminal_basis","Review your end-of-period assumptions."),"SmallText")
    if result.get("budget_scenarios"):
        add("A budget range was entered. Headline figures use the midpoint; low and high budgets are alternative starting-cost scenarios.","SmallText")
    heading("Before committing to the design")
    for i,text in enumerate(view["next_steps"],1): add(f"{i}. {text}","SmallText")
    if p["building_type"]=="Apartment Building":
        add("Whole apartment building: include all relevant apartments, lifts, car parks, central plant, fire systems and common services in costs. The generic model does not automatically price these systems. Occupancy is a planning estimate, not a permitted capacity.","SmallText")

    page("Evidence and report notes","Sources support the assumptions; they are not a guarantee of your project's performance.")
    heading("Utility and cost references")
    for source in result.get("sources",[]):
        story.append(KeepTogether([para(source["organisation"] + " - " + source["title"],"Heading3"),para(source["url"],"SmallText"),para(f"Reference period: {source.get('effective_from','not recorded')} to {source.get('effective_to') or 'not specified'}. Checked: {source.get('retrieved_at','not recorded')}.","SmallText")]))
    heading("Supporting research")
    evidence=result.get("evidence",[])[:8]
    for i,e in enumerate(evidence,1):
        location=f"page {e['page']}" if e.get("page") else "web reference"
        kind="Included project research" if e.get("source_type")=="PROJECT_RESEARCH" else "Research / web context"
        add(f"[S{i}] {e['source']} - {location}. {kind}.","SmallText")
        if e.get("url"): add(e["url"],"SmallText")
    if not evidence: add("No research references were retained for this comparison.","SmallText")
    heading("What this report can and cannot tell you")
    add("This is a financial comparison of the entered scenarios. It does not certify BASIX, NatHERS, structural design or building compliance. Sustainability features may offer comfort or environmental benefits that this cost calculation does not measure.","SmallText")
    add("Research assumptions and generic building quantities need project confirmation. Demonstration values and indicative prices must be replaced with applicable bills, plans and installed quotes. Higher cost for the sustainable option is a valid result.","SmallText")
    add("For a complete input record, save your project JSON. For each year's costs, download the cash-flow CSV. Those files retain the technical detail without filling this client report with raw data.","SmallText")
    add(f"Price reference: {result.get('price_snapshot_date') or p['price_date']} | Assumption set: {result.get('assumption_version','not recorded')}.","SmallText")
    def footer(canvas,doc):
        canvas.setStrokeColor(colors.HexColor("#dce5df"));canvas.line(45,39,A4[0]-45,39)
        canvas.setFont("Helvetica",8);canvas.setFillColor(green)
        canvas.drawString(45,25,"GreenCost | Planning estimate | AUD")
        canvas.drawRightString(A4[0]-45,25,f"Page {doc.page}")
    SimpleDocTemplate(out,pagesize=A4,rightMargin=45,leftMargin=45,topMargin=40,bottomMargin=52,title=plain((p["name"] or "Untitled project") + " - GreenCost decision report"),author="GreenCost").build(story,onFirstPage=footer,onLaterPages=footer)
    return out.getvalue()
