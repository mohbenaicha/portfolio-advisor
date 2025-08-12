import { getPortfolios, loadArchives } from "./api.js";
import { initialUpdateQuestionPlaceholder } from "./portfolio.js";

export async function loadUserData() {
    await loadArchives();
    const portfolios = await getPortfolios(true); // force refresh on login
    window._portfolios = portfolios;
    await initialUpdateQuestionPlaceholder(portfolios);
    
    // Trigger summary panel render if function exists
    if (window.renderPortfolioSummary) window.renderPortfolioSummary();
}