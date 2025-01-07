import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, initialize_agent
from langchain.vectorstores import FAISS
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Summarization Tool
def summarize_document(document_text: str) -> str:
    """
    Summarize a document, including results, numbers, and key metrics.
    """
    chat_llm = ChatOpenAI(temperature=0.3)
    prompt = (
        "Summarize the following document in a detailed, concise manner, focusing on:\n"
        "- Key innovations and techniques introduced.\n"
        "- Highlighted results with important metrics and numbers.\n"
        "- Major experiments conducted and their outcomes.\n"
        "- Any comparisons with existing methods and their improvements.\n"
        "Avoid including trivial details. Present the information in an organized and coherent format:\n\n"
        f"{document_text}"
    )
    response = chat_llm.invoke(prompt)
    return response.content


# Document QA Tool
def answer_document_question(question: str, retriever) -> str:
    """
    Answer a question based on specific chunks of the document.
    """
    chat_llm = ChatOpenAI(temperature=0.3)
    retriever_results = retriever.get_relevant_documents(question)

    # Combine the relevant chunks into a single prompt
    context = "\n\n".join([doc.page_content for doc in retriever_results])
    prompt = (
        "You are a knowledgeable and engaging AI assistant tasked with answering the user's question based on the provided document context. "
        "Your goal is to provide a detailed, accurate, and fully satisfying response by breaking down the question into clear sub-goals and addressing each one comprehensively. "
        "Follow these steps to ensure a complete and user-friendly answer:\n\n"
        "1. Analyze the user's question and split it into sub-goals or key parts in a scratchpad.\n"
        "2. Use the document context provided to answer each sub-goal with as much depth and clarity as possible. "
        "Incorporate key details, results, numbers, and explanations to make your response informative and actionable.\n"
        "3. Once all sub-goals are addressed, provide a final, cohesive answer that ties everything together. "
        "Ensure that your response is clear, concise, and leaves no part of the user's question unanswered.\n"
        "4. Keep the tone conversational, engaging, and professional, as if you are an expert explaining the content to a curious learner.\n\n"
        "Document Context:\n"
        f"{context}\n\n"
        "User Question: {question}\n\n"
        "Final Answer:"
    )
    response = chat_llm.invoke(prompt)
    return response.content


# Function to load and process the PDF
def load_and_process_pdf(pdf_path: str):
    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()
    text = "\n".join([doc.page_content for doc in documents])
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    return text, chunks


# Function to create the vector store
def create_vector_store(chunks):
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)
    return vector_store


def get_chatllm_response():
    pass


# Main function
if __name__ == "__main__":
    # Path to the PDF file
    pdf_path = "/Users/anujdutt/Downloads/Demo/Attention_is_all_you_need.pdf"
    document_text, chunks = load_and_process_pdf(pdf_path)
    vector_store = create_vector_store(chunks)

    # Initialize the QA chain
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    # Define the tools
    summarization_tool = Tool(
        name="DocumentSummarizer",
        func=lambda _: summarize_document(document_text),
        description="Use this tool to summarize the loaded document with a focus on results, numbers, and key metrics."
    )

    document_qa_tool = Tool(
        name="DocumentQA",
        func=lambda question: answer_document_question(question, retriever),
        description="Use this tool to answer questions based on the loaded document."
    )

    # Initialize the agent with both tools
    llm = ChatOpenAI(model="gpt-4", temperature=0.3)
    tools = [summarization_tool, document_qa_tool]
    agent_executor = initialize_agent(
        tools,
        llm,
        agent="zero-shot-react-description",
        verbose=True,
        return_intermediate_steps=True  # Enable intermediate steps
    )

    # Interactive loop
    print("PDF QA Assistant with Summarization and Document QA Tools. Type 'exit' to quit.")
    while True:
        question = input("\nEnter your question: ")
        if question.lower() == "exit":
            break

        # Run the agent
        try:
            response = agent_executor.invoke(question)
            # Aggregate intermediate steps and observations
            intermediate_steps = response.get("intermediate_steps", [])
            aggregated_response = "\n".join(
                [f"Action: {step[0]}, Observation: {step[1]}" for step in intermediate_steps]
            )
            # Print the aggregated response
            print("\nAggregated Intermediate Observations:")
            print(aggregated_response)

            # Print the final answer
            final_answer = response["output"]
            print("\nFinal Answer:")
            print(final_answer)

        except Exception as e:
                print(f"Error: {e}")
                continue

        # print(f"\nResponse: {response['output']}")