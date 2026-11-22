
from research import tavily_search
from product import product_search
from core.creating_doc import prepare_documents
from core.chunking import split_documents
from core.vector_store import (
    build_vector,
    get_retriver,
    delete_vector_store
)
from core.generation import generate_answer


def run_buy_smart(query: str):

    # --------------------------------------------------
    # 1. Clear previous research session
    # --------------------------------------------------
    print("\n[1] Clearing previous research data...")

    delete_vector_store()

    # --------------------------------------------------
    # 2. Search products
    # --------------------------------------------------
    print("\n[2] Searching products...")

    products = product_search.search_products(query=query)

    if not products:
        return "No products found for your query."

    print(f"\nProducts found: {len(products)}")

    for product in products:
        print(
            f"- {product.get('title', 'Unknown')} | "
            f"{product.get('price', 'Price unavailable')}"
        )

    # --------------------------------------------------
    # 3. Search reviews
    # --------------------------------------------------
    print("\n[3] Searching reviews...")

    review_list = []

    for i, product in enumerate(products, 1):

        title = product.get("title", "Unknown product")

        print(f"Searching reviews {i}/{len(products)}: {title}")

        reviews = tavily_search.search_reviews(title)

        review_list.append(reviews)

    # --------------------------------------------------
    # 4. Merge product data and reviews
    # --------------------------------------------------
    print("\n[4] Merging product information...")

    final = tavily_search.final_dict(products, review_list)

    # --------------------------------------------------
    # 5. Clean data
    # --------------------------------------------------
    print("\n[5] Cleaning data...")

    final = tavily_search.clean_data(final)

    if not final:
        return "No usable product data remained after cleaning."

    print(f"Products after cleaning: {len(final)}")

    print("\nCleaned products:")

    for product in final:
        print(
            f"- {product.get('title', 'Unknown')} | "
            f"{product.get('price', 'Price unavailable')}"
        )

    # --------------------------------------------------
    # 6. Prepare documents
    # --------------------------------------------------
    print("\n[6] Preparing documents...")

    documents = prepare_documents(final)

    print(f"Documents created: {len(documents)}")

    # --------------------------------------------------
    # 7. Chunk documents
    # --------------------------------------------------
    print("\n[7] Chunking documents...")

    chunks = split_documents(documents)

    print(f"Chunks created: {len(chunks)}")

    # --------------------------------------------------
    # 8. Build vector database
    # --------------------------------------------------
    print("\n[8] Building vector database...")

    vector_store = build_vector(chunks)

    print(
        f"Stored chunks: "
        f"{vector_store._collection.count()}"
    )

    # --------------------------------------------------
    # 9. Initial recommendation
    # --------------------------------------------------
    print("\n[9] Generating initial recommendations...")

    # IMPORTANT:
    # Use ALL chunks for initial product comparison.
    # Do not restrict the initial recommendation to
    # only the top-k semantic retrieval results.

    comparison_docs = chunks

    print(f"Chunks passed to LLM: {len(comparison_docs)}")

    print("\nProducts passed to LLM:")

    unique_products = set()

    for doc in comparison_docs:

        product_name = doc.metadata.get(
            "product_name",
            "Unknown"
        )

        unique_products.add(product_name)

        print(f"- {product_name}")

    print(
        f"\nUnique products available for comparison: "
        f"{len(unique_products)}"
    )

    answer = generate_answer(query, comparison_docs)

    # --------------------------------------------------
    # 10. Return answer
    # --------------------------------------------------
    print("\n[10] Research completed.")

    return answer


# ------------------------------------------------------
# Follow-up question helper
# ------------------------------------------------------

def answer_follow_up(question: str, vector_store):

    retriever = get_retriver(vector_store, k=6)

    retrieved_docs = retriever.invoke(question)

    print(f"\nFollow-up chunks retrieved: {len(retrieved_docs)}")

    print("\nRetrieved products:")

    for doc in retrieved_docs:
        print(
            "- ",
            doc.metadata.get("product_name", "Unknown")
        )

    if not retrieved_docs:
        return "I couldn't find relevant information in the research."

    response = generate_answer(question, retrieved_docs)

    return response
