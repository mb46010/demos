from langchain_openai import ChatOpenAI

# 1. Init an openai model
llm = ChatOpenAI(model="gpt-4.1",
                 temperature=0,
                 max_tokens=1000)
                 