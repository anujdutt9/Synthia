from langchain_openai import ChatOpenAI

def get_chatllm_response(question: str, context: str) -> str:
    print(f"Quesion: {question}\nContext: {context}")
    return f"This is a response from the assistant. {context}"

#ToDo: assistant should be able to summarize documents, perform QA on documents as well as answers random queries as well

# ToDo: Define Summarize tool
# ToDo: Define QA Tool