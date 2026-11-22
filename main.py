from core.rag_pipeline import run_buy_smart
from core.vector_store import load_vector_store, get_retriver, delete_vector_store
from core.generation import generate_answer


def main():

    query = input("What do you want to buy? ")

    # Run initial research pipeline
    answer = run_buy_smart(query)

    print("\n" + "=" * 50)
    print("BUYSMART AI RESULT")
    print("=" * 50)
    print(answer)

    # Load vector database for follow-up questions
    vector_store = load_vector_store()
    retriever = get_retriver(vector_store, k=4)

    print("\n" + "=" * 50)
    print("You can now ask follow-up questions about your research.")
    print("Type 'exit' or 'quit' to end the session.")
    print("=" * 50)

    while True:

        follow_up = input("\nYou: ").strip()

        # Exit condition
        if follow_up.lower() in ["exit", "quit"]:

            print("\nDeleting research data...")
            delete_vector_store()

            print("BuySmart AI: Goodbye!")
            break

        if not follow_up:
            continue

        # Retrieve relevant documents
        retrieved_docs = retriever.invoke(follow_up)

        if not retrieved_docs:
            print("\nBuySmart AI: I couldn't find relevant information in the research.")
            continue

        # Generate response
        response = generate_answer(follow_up, retrieved_docs)

        print("\nBuySmart AI:")
        print(response)


if __name__ == "__main__":
    main()