from langchain_openai import ChatOpenAI

def get_chatllm_response(question: str, context: str) -> str:
    print(f"Quesion: {question}\nContext: {context}")
    return f"This is a response from the assistant. {context}"
