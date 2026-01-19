import os

# from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI


def create_executor_chat_model() -> ChatGoogleGenerativeAI:
    gemini_api_key = os.environ["GOOGLE_API_KEY"]

    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        api_key=gemini_api_key,
    )
    return llm

def create_planner_chat_model() -> ChatGoogleGenerativeAI:
    gemini_api_key = os.environ["GOOGLE_API_KEY"]

    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        api_key=gemini_api_key,
    )
    return llm