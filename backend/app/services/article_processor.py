import asyncio
from typing import List
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from openai import OpenAI
from pydantic import SecretStr
from app.config import OPEN_AI_API_KEY, SUMMARY_LLM, EMBEDDING_MODEL
from app.utils.advisor_utils import count_tokens


# production model
summary_client = ChatOpenAI(
    model=SUMMARY_LLM, temperature=0, api_key=SecretStr(OPEN_AI_API_KEY)
)
embedding_client = OpenAI(api_key=OPEN_AI_API_KEY)


def sync_batch_embed(texts: list[str]) -> list[list[float]]:
    """
    Synchronously embed a batch of texts using OpenAI's embedding model.
    """
    response = embedding_client.embeddings.create(
        model=EMBEDDING_MODEL, input=texts  # list of strings
    )
    return [item.embedding for item in response.data]


async def batch_embed(texts: list[str]) -> list[list[float]]:
    asnyc_loop = asyncio.get_event_loop()
    return await asnyc_loop.run_in_executor(None, sync_batch_embed, texts)


async def embed_articles(articles: List[dict]) -> List[dict]:
    texts = [a["summary"] for a in articles]

    # Count input tokens for embeddings
    total_embedding_text = " ".join(texts)
    embedding_input_tokens = count_tokens(total_embedding_text, EMBEDDING_MODEL)
    print(f"Embedding input tokens: {embedding_input_tokens}")

    embeddings = await batch_embed(texts)
    for article, emb in zip(articles, embeddings):
        article["summary_embedding"] = emb

    return articles


async def process_article(article, splitter, chain, max_summary_length):
    # Debug: Check what fields are actually available
    print(f"DEBUG - Article: {article.get('link', 'unknown')} \n")

    # Use raw_article as before (no assumptions)
    content = article.get("raw_article", "")
    if len(content) < 50:
        return article, 0, 0

    if len(content) > 8000:
        content = content[:8000]

    doc = Document(
        page_content=content,
        metadata={"url": article.get("link")},
    )
    chunks = splitter.split_documents([doc])

    # Pass documents and max_length
    response = await chain.arun(
        {"input_documents": chunks, "max_length": max_summary_length}
    )  # COMMENTED OUT TO SAVE API COSTS

    article["summary"] = response
    return article


async def summarize_articles(articles, llm=summary_client, max_summary_length=300):
    # Filter out articles with insufficient content
    filtered_articles = []
    for article in articles:
        raw_article = article.get("raw_article", "")
        if len(raw_article) >= 50:
            filtered_articles.append(article)
        else:
            print(f"SKIPPING: only {len(raw_article)} chars")

    print(
        f"Processing {len(filtered_articles)} articles (filtered from {len(articles)})"
    )

    splitter = CharacterTextSplitter(chunk_size=3000, chunk_overlap=200)

    custom_prompt = """
    Summarize the following text in {max_length} characters or less. 
    Focus on key facts. Be concise and direct. 
    Keep important entity names, dates and figures in the summary.
    
    {text}
    
    Summary:"""

    from langchain.prompts import PromptTemplate

    prompt = PromptTemplate(
        template=custom_prompt, input_variables=["text", "max_length"]
    )

    # Use "stuff" chain type with custom prompt
    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)

    results = await asyncio.gather(*[process_article(a, splitter, chain, max_summary_length) for a in filtered_articles])
    summarized = [result for result in results]
    return summarized


async def summarize_and_embed_articles(articles, llm=summary_client) -> List[dict]:
    print(f"Starting summarization of {len(articles)} articles...")
    summarized = await summarize_articles(articles, llm=llm)
    print(f"Completed summarization, now embedding {len(summarized)} articles...")
    summarize_and_embedded = await embed_articles(summarized)
    return summarize_and_embedded
