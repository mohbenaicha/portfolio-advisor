from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
import asyncio, os


# production model
llm = ChatOpenAI(
    model="gpt-4o-mini", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY")
)


async def summarize_articles(articles, llm=llm):
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chain = load_summarize_chain(llm, chain_type="map_reduce")

    async def process_article(article):
        doc = Document(
            page_content=article.get("raw_article", ""),
            metadata={"url": article.get("link")},
        )
        chunks = splitter.split_documents([doc])
        summary = chain.run(chunks)
        article["summary"] = summary
        return article

    # Process articles concurrently
    summarized = await asyncio.gather(*[process_article(a) for a in articles])
    return summarized

# async def summarize_articles(articles, predefined_keywords, llm=llm):
#     splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
#     chain = load_summarize_chain(llm, chain_type="map_reduce")

#     async def process_article(article):
#         doc = Document(
#             page_content=article.get("raw_article", ""),
#             metadata={"url": article.get("url")},
#         )
#         chunks = splitter.split_documents([doc])

#         # Custom prompt to select keywords from a predefined set
#         prompt = (
#             "Summarize the following article and select the 1-2 most relevant keywords "
#             "from this list: {keywords}. "
#             "Return the result as a JSON object with the format: "
#             '{"summary": "<summary text>", "keywords": ["<keyword1>", "<keyword2>"]}.'
#         ).format(keywords=", ".join(predefined_keywords))

#         chain = load_summarize_chain(llm, chain_type="map_reduce", prompt_template=prompt)

#         # Run the chain
#         result = chain.run(chunks)

#         # Parse the JSON result
#         parsed_result = eval(result)  # Use `json.loads` if the result is a valid JSON string
#         article["summary"] = parsed_result.get("summary", "")
#         article["extracted_keywords"] = parsed_result.get("keywords", [])
#         return article

#     # Process articles concurrently
#     summarized = await asyncio.gather(*[process_article(a) for a in articles])
#     return summarized