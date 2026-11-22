import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


def load_llm():
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0
    )
    return llm


def generate_answer(question: str, retrieved_docs: list) -> str:

    llm = load_llm()

    context = ""

    for i, doc in enumerate(retrieved_docs, 1):
        context += f"""
        Review {i}:
        Product: {doc.metadata.get('product_name', 'Unknown')}
        Price: {doc.metadata.get('price', 'Unknown')}
        Source: {doc.metadata.get('source', 'Unknown')}

        Review Content:
        {doc.page_content}

        -------------------------
        """

    prompt = f"""
    You are BuySmart AI, an intelligent electronics shopping assistant.

    Answer the user's question using ONLY the information provided
    in the retrieved context.

    Instructions:
    - Give clear, useful and unbiased recommendations.
    - Compare products when relevant.
    - Consider both positive and negative feedback.
    - Do not invent specifications, prices, or reviews.
    - If information is insufficient, clearly say so.
    - Mention the product names when discussing them.
    - Make your answer easy to read.
    - Treat statements from reviews as user-reported experiences, not verified facts.
    - Do not generalize a single review into a guaranteed result.
    - Clearly distinguish reported experiences from objective specifications.
    - When making rankings, explain that rankings are based on the retrieved evidence. 

    CONTEXT:
    {context}

    USER QUESTION:
    {question}

    ANSWER:
    """

    response = llm.invoke(prompt)

    return response.content