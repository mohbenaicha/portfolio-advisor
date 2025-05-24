import httpx, markdown, webbrowser, tempfile

BASE_URL = "http://localhost:8000"
USER_TOKEN = (
    "df77c9be-67fb-44b9-a15c-8146131e2d14"  # Replace with actual token for user 1
)
USER_ID = "1"

HEADERS = {
    "Authorization": f"Bearer {USER_TOKEN}",
    "x-user-id": USER_ID,
    "Content-Type": "application/json",
}


async def test_analyze_endpoint():
    async with httpx.AsyncClient(timeout=None) as client:
        # Step 1: Authenticate
        auth_payload = {"token": USER_TOKEN}
        auth_resp = await client.post(f"{BASE_URL}/auth", json=auth_payload)
        assert auth_resp.status_code == 200
        user_id = auth_resp.json().get("user_id")
        assert user_id is not None

        # Step 2: Call analyze with x-user-id header
        analyze_payload = {
            "question": "I want to fully shift my portfolio to renewable energy. Can you recommend some well performing assets?",
            "portfolio_id": 9,
        }
        headers = {"x-user-id": str(user_id)}
        analyze_resp = await client.post(
            f"{BASE_URL}/analyze", json=analyze_payload, headers=headers
        )
        assert analyze_resp.status_code == 200
        analyze_data = analyze_resp.json()
        assert "summary" in analyze_data
        assert isinstance(analyze_data["summary"], str) and analyze_data["summary"]

        with open("./tests/analyze_summary.txt", "w", encoding="utf-8") as file:
            file.write(analyze_data["summary"])
        print("Analyze response saved to analyze_summary.txt")
        html_output = convert_markdown_to_html(analyze_data["summary"])
        render_html_directly(html_output)


def convert_markdown_to_html(markdown_text):
    html_content = markdown.markdown(markdown_text, extensions=["extra", "smarty"])
    styled_html = f"""
    <html>
    <head>
        <style>
            body {{
                background-color: black;
                color: yellow;
                font-family: 'Inter', sans-serif;
                margin: 20px;
            }}
            h1, h2, h3, h4, h5, h6 {{
                font-family: 'Oswald', sans-serif;
                color: orange;
                font-size: 24px;
                margin-bottom: 10px;

            }}
            p, li {{
                font-family: 'Inter', sans-serif;
                color: yellow;
                font-size: 12px;
                line-height: 1.5;
                margin-bottom: 10px;
            }}
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Oswald:wght@400;700&display=swap" rel="stylesheet">
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    return styled_html


def render_html_directly(html_content):
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".html", mode="w", encoding="utf-8"
    ) as temp_file:
        temp_file.write(html_content)
        webbrowser.open(f"file://{temp_file.name}")


if __name__ == "__main__":

    html_out = convert_markdown_to_html(
        """
**1‑Sentence Answer**  
Shift your portfolio from general tech stocks to a diversified mix of leading renewable energy utilities like SSE plc and clean energy ETFs for strong growth and long-term sustainable infrastructure exposure.

**Portfolio Impact Analysis**  
Your current portfolio is 100% US technology stocks (Nvidia, Tesla, Microsoft), lacking renewable energy exposure. The strong FY25 results and ambitious capital investments from SSE plc—a major UK renewable utility—highlight attractive opportunities in clean energy infrastructure. Exposure to a broad renewable energy ETF could complement SSE’s direct utility play and accelerate your transition.

**Recommendations (Numbered)**  
1. **Sell 100% of NVDA and MSFT positions** and reduce TSLA holdings by 50% within 1 month. This liquidation frees capital for renewable energy investments and de-risks sector concentration in tech.  
2. **Buy SSE plc (ticker: SSE)** to target 30% portfolio weight over 3 months. SSE’s strong earnings, increased renewables output (+18%), and £17.5bn investment plan underpin reliable income and growth in clean energy infrastructure.  
3. **Acquire a renewable energy ETF** (e.g., iShares Global Clean Energy ETF [ICLN]) for 40% portfolio exposure over 2 months. This ETF provides diversified, liquid access to global renewable companies, reducing single-name risk.  
4. **Allocate remaining 30% into solar/wind pure-play stocks or green bonds** for further diversification aligned with sustainable infrastructure growth. Consider names like NextEra Energy or Vestas Wind Systems.  
5. Review and rebalance quarterly to hedge against regulatory shifts or commodity price risks, maintaining portfolio alignment with evolving clean energy trends.  

**Key Risks & Unknowns**  
- Regulatory and subsidy changes impacting renewable energy profitability  
- Project execution delays or cost overruns for infrastructure utilities like SSE  
- Market volatility in new/regulatory-driven asset classes like clean energy ETFs  
- Currency risk from non-US investments (SSE is UK-based)  
- Possible valuation correction due to rising interest rates or inflation pressures  

**Confidence (0‑100%)**  
82% — SSE’s clear strategic investment and stable earnings plus diversified ETF exposure provide a strong base, though renewable energy markets still carry policy and execution uncertainties.

**References & Assumptions**  
- SSE FY25 adjusted EPS 160.9p, 18% renewables output growth, £17.5bn investment plan  
- User’s current 100% US tech exposure implies need for geographic and sector diversification  
- Clean energy ETFs like ICLN offer diversified renewable exposure  
- Industry trends favor utilities investing in sustainable infrastructure  

**Citations**  
- “SSE Reports Strong Performance and Strategic Investment in Clean Energy Transition,” tipranks.com  
- “ETF Talk: Investing in Iberian Ambitions with the iShares MSCI Spain ETF (EWP),” stockinvestor.com (for ETF diversification context)
"""
    )
    print(html_out)
    render_html_directly(html_out)
