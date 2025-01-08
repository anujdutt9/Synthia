import os
import re
from typing import List
from dotenv import load_dotenv
import tiktoken
from langchain_openai.chat_models import ChatOpenAI
from langchain.agents import Tool, initialize_agent, AgentExecutor
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI Embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
# Initialize the tokenizer for token counting
enc = tiktoken.get_encoding("gpt2")


def count_tokens(text: str) -> int:
    """
    Count the number of tokens in a given text using tiktoken.
    """
    return len(enc.encode(text))


def split_text_into_chunks(text: str, max_tokens: int = 1500, overlap: int = 150) -> List[str]:
    """
    Split text into chunks that do not exceed max_tokens, with a specified overlap.
    """
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + max_tokens
        chunk = enc.decode(tokens[start:end])
        chunks.append(chunk)
        start += max_tokens - overlap  # Move start forward, maintaining overlap
    return chunks


def filter_chunks(chunks: List[str]) -> List[str]:
    """
    Filter out lines with fewer than 2 words from each chunk.
    """
    filtered_chunks = []
    for chunk in chunks:
        # Remove lines with fewer than 2 words
        cleaned_chunk = "\n".join([line for line in chunk.split("\n") if len(line.split()) >= 2])
        if cleaned_chunk.strip():  # Only add non-empty chunks
            filtered_chunks.append(cleaned_chunk)
    return filtered_chunks


def load_and_process_pdf(pdf_path: str, chunk_size: int = 1500, chunk_overlap: int = 150) -> (List, List):
    """
    Load a PDF file, extract text, split it into chunks, and filter the chunks.
    """
    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_documents(documents)

    # Filter out noisy chunks
    filtered_chunks = filter_chunks([doc.page_content for doc in chunks])
    return documents, filtered_chunks


def create_or_load_vector_store(index_path: str, chunks: List[str]) -> FAISS:
    """
    Load an existing FAISS vector store if available, or create a new one from the provided filtered chunks.
    """
    if os.path.exists(index_path):
        vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        print("Loaded existing vector store.")
    else:
        if not chunks:
            raise ValueError("Chunks must be provided to create a new vector store.")
        print("Creating a new vector store...")
        vector_store = FAISS.from_texts(chunks, embeddings)
        vector_store.save_local(index_path)
        print("Vector store created and saved.")
    return vector_store


def summarize_text(text: str) -> str:
    """
    Summarize a given text using the GPT-4 model.
    """
    chat_llm = ChatOpenAI(
        temperature=0.3,
        openai_api_key=OPENAI_API_KEY,
        model_name="gpt-4o"
    )
    prompt = (
        "Summarize the following text in a detailed manner:\n\n"
        f"{text}"
    )
    response = chat_llm.invoke(prompt)
    return response.content


def answer_document_question(question: str, retriever) -> str:
    """
    Answer a question based on the document using the retriever.
    """
    chat_llm = ChatOpenAI(
        temperature=0.3,
        openai_api_key=OPENAI_API_KEY,
        model_name="gpt-4o"
    )
    # retriever_results = retriever.get_relevant_documents(question)
    retriever_results = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in retriever_results])
    prompt = (
        "Answer the following question based on the provided document context:\n\n"
        f"Document Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )
    response = chat_llm.invoke(prompt)
    return response.content


def initialize_agent_executor(documents: List, vector_store: FAISS) -> AgentExecutor:
    """
    Initialize the agent executor with summarization and QA tools using chunked summarization.
    """
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    summarization_tool = Tool(
        name="DocumentSummarizer",
        func=lambda _: summarize_text("\n\n".join([doc.page_content for doc in documents])),
        description="Use this tool to summarize the loaded document."
    )

    document_qa_tool = Tool(
        name="DocumentQA",
        func=lambda question: answer_document_question(question, retriever),
        description="Use this tool to answer questions based on the loaded document."
    )

    llm = ChatOpenAI(
        model_name="gpt-4o",
        temperature=0.3,
        openai_api_key=OPENAI_API_KEY
    )

    tools = [summarization_tool, document_qa_tool]
    agent_executor = initialize_agent(
        tools,
        llm,
        agent="zero-shot-react-description",
        verbose=True,
        return_intermediate_steps=False,
        handle_parsing_errors=True
    )

    return agent_executor


def get_agent_executor(pdf_path: str, index_path: str) -> AgentExecutor:
    """
    Process a PDF document, create/load FAISS index, and initialize the agent executor.
    """
    documents, filtered_chunks = load_and_process_pdf(pdf_path)
    vector_store = create_or_load_vector_store(index_path, filtered_chunks)
    agent_executor = initialize_agent_executor(documents, vector_store)
    return agent_executor


def get_llm_response(question: str, agent_executor: AgentExecutor) -> str:
    """
    Get the LLM response for a given question using the agent executor.
    """
    try:
        response = agent_executor.invoke(question)
        return response['output']
    except Exception as e:
        return f"An error occurred: {e}"


if __name__ == "__main__":
    from pathlib import Path
    pdf_path = "/Users/anujdutt/Downloads/Demo/Attention_is_all_you_need.pdf"
    store_name = Path(pdf_path).name.split('.')[0]
    index_path = f"vectorstores/{store_name}.index"

    agent_executor = get_agent_executor(pdf_path, index_path)

    while True:
        question = input("Ask a question: ")
        response = get_llm_response(question, agent_executor)
        print("Response:", response['output'])