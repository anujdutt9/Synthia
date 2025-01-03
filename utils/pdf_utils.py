import os.path
from dotenv import load_dotenv
from pathlib import Path
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_pdf_text(fpath_pdf: Path):
    pdf_reader = PdfReader(fpath_pdf)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    return text


def get_chunks_from_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)

    return chunks

def get_text_embeddings(fpath_pdf: Path, chunks: list[str], fpath_index: Path):
    embeddings = OpenAIEmbeddings()
    if os.path.exists(fpath_index):
        return FAISS.load_local(fpath_index.name, embeddings, allow_dangerous_deserialization=True)
    else:
        vectorstores = FAISS.from_texts(chunks, embeddings)
        store_name = fpath_pdf.name.split(".")[0]
        vectorstores.save_local(f"{store_name}.faiss")
        return vectorstores

def get_relevant_chunks(query: str, vectorstores: FAISS, top_k: int = 3):
    docs = vectorstores.similarity_search(query, top_k=top_k)
    relevant_chunks = [doc.page_content for doc in docs]
    return relevant_chunks