def get_portfolio_summary(selected_portfolio):
    return f"""
Asset names: {list({asset["name"]for asset in selected_portfolio.get("assets", [])})}
Asset types: {list({asset["asset_type"]for asset in selected_portfolio.get("assets", [])})}
Sectors: {list({asset["sector"] for asset in selected_portfolio.get("assets", [])})}
Regions: {list({asset["region"] for asset in selected_portfolio.get("assets", [])})}

"""


def get_asset_representation(selected_portfolio):

    assets_representation = "\n".join(
        [
            f"Ticker: {asset['ticker']}, Name: {asset['name']}, Type: {asset['asset_type']}, "
            f"Sector: {asset['sector']}, Region: {asset['region']}, Market Price: {asset['market_price']}, "
            f"Units Held: {asset['units_held']}, Is Hedge: {asset.get('is_hedge', False)}, "
            f"Hedges Asset: {asset.get('hedges_asset', 'None')}"
            for asset in selected_portfolio.get("assets", [])
        ]
    )

    assets_representation_str = f"""
Assets Representation:
{assets_representation}
"""
    return assets_representation_str


def get_exposure_summary(selected_portfolio):
    exposure_summary = {
        "regions": {},
        "sectors": {},
        "asset_types": {},
    }

    for asset in selected_portfolio.get("assets", []):
        region = asset["region"]
        sector = asset["sector"]
        asset_type = asset["asset_type"]
        value = asset["units_held"] * asset["market_price"]

        exposure_summary["regions"][region] = (
            exposure_summary["regions"].get(region, 0) + value
        )
        exposure_summary["sectors"][sector] = (
            exposure_summary["sectors"].get(sector, 0) + value
        )
        exposure_summary["asset_types"][asset_type] = (
            exposure_summary["asset_types"].get(asset_type, 0) + value
        )

    assets_representation_str = f"""
Portfolio Exposure Summary:
Regions: {exposure_summary["regions"]}
Sectors: {exposure_summary["sectors"]}
Asset Types: {exposure_summary["asset_types"]}
"""
    return assets_representation_str


def get_portfolio(selected_portfolio: dict) -> str:
    portfolio_summary = get_portfolio_summary(selected_portfolio)
    assets_representation = get_asset_representation(selected_portfolio)
    exposure_summary = get_exposure_summary(selected_portfolio)

    portfolio_str = f"""
Portfolio Summary:
{portfolio_summary}
Assets Representation:
{assets_representation}
Portfolio Exposure Summary:
{exposure_summary}
"""
    return portfolio_str
