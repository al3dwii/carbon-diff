from fastapi import FastAPI, Query, Response

app = FastAPI()

SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="110" height="20">
<rect width="110" height="20" fill="#555"/>
<rect x="60" width="50" height="20" fill="{color}"/>
<text x="30" y="14" fill="#fff" font-family="Verdana" font-size="11">Δ kWh</text>
<text x="65" y="14" fill="#fff" font-family="Verdana" font-size="11">{label}</text>
</svg>
"""

@app.get("/badge")
def badge(kwh: float = Query(..., description="kWh delta")):
    color = "#4c1" if kwh <= 0 else "#e05d44"  # green / red
    label = f"{kwh:+.2f}"
    return Response(SVG.format(color=color, label=label),
                    media_type="image/svg+xml",
                    headers={"Cache-Control": "max-age=86400"})
