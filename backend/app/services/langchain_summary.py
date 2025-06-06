from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
import asyncio
from app.config import OPEN_AI_API_KEY, SUMMARY_MODEL


# production model
llm = ChatOpenAI(model=SUMMARY_MODEL, temperature=0, openai_api_key=OPEN_AI_API_KEY)


async def summarize_articles(articles, llm=llm):
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
