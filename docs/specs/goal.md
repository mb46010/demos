test_cases = [
    {
        "question": "How many vacation days do new employees get?",
        "expected_answer": "New employees receive 25 vacation days per year, prorated for the first year based on start date.",
        "relevant_doc_ids": ["policy_vacation_2024.pdf"],
        "category": "factual_lookup"
    },
    {
        "question": "Can I work from another country temporarily?",
        "expected_answer": "Employees may work from abroad for up to 20 working days per calendar year with manager approval. Extended periods require HR and tax review.",
        "relevant_doc_ids": ["policy_remote_work.pdf", "policy_international_assignment.pdf"],
        "category": "policy_interpretation"
    },
    {
        "question": "What's the process for reporting harassment?",
        "expected_answer": "Reports can be made to your manager, HR Business Partner, or anonymously through the Ethics Hotline. All reports are investigated within 5 business days.",
        "relevant_doc_ids": ["policy_code_of_conduct.pdf", "policy_complaints_procedure.pdf"],
        "category": "sensitive_process"
    },
    # ... assume 150 total cases
]

Your task:
Build an evaluation pipeline that helps us understand where the system is failing. You have 25 minutes and can use any libraries. We need:

Retrieval evaluation — Are we retrieving the right documents? Implement metrics.
Answer quality evaluation — Is the generated answer correct? How do you measure this?
Failure categorization — When the system fails, why? (wrong retrieval, hallucination, outdated source, etc.)
Run evaluation — Execute on a sample test set and show results


# Current implementation (simplified)
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_community.vectorstores import FAISS

def get_answer(question: str, vector_store: FAISS, llm: AzureChatOpenAI) -> dict:
    """Current production code - returns answer and sources"""
    docs = vector_store.similarity_search(question, k=4)
    
    context = "\n\n".join([doc.page_content for doc in docs])
    
    prompt = f"""Answer the HR policy question based only on the context provided.
If the context doesn't contain the answer, say "I don't have information about this."

Context:
{context}

Question: {question}

Answer:"""
    
    response = llm.invoke(prompt)
    
    return {
        "answer": response.content,
        "sources": [doc.metadata.get("source", "unknown") for doc in docs]
    }