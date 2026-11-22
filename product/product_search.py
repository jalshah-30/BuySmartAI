import os
import serpapi
import re
from dotenv import load_dotenv
load_dotenv()

client=serpapi.Client(
    api_key=os.getenv("SERPAPI_KEY"),
    timeout=10
)

def search_products(query: str, limit: int = 10)->list:

    results = client.search({
        "engine": "google_shopping",
        "q": query,
        "gl": "in",
        "hl": "en"
    })

    products = results.get("shopping_results", [])

    cleaned_products = []

    for product in products[:limit]:

        cleaned_products.append({
            "title": product.get("title"),
            "price": product.get("price"),
            "source": product.get("source"),
            "rating": product.get("rating"),
            "reviews": product.get("reviews"),
            "link": product.get("link")
        })

    return cleaned_products

def extract_budget(query: str):
    match = re.search(r"(?:under|below|less than|within|upto|up to)\s*₹?\s*(\d+)", query.lower())

    if match:
        return int(match.group(1))

    return None