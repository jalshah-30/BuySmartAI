from langchain_core.documents import Document

def prepare_documents(products):

    documents = []

    for product in products:

        content = f"""
        Product: {product.get('title', 'Unknown')}
        Price: {product.get('price', 'Unknown')}
        Seller: {product.get('source', 'Unknown')}
        Rating: {product.get('rating', 'Not available')}

        Customer Reviews:
        {product.get('review', 'No reviews available')}
        """

        metadata = {
            "product_name": product.get("title", ""),
            "price": product.get("price", ""),
            "source": product.get("source", ""),
            "rating": product.get("rating", 0)
        }

        doc = Document(
            page_content=content,
            metadata=metadata
        )

        documents.append(doc)

    return documents