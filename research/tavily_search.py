from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")
tavily_ai = TavilyClient(api_key=api_key) if api_key else None


def search_reviews(product: str) -> dict:
    """Search for customer reviews of a product and return them as a dictionary."""

    if not tavily_ai:
        return {"error": "TAVILY_API_KEY is missing from the .env file."}

    try:
        response = tavily_ai.search(
            query=f"{product} user reviews customer feedback India",
            search_depth="advanced",
            include_domains=[
                "amazon.in",
                "flipkart.com",
                "mouthshut.com",
                "reddit.com"
            ],
            max_results=8
        )

        results = response.get("results", [])

        if not results:
            return {"message": f"No reviews found for {product}."}

        review_dict = {}

        for i, r in enumerate(results, start=1):
            review_dict[f"Review {i}"] = {
                "title": r.get("title", ""),
                "content": r.get("content", "")[:2000]
            }

        return review_dict

    except Exception as e:
        return {"error": f"Review search failed: {e}"}


def final_dict(product_search: list, all_reviews: list) -> list:
    for product in product_search:
        product_title = product["title"]

        for review_dict in all_reviews:
            for review in review_dict.values():

                if product_title.lower() in review["title"].lower():
                    product["review"] = review["content"]
                    break

    return product_search


import re
import html

def clean_data(data):

    if isinstance(data, dict):
        cleaned = {}

        for key, value in data.items():
            cleaned_value = clean_data(value)

            if cleaned_value not in (None, "", [], {}):
                cleaned[key] = cleaned_value

        return cleaned

    elif isinstance(data, list):
        cleaned_list = []

        for item in data:
            cleaned_item = clean_data(item)

            if cleaned_item not in (None, "", [], {}):
                cleaned_list.append(cleaned_item)

        return cleaned_list

    elif isinstance(data, str):

        # Decode HTML entities
        data = html.unescape(data)

        # Replace unusual whitespace
        data = data.replace("\xa0", " ")
        data = data.replace("\u200b", "")

        # Remove unnecessary whitespace
        data = re.sub(r"\s+", " ", data)

        # Remove website UI noise
        noise_patterns = [
            r"CancelReport",
            r"Sending feedback\.{0,3}",
            r"HelpfulThank you for your feedback",
            r"Sorry, we failed to record your vote",
            r"Notification Preferences",
            r"24x7 Customer Care",
        ]

        for pattern in noise_patterns:
            data = re.sub(pattern, "", data, flags=re.IGNORECASE)

        # Clean spaces again after removals
        data = re.sub(r"\s+", " ", data).strip()

        return data

    else:
        return data

import re

def filter_by_budget(products: list, budget=None) -> list:

    # If the user didn't specify a budget, return all products
    if budget is None:
        return products

    filtered_products = []

    for product in products:
        price = product.get("price", "")

        # Extract numeric price
        price_value = re.sub(r"[^\d.]", "", str(price))

        if not price_value:
            continue

        price_value = float(price_value)

        if price_value <= budget:
            filtered_products.append(product)

    return filtered_products