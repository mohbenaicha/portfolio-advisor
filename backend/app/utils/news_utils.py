def news_summary_string_representation(articles):
    """
    Convert a list of articles into a string representation for OpenAI.
    """
    return "\n\n".join([f"Title: {a['title']}\nSummary: {a['summary']}\nURL: {a['url']}" for a in articles])

