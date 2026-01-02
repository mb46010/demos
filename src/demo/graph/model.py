"""Module for initializing the ChatOpenAI model."""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# 1. Init an openai model
llm = ChatOpenAI(model="gpt-4.1", temperature=0, max_tokens=10000)
