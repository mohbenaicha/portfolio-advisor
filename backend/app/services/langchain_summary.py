from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document

llm = ChatOpenAI(temperature=0)

async def summarize_articles(articles):
    summarized = []
    for a in articles:
        doc = Document(page_content=a.get("raw_article", ""))
        splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents([doc])
        chain = load_summarize_chain(llm, chain_type="refine")
        summary = chain.run(chunks)
        a["summary"] = summary
        summarized.append(a)
    return summarized
