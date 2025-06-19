import asyncio
from typing import List
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from openai import OpenAI
from app.config import OPEN_AI_API_KEY, SUMMARY_LLM, EMBEDDING_MODEL


# production model
summary_client = ChatOpenAI(model=SUMMARY_LLM, temperature=0, openai_api_key=OPEN_AI_API_KEY)
embedding_client = OpenAI(api_key=OPEN_AI_API_KEY)


def sync_batch_embed(texts: list[str]) -> list[list[float]]:
    """
    Synchronously embed a batch of texts using OpenAI's embedding model.
    """
    response = embedding_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts  # list of strings
    )
    return [item.embedding for item in response.data]


async def batch_embed(texts: list[str]) -> list[list[float]]:
    asnyc_loop = asyncio.get_event_loop()
    return await asnyc_loop.run_in_executor(None, sync_batch_embed, texts)


async def embed_articles(articles: List[dict]) -> List[dict]:
    texts = [a["summary"] for a in articles]
    embeddings = await batch_embed(texts)
    for article, emb in zip(articles, embeddings):
        article["summary_embedding"] = emb
    return articles

async def summarize_articles(articles, llm=summary_client):
    splitter = CharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
    chain = load_summarize_chain(llm, chain_type="refine")

    async def process_article(article):
        doc = Document(
            page_content=article.get("raw_article", ""),
            metadata={"url": article.get("link")},
        )
        chunks = splitter.split_documents([doc])
        summary = await chain.arun(chunks)
        article["summary"] = summary
        return article

    # Process articles concurrently
    summarized = await asyncio.gather(*[process_article(a) for a in articles])
    return summarized

async def summarize_and_embed_articles(articles, llm=summary_client) -> List[dict]:
    summarized = await summarize_articles(articles, llm=llm)
    summarize_and_embedded = await embed_articles(summarized)
    return summarize_and_embedded