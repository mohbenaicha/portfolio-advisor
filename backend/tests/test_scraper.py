import json

from app.services.article_scraper import extract_with_readability


def test_article_scraping_and_saving():
    articles = [
        {
            "Title": "Paramount's Super Bowl Boost And Studio Strength Help Offset Streaming Miss: Analyst",
            "Link": "https://www.benzinga.com/general/entertainment/25/05/45358172/paramounts-super-bowl-boost-and-studio-strength-help-offset-streaming-miss-analyst",
        },
        {
            "Title": "Unity Software's Options: A Look at What the Big Money is Thinking",
            "Link": "https://www.benzinga.com/insights/options/25/05/45357814/unity-softwares-options-a-look-at-what-the-big-money-is-thinking",
        },
        {
            "Title": "Paramount's Super Bowl Boost And Studio Strength Help Offset Streaming Miss: Analyst - Paramount Glb  ( NASDAQ:PARA ) , Paramount Glb  ( NASDAQ:PARAA )",
            "Link": "https://www.benzinga.com/general/entertainment/25/05/45358172/paramounts-super-bowl-boost-and-studio-strength-help-offset-streaming-miss-analyst",
        },
        {
            "Title": "Unity Software's Options: A Look at What the Big Money is Thinking - Unity Software  ( NYSE:U )",
            "Link": "https://www.benzinga.com/insights/options/25/05/45357814/unity-softwares-options-a-look-at-what-the-big-money-is-thinking",
        },
        {
            "Title": "Pinterest Options Trading: A Deep Dive into Market Sentiment - Pinterest  ( NYSE:PINS )",
            "Link": "https://www.benzinga.com/insights/options/25/05/45357806/pinterest-options-trading-a-deep-dive-into-market-sentiment",
        },
        {
            "Title": "Decoding Roku's Options Activity: What's the Big Picture? - Roku  ( NASDAQ:ROKU )",
            "Link": "https://www.benzinga.com/insights/options/25/05/45357805/decoding-rokus-options-activity-whats-the-big-picture",
        },
        {
            "Title": "Why Shopify  ( SHOP )  Stock Hit A New 52-Week High Today - Shopify  ( NASDAQ:SHOP )",
            "Link": "https://www.benzinga.com/news/25/05/45357529/why-shopify-shop-stock-hit-a-new-52-week-high-today",
        },
        {
            "Title": "Unpacking the Latest Options Trading Trends in Fortinet - Fortinet  ( NASDAQ:FTNT )",
            "Link": "https://www.benzinga.com/insights/options/25/05/45356527/unpacking-the-latest-options-trading-trends-in-fortinet",
        },
        {
            "Title": "HubSpot's Options Frenzy: What You Need to Know - HubSpot  ( NYSE:HUBS )",
            "Link": "https://www.benzinga.com/insights/options/25/05/45355119/hubspots-options-frenzy-what-you-need-to-know",
        },
        {
            "Title": "ServiceNow's Options: A Look at What the Big Money is Thinking - ServiceNow  ( NYSE:NOW )",
            "Link": "https://www.benzinga.com/insights/options/25/05/45355095/servicenows-options-a-look-at-what-the-big-money-is-thinking",
        },
        {
            "Title": "EverCommerce Analysts Raise Their Forecasts After Upbeat Sales - EverCommerce  ( NASDAQ:EVCM )",
            "Link": "https://www.benzinga.com/25/05/45353504/evercommerce-analysts-raise-their-forecasts-after-upbeat-sales",
        },
        {
            "Title": "NU's Q1 Earnings Approaching: Time to Buy, Sell or Hold the Stock?",
            "Link": "https://www.zacks.com/stock/news/2467025/nus-q1-earnings-approaching-time-to-buy-sell-or-hold-the-stock",
        },
        {
            "Title": "Spotlight on Eaton Corp: Analyzing the Surge in Options Activity - Eaton Corp  ( NYSE:ETN )",
            "Link": "https://www.benzinga.com/insights/options/25/05/45349230/spotlight-on-eaton-corp-analyzing-the-surge-in-options-activity",
        },
        {
            "Title": "Byline Bank Expands Payments and Fintech Banking Group to Support Embedded Payment Solutions - Byline Bancorp  ( NYSE:BY )",
            "Link": "https://www.benzinga.com/pressreleases/25/05/g45349085/byline-bank-expands-payments-and-fintech-banking-group-to-support-embedded-payment-solutions",
        },
        {
            "Title": "This NeuroSense Therapeutics Analyst Begins Coverage On A Bullish Note; Here Are Top 3 Initiations For Monday - NeuroSense Therapeutics  ( NASDAQ:NRSN ) , Primis Finl  ( NASDAQ:FRST )",
            "Link": "https://www.benzinga.com/news/25/05/45347103/this-neurosense-therapeutics-analyst-begins-coverage-on-a-bullish-note-here-are-top-3-initiations-fo",
        },
        {
            "Title": "SelectQuote  ( SLQT )  Misses Q3 Earnings and Revenue Estimates",
            "Link": "https://www.zacks.com/stock/news/2466601/selectquote-slqt-misses-q3-earnings-and-revenue-estimates",
        },
        {
            "Title": "ProAssurance Q1 Earnings Miss Estimates on Declining Premiums",
            "Link": "https://www.zacks.com/stock/news/2466596/proassurance-q1-earnings-miss-estimates-on-declining-premiums",
        },
        {
            "Title": "With Warren Buffett Stepping Down as CEO, Will Berkshire Hathaway Sell Apple Stock?",
            "Link": "https://www.fool.com/investing/2025/05/12/will-berkshire-hathaway-sell-apple-stock-with-warr/",
        },
        {
            "Title": "Warren Buffett's Cash Mountain Grows To $314 Billion As Berkshire Hathaway Emerges As Top Treasury-Bill Holder: 'We'd Spend $100 Billion' If the Right Deal Came Along, Says Oracle Of Omaha",
            "Link": "https://www.benzinga.com/markets/equities/25/05/45342110/warren-buffetts-cash-mountain-grows-to-314-billion-as-berkshire-hathaway-emerges-as-top-treasury",
        },
        {
            "Title": "This Undervalued Restaurant Stock Is Up About 10% Since a Member of the Audience Mistakenly Asked About It at Berkshire Hathaway's Annual Meeting",
            "Link": "https://www.fool.com/investing/2025/05/12/this-undervalued-restaurant-stock-is-up-about-10-s/",
        },
        {
            "Title": "16 Words From Warren Buffett That Should Have Apple Stock Investors Excited",
            "Link": "https://www.fool.com/investing/2025/05/11/16-words-from-warren-buffett-should-have-apple/",
        },
        {
            "Title": "Faruqi & Faruqi Reminds Open Lending Investors of the Pending Class Action Lawsuit with a Lead Plaintiff Deadline of June 30, 2025 - LPRO - Open Lending  ( NASDAQ:LPRO )",
            "Link": "https://www.benzinga.com/pressreleases/25/05/g45337469/faruqi-faruqi-reminds-open-lending-investors-of-the-pending-class-action-lawsuit-with-a-lead-plain",
        },
        {
            "Title": "Faruqi & Faruqi Reminds Bakkt Holdings Investors of the Pending Class Action Lawsuit with a Lead Plaintiff Deadline of June 2, 2025 - BKKT - Bakkt Hldgs  ( NYSE:BKKT )",
            "Link": "https://www.benzinga.com/pressreleases/25/05/g45337446/faruqi-faruqi-reminds-bakkt-holdings-investors-of-the-pending-class-action-lawsuit-with-a-lead-pla",
        },
        {
            "Title": "Where Will VeriSign Stock Be in 3 Years?",
            "Link": "https://www.fool.com/investing/2025/05/11/where-will-verisign-stock-be-in-3-years/",
        },
        {
            "Title": "TBBK DEADLINE NOTICE: ROSEN, A GLOBALLY RESPECTED LAW FIRM, Encourages The Bancorp, Inc. Investors to Secure Counsel Before Important May 16 Deadline in Securities Class Action - TBBK",
            "Link": "https://markets.businessinsider.com/news/stocks/tbbk-deadline-notice-rosen-a-globally-respected-law-firm-encourages-the-bancorp-inc.-investors-to-secure-counsel-before-important-may-16-deadline-in-securities-class-action-tbbk-1034702726",
        },
        {
            "Title": "Warren Buffett Says 'Tim Cook Has Made Berkshire A Lot More Money,' Apple's $95 Million Privacy Lawsuit Settlement And More: Top Appleverse Updates - Apple  ( NASDAQ:AAPL )",
            "Link": "https://www.benzinga.com/markets/equities/25/05/45335120/apple-incs-whirlwind-week-from-steve-jobs-resurfaced-interview-to-privacy-lawsuit-settlement",
        },
        {
            "Title": "Does Warren Buffett Know Something Wall Street Doesn't? Why the Billionaire Investor Owns This High-Yielding Dividend Stock.",
            "Link": "https://www.fool.com/investing/2025/05/10/does-warren-buffett-know-something-wall-street-doe/",
        },
        {
            "Title": "Trump Media Reports First Quarter 2025 Results",
            "Link": "https://www.globenewswire.com/news-release/2025/05/09/3078559/0/en/Trump-Media-Reports-First-Quarter-2025-Results.html",
        },
        {
            "Title": "What the Options Market Tells Us About Baidu - Baidu  ( NASDAQ:BIDU )",
            "Link": "https://www.benzinga.com/insights/options/25/05/45328549/what-the-options-market-tells-us-about-baidu",
        },
        {
            "Title": "UNH INVESTOR ALERT: Bronstein, Gewirtz & Grossman LLC Announces that UnitedHealth Group Incorporated Investors with Substantial Losses Have Opportunity to Lead Class Action Lawsuit - UnitedHealth Group  ( NYSE:UNH )",
            "Link": "https://www.benzinga.com/pressreleases/25/05/g45328365/unh-investor-alert-bronstein-gewirtz-grossman-llc-announces-that-unitedhealth-group-incorporated-i",
        },
        {
            "Title": "Shopify Grows Fast, But Profit Questions Won't Go Away - Shopify  ( NASDAQ:SHOP )",
            "Link": "https://www.benzinga.com/analyst-ratings/price-target/25/05/45328107/shopify-shows-strong-global-momentum-but-guidance-raises-questions-on-profitability-",
        },
        {
            "Title": "Pinterest Sees Solid Q1: Analyst Highlights Growing Platform Monetization Potential Pinterest Analyst Cites Strong Ad Strategy, Reiterates Buy For Stock - Pinterest  ( NYSE:PINS )",
            "Link": "https://www.benzinga.com/general/social-media/25/05/45327696/pinterest-sees-solid-q1-analyst-highlights-growing-platform-monetization-potential",
        },
        {
            "Title": "Pinterest's Options: A Look at What the Big Money is Thinking - Pinterest  ( NYSE:PINS )",
            "Link": "https://www.benzinga.com/insights/options/25/05/45327240/pinterests-options-a-look-at-what-the-big-money-is-thinking",
        },
        {
            "Title": "Galaxy Digital approved for US domicile, clearing way for Nasdaq listing",
            "Link": "https://cointelegraph.com/news/galaxy-digital-approved-us-domicile-nasdaq-listing",
        },
        {
            "Title": "Dell Technologies's Options: A Look at What the Big Money is Thinking - Dell Technologies  ( NYSE:DELL )",
            "Link": "https://www.benzinga.com/insights/options/25/05/45324724/dell-technologiess-options-a-look-at-what-the-big-money-is-thinking",
        },
        {
            "Title": "Market Whales and Their Recent Bets on APP Options - AppLovin  ( NASDAQ:APP )",
            "Link": "https://www.benzinga.com/insights/options/25/05/45324723/market-whales-and-their-recent-bets-on-app-options",
        },
        {
            "Title": "Applovin Wins Analyst Conviction With AI-Driven Ad Strength - AppLovin  ( NASDAQ:APP )",
            "Link": "https://www.benzinga.com/analyst-ratings/analyst-color/25/05/45323056/applovins-rapid-ad-growth-ai-gains-drive-hike-in-analyst-price-forecast",
        },
        {
            "Title": "Compass Analysts Lower Their Forecasts After Weaker-Than-Expected Results - Compass  ( NYSE:COMP )",
            "Link": "https://www.benzinga.com/25/05/45322954/compass-analysts-lower-their-forecasts-after-weaker-than-expected-results",
        },
        {
            "Title": "These Analysts Raise Their Forecasts On Appian After Upbeat Q1 Results - Appian  ( NASDAQ:APPN )",
            "Link": "https://www.benzinga.com/25/05/45322735/these-analysts-raise-their-forecasts-on-appian-after-upbeat-q1-results",
        },
        {
            "Title": "Palantir Technologies Unusual Options Activity - Palantir Technologies  ( NASDAQ:PLTR )",
            "Link": "https://www.benzinga.com/insights/options/25/05/45318721/palantir-technologies-unusual-options-activity",
        },
        {
            "Title": "Questex's ULTRA Summit and GMITE Conclude Co-Located Events at Chateau Elan",
            "Link": "https://www.benzinga.com/pressreleases/25/05/g45318604/questexs-ultra-summit-and-gmite-conclude-co-located-events-at-chateau-elan",
        },
        {
            "Title": "Remitly Announces Upcoming Investor Conference Participation",
            "Link": "https://www.globenewswire.com/news-release/2025/05/09/3078313/0/en/Remitly-Announces-Upcoming-Investor-Conference-Participation.html",
        },
        {
            "Title": "Remitly Announces Upcoming Investor Conference Participation - Remitly Global  ( NASDAQ:RELY )",
            "Link": "https://www.benzinga.com/pressreleases/25/05/g45317610/remitly-announces-upcoming-investor-conference-participation",
        },
        {
            "Title": "MGIC Investment Corporation  ( MTG )  Hit a 52 Week High, Can the Run Continue?",
            "Link": "https://www.zacks.com/stock/news/2465981/mgic-investment-corporation-mtg-hit-a-52-week-high-can-the-run-continue",
        },
        {
            "Title": "Mark Cuban Slams Memecoins, Says They Set A 'Bad Example' For New Crypto Investors - Trump Media & Tech Gr  ( NASDAQ:DJT )",
            "Link": "https://www.benzinga.com/government/regulations/25/05/45314812/mark-cuban-slams-memecoins-says-they-set-a-bad-example-for-new-crypto-investors",
        },
        {
            "Title": "Essent Group  ( ESNT )  Tops Q1 Earnings and Revenue Estimates",
            "Link": "https://www.zacks.com/stock/news/2465852/essent-group-esnt-tops-q1-earnings-and-revenue-estimates",
        },
        {
            "Title": "Bitcoin Tops $102K for First Time Since January: ETFs in Focus",
            "Link": "https://www.zacks.com/stock/news/2465786/bitcoin-tops-102k-for-first-time-since-january-etfs-in-focus",
        },
        {
            "Title": "Gogo Earnings Are Imminent; These Most Accurate Analysts Revise Forecasts Ahead Of Earnings Call - Gogo  ( NASDAQ:GOGO )",
            "Link": "https://www.benzinga.com/25/05/45310908/gogo-earnings-are-imminent-these-most-accurate-analysts-revise-forecasts-ahead-of-earnings-call",
        },
        {
            "Title": "2 Popular AI Stock to Sell Before They Fall 64% and 67%, According to Certain Wall Street Analysts",
            "Link": "https://www.fool.com/investing/2025/05/09/2-ai-stocks-to-sell-before-fall-67-wall-street/",
        },
        {
            "Title": "Rumble CEO confirms Tether-collab crypto wallet to launch in Q3",
            "Link": "https://cointelegraph.com/news/rumble-launch-bitcoin-stablecoin-wallet-q3",
        },
        {
            "Title": "Arm CFO Explains Why Company Withheld Fiscal 2026 Full Year Guidance Amid Uncertainty From Customers And Tariff Impacts: 'The Amount Of Signals I'm Getting…' - ARM Holdings  ( NASDAQ:ARM )",
            "Link": "https://www.benzinga.com/markets/25/05/45306998/arm-cfo-explains-why-company-withheld-fiscal-2026-full-year-guidance-amid-uncertainty-from-customers-and-",
        },
        {
            "Title": "GOHEALTH ALERT: Bragar Eagel & Squire, P.C. is Investigating GoHealth, Inc. on Behalf of GoHealth Stockholders and Encourages Investors to Contact the Firm - GoHealth  ( NASDAQ:GOCO )",
            "Link": "https://www.benzinga.com/pressreleases/25/05/g45307001/gohealth-alert-bragar-eagel-squire-p-c-is-investigating-gohealth-inc-on-behalf-of-gohealth-stockho",
        },
    ]

    scraped_content = {}
    for article in articles:
        try:
            summary = extract_with_readability(article["Link"])
            scraped_content[article["Title"]] = {
                "Link": article["Link"],
                "summary": summary,
            }
            print(f"✅ Scraped content for {article['Title']}")
        except Exception as e:
            print(f"Error fetching {article['Title']}: {e}")

    with open("./tests/article_content.json", "w", encoding="utf-8") as f:
        json.dump(scraped_content, f, ensure_ascii=False, indent=4)

    print("✅ Article scraping and saving test completed.")
