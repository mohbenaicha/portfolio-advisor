from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
import asyncio, os


# production model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))


async def summarize_articles(articles, llm=llm):
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    
    async def process_article(article):
        doc = Document(page_content=article.get("raw_article", ""), metadata={"url": article.get("url")})
        chunks = splitter.split_documents([doc])
        summary = chain.run(chunks)
        article["summary"] = summary
        return article

    # Process articles concurrently
    summarized = await asyncio.gather(*[process_article(a) for a in articles])
    return summarized
