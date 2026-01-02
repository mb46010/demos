"""Module for initializing the ChatOpenAI model."""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# 1. Init an openai model
llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0,
    max_tokens=10000,
).with_retry(
    retry_if_exception_type=(Exception,),  # You can specify RateLimitError, etc.
    wait_exponential_jitter=True,  # This enables exponential backoff with jitter
    stop_after_attempt=3,  # Number of retries
)
