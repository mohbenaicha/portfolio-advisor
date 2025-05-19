import markdown
import webbrowser
import os

# Raw Markdown string
raw_response_ = """
# **1‑Sentence Answer**
Recent geopolitical shifts and technological initiatives in Europe create both growth opportunities and risks, particularly impacting Siemens AG and Vodafone Group in your portfolio.

# **Portfolio Impact Analysis**
Siemens AG operates in the manufacturing sector, which could benefit from Europe’s emphasis on technological sovereignty and military investments, enhancing local manufacturing capabilities. Conversely, Vodafone Group faces potential headwinds due to the EU's regulatory push for tech autonomy, which may stress margins as companies adapt. Additionally, the strong focus on European tech innovation highlights opportunities in high-growth sectors.

# **Recommendations (Numbered)**
1. **Reduce Exposure to Vodafone (Target Weight: 5% of portfolio)**: Sell 100 shares to decrease exposure in a potentially declining regulatory environment within the tech sector. Time frame: 1-3 months. Thesis: Demand uncertainty and regulatory risks may diminish returns.
   
2. **Increase Exposure to Siemens (Target Weight: 10% of portfolio)**: Purchase 40 shares to capitalize on expected growth from Europe's manufacturing focus and military investments. Time frame: 3-12 months. Thesis: Siemens is likely to benefit from increased public spending in its sector.
   
3. **Consider Diversifying into Agri-Tech (Target 5% allocation)**: Identify and invest in agri-tech companies within Europe due to projected market growth (CAGR of 13.81%). Time frame: 1 year. Thesis: Demand for resource-efficient technologies is likely to rise, creating robust investment opportunities.

# **Key Risks & Unknowns**
- Geopolitical developments may impact market stability.
- Potential regulatory changes could adversely affect tech margins.
- Economic slowdowns in Europe could undermine growth projections.
- Possible over-reliance on consumer trends in technology may lead to volatility.

# **Confidence (0‑100%)**
75% - Relying on current trends in geopolitical strategies and European technological investments, yet market shifts can rapidly change outcomes.

# **References & Assumptions**
- News insights on technological sovereignty and growth of the European tech sector.
- Siemens AG's position within the military investment landscape as described in the news.
- Vodafone Group's risk exposure related to EU digital regulations and sovereignty initiatives.

# **Compliance Note**
This information is for educational purposes only and does not constitute financial advice.
"""

raw_response__ = "# 1‑Sentence Answer\nEmerging market assets are poised for volatility due to geopolitical tensions and fluctuating commodity prices, impacting your portfolio's performance.\n\n# Portfolio Impact Analysis\n- **EEM (MSCI EM Index ETF)**: Positive sentiment from U.S.-China tariff reductions could temporarily lift investor confidence; however, increased geopolitical risks may introduce volatility.\n- **PBR (Petrobras)**: Expected decline in global oil demand and production forecasts could pressure Petrobras, particularly amid a weak energy sector linked to OPEC production strategies.\n- **PBR-PUT**: As a hedge, the put option provides effective risk management against potential downturns in Petrobras.\n\n# Recommendations (Numbered)\n1. **Reduce EEM Exposure**: Consider decreasing EEM allocation from 500 units to 350 units. Target weight: 70% of current position. Time frame: 1 month. Thesis: Mitigate potential downturn amid geopolitical uncertainty.\n2. **Increase PBR-PUT Holdings**: Expand put option contracts from 100 to 150. Target weight: 50% increase. Time frame: 2 months. Thesis: Enhance downside protection against energy sector volatility.\n3. **Monitor Energy Sector Developments**: Allocate resources for tactical shifts based on OPEC and economic data releases within 3 months. Thesis: Adjust positions proactively in response to evolving market conditions.\n\n# Key Risks & Unknowns\n- Sustained geopolitical tensions affecting emerging markets.\n- Uncertainty in global energy demand and OPEC’s production decisions.\n- Regulatory changes impacting emerging market equities.\n- Market reactions to upcoming U.S. economic indicators and central bank policies.\n\n# Confidence (0‑100%)\n75% - Strong rationale based on current geopolitical developments and commodity forecasts supports the recommendations, but potential unpredictability exists.\n\n# References & Assumptions\n- Market sentiment uplift from the US-China tariff pause (U.S. index futures surge).\n- Projected decline in U.S. crude production and its implications on energy stocks (S&P Global forecast).\n- Petrobras facing pressure from declining oil demand outlook and OPEC strategies.\n\n# Compliance Note\nThis information is for educational purposes and should not be construed as personal financial advice."

raw_response = """
# 1‑Sentence Answer
Recent downgrades to the U.S. credit rating and geopolitical developments are increasing volatility, favoring a defensive stance in government bonds and impacting gold as a safe haven.

# Portfolio Impact Analysis
1. **20Y Treasury ETF (TLT)**: The Moody's downgrade of the U.S. credit rating may increase risk perception, potentially leading to a sell-off in long-term treasuries despite their safety during economic uncertainty.
2. **Gold ETF (GLD)**: The drop in gold prices amid positive U.S.-China trade talks (indicating reduced risk premium) may weaken gold's role as a hedge, affecting your position negatively.
3. **TLT-SWAP**: Your hedge via the TLT swap may become more valuable in a tightening interest rate environment, providing protection against potential losses in TLT.

# Recommendations (Numbered)
1. **Reduce TLT Position**: Decrease TLT holdings by 20% to 120 units to mitigate exposure to potential credit downgrades; target weight 10% of portfolio; timeframe: immediate.
2. **Increase GLD Position**: Reallocate 15% of the cash position into GLD for tactical exposure as a hedge against inflation and seek price recovery; timeframe: next 1-3 months.
3. **Maintain TLT-SWAP**: Retain existing TLT swap hedge to protect against rising interest rates and bond sell-offs; monitor closely for rebalancing.

# Key Risks & Unknowns
- Further downgrades or fiscal mismanagement could destabilize U.S. bonds.
- Geopolitical risks might alter demand for safe-haven assets, particularly gold.
- Economic data, such as U.S. CPI or PPI releases, could shift sentiment drastically.

# Confidence (0‑100%)
75% – The analysis reflects current market conditions and sentiments but is subject to influence from forthcoming economic indicators and geopolitical developments.

# References & Assumptions
- Credit ratings impact on bonds (Moody's downgrades, May 2025).
- Trade negotiations influencing asset volatility (U.S.-China trade deals affecting gold prices).
- Current interest rates and economic forecasts (Federal Reserve's stance on inflation and growth).

# Citations
- "Moody's cuts America's pristine credit rating, citing rising debt," Reuters.
- "Gold falls 3% as US and China strike tariff deal," Reuters.
- "Gold ETFs Melt Away as Safe Haven Status is Battered by Tariff Thaw," TipRanks.
- "Projected US Interest Rates in 5 Years," CCN.
"""
# Convert Markdown to HTML
html_content = markdown.markdown(raw_response)

# Wrap the HTML content in a basic HTML template
html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown Render</title>
    <style>
        body {{
            font-family: Inter, Arial, sans-serif;
            line-height: 1.6;
            margin: 20px;
        }}
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Oswald', sans-serif;
            color: #333;
        }}
        p {{
            margin-bottom: 10px;
        }}
        ul {{
            margin-left: 20px;
        }}
        </style>
</head>
<body>
    {html_content}
</body>
</html>
"""

# Write the HTML to a file
output_file = "output.html"
with open(output_file, "w", encoding="utf-8") as file:
    file.write(html_template)

# Open the file in the default web browser
webbrowser.open(f"file://{os.path.abspath(output_file)}")
