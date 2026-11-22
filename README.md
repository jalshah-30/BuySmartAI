# BuySmart AI

**BuySmart AI** is an AI-powered electronics research and shopping
assistant that helps users compare products, understand review evidence,
and make more informed purchasing decisions.

Instead of relying only on product specifications or a single review,
BuySmart AI searches for product information and review content,
organizes the information, and uses Retrieval-Augmented Generation (RAG)
to generate comparisons and recommendations.

> **Project status:** Under active development. Features listed under
> *Planned Features* are not implemented yet.

------------------------------------------------------------------------

## Features

### Currently implemented

-   Search for electronics products based on a natural-language shopping
    query.
-   Retrieve online review-related information using Tavily search.
-   Combine product-search results with review information.
-   Clean and filter retrieved data before processing.
-   Convert product information into documents and split documents into
    chunks.
-   Generate embeddings using a Hugging Face sentence-transformer model.
-   Store and retrieve research data with ChromaDB.
-   Use RAG with a Groq-hosted LLM to generate product comparisons and
    recommendations.
-   Support follow-up questions based on the collected research.
-   Web interface built with Flask, HTML, CSS, and JavaScript (project
    is under active development).

### Planned features

-   **YouTube review research:** Find relevant video reviews for a
    product, extract video transcripts where available, and analyze the
    review content.
-   **Review validation and cross-checking:** Compare claims across
    multiple independent sources and identify repeated, conflicting, or
    poorly supported claims.
-   **Evidence-based review summaries:** Distinguish reviewer opinions,
    personal experiences, specifications, and verifiable claims.
-   **Source transparency:** Show the source URL and supporting evidence
    for important statements.
-   **Review quality and confidence indicators:** Assess evidence
    strength based on source relevance, number of sources, consistency,
    recency, and whether the exact product model is confirmed.
-   **Improved product matching:** Reduce the risk of mixing reviews or
    specifications from different variants, generations, or similarly
    named products.
-   **More structured comparison and ranking:** Use transparent criteria
    that can be adjusted to the user's needs.
-   **Additional product categories and improved UI/UX.**

------------------------------------------------------------------------

## How it works

The current research pipeline follows this general flow:

1.  **Product search** -- Search for products matching the user's query.
2.  **Review search** -- Search the web for review-related information
    for the returned products.
3.  **Merge** -- Combine product information and retrieved review
    content.
4.  **Cleaning and filtering** -- Remove or filter unusable data.
5.  **Document preparation** -- Convert product research into LangChain
    documents.
6.  **Chunking** -- Split documents into smaller chunks for retrieval
    and processing.
7.  **Embeddings** -- Convert chunks into vector representations.
8.  **Vector storage** -- Store the chunks in ChromaDB.
9.  **Recommendation generation** -- Use the collected product evidence
    with the LLM to generate an initial comparison and recommendations.
10. **Follow-up questions** -- Retrieve relevant chunks from the vector
    store and answer follow-up questions using the research context.

``` mermaid
flowchart TD
    A[User shopping query] --> B[Product search]
    B --> C[Search review information]
    C --> D[Merge product and review data]
    D --> E[Clean and filter]
    E --> F[Prepare documents]
    F --> G[Chunk documents]
    G --> H[Generate embeddings]
    H --> I[ChromaDB vector store]
    I --> J[LLM comparison and recommendations]
    I --> K[Semantic retrieval for follow-up questions]
    K --> L[LLM answer]
```

------------------------------------------------------------------------

## Planned YouTube review and validation workflow

The planned review-analysis system aims to make recommendations more
evidence-based. The intended workflow is:

1.  Search YouTube for videos reviewing the exact product model.
2.  Collect relevant metadata such as video title, channel, publication
    date, and URL.
3.  Obtain transcripts when available and permitted through the chosen
    method.
4.  Match the transcript to the correct product model and variant.
5.  Extract review claims, including advantages, drawbacks, performance
    observations, and reported issues.
6.  Compare extracted claims with other video reviews, web sources, and
    product information.
7.  Identify:
    -   claims supported by multiple sources,
    -   claims reported by only one source,
    -   conflicting opinions,
    -   claims that cannot be verified,
    -   potentially outdated information.
8.  Store source references and evidence alongside extracted claims.
9.  Use the validated evidence in the RAG pipeline to generate a summary
    and recommendation.

### Important: validity is not the same as certainty

The system will not treat a claim as true simply because an LLM
extracted it or because several videos repeat it. Repeated claims may
originate from the same source, sponsored content, copied information,
or incorrect testing.

The planned system should: - verify that sources discuss the **same
model and variant**; - preserve the source and evidence for each
claim; - distinguish measured results from subjective opinions; - look
for independent corroboration; - flag contradictions rather than
silently resolving them; - label unsupported claims as **unverified**; -
avoid presenting review analysis as a guarantee of product quality.

------------------------------------------------------------------------

## Tech Stack

  Component               Technology
  ----------------------- --------------------------------------
  Language                Python
  Product search          SerpAPI
  Web/review research     Tavily
  LLM                     Groq (Llama model)
  Embeddings              Sentence Transformers / Hugging Face
  RAG framework           LangChain
  Vector database         ChromaDB
  Backend                 Flask
  Frontend                HTML, CSS, JavaScript
  Environment variables   python-dotenv

------------------------------------------------------------------------

## Project Structure

``` text
BuySmartAI/
├── analysis/                 # Analysis experiments and related work
├── core/
│   ├── chunking.py           # Document chunking
│   ├── creating_doc.py       # Document preparation
│   ├── embeddings.py          # Embedding-related logic
│   ├── generation.py         # LLM answer generation
│   ├── rag_pipeline.py       # Main RAG pipeline
│   └── vector_store.py       # ChromaDB operations
├── product/
│   └── product_search.py     # Product search
├── research/
│   └── tavily_search.py      # Review/web research
├── static/
│   ├── script.js             # Frontend JavaScript
│   └── style.css             # Styles
├── templates/
│   └── index.html            # Flask HTML template
├── vector_db/                # Local vector database (generated)
├── .env                      # API keys (not committed)
├── .gitignore
├── app.py                    # Flask application
├── main.py                   # Main/entry script
└── requirements.txt
```

------------------------------------------------------------------------

## Setup and Installation

### 1. Clone the repository

``` bash
git clone <your-repository-url>
cd BuySmartAI
```

### 2. Create a virtual environment

``` bash
python -m venv .venv
```

Activate it:

**macOS / Linux**

``` bash
source .venv/bin/activate
```

**Windows**

``` bash
.venv\Scripts\activate
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and add your API keys:

``` env
SERPAPI_API_KEY=your_serpapi_key
TAVILY_API_KEY=your_tavily_key
GROQ_API_KEY=your_groq_key
```

Keep API keys private. Do not commit your `.env` file or expose keys in
screenshots, logs, or public repositories.

### 5. Run the application

Depending on the entry point currently being used:

``` bash
python app.py
```

or

``` bash
python main.py
```

Follow the terminal output to access the local application.

------------------------------------------------------------------------

## Example Queries

-   Compare smartphones in the ₹25,000--₹35,000 price range,
    prioritizing battery life, camera quality, performance, and
    reliability.
-   Find Smart TVs in the ₹30,000--₹50,000 range for movies and sports,
    comparing picture quality, HDR, sound, refresh rate, and value.
-   Research common problems reported by owners of a specific laptop
    model and separate recurring complaints from isolated reports.
-   Compare two products and explain which is better for my use case,
    with evidence and trade-offs.

------------------------------------------------------------------------

## Responsible and Evidence-Based Recommendations

BuySmart AI is intended to assist with product research, not replace the
user's own decision.

Recommendations should: - use the collected research context; - disclose
when information is missing or insufficient; - avoid inventing
specifications, prices, reviews, or aggregate statistics; - distinguish
product specifications from reviewer experiences and opinions; - mention
relevant trade-offs and contradictory evidence; - avoid implying that
online reviews represent every owner's experience; - include source
references wherever the system supports them.

Search results and reviews may be incomplete, outdated, inaccurate,
promotional, or refer to a different product variant. Users should
verify important details---such as price, warranty, specifications, and
availability---before purchasing.

------------------------------------------------------------------------

## Limitations

-   Search results and review coverage depend on external services and
    their availability.
-   Some products may have little review information.
-   Search results can include incorrect product matches or variants.
-   The LLM may still make mistakes; generated answers should be checked
    against their sources.
-   YouTube transcript access and future review-validation capabilities
    are planned, not currently guaranteed.

------------------------------------------------------------------------

## Future Roadmap

-   [ ] YouTube video-review search and transcript collection
-   [ ] Product/model/variant matching for review sources
-   [ ] Claim extraction from reviews
-   [ ] Cross-source claim verification and contradiction detection
-   [ ] Evidence links and source attribution in generated answers
-   [ ] Review confidence / evidence-strength indicators
-   [ ] Improved recommendation scoring and ranking
-   [ ] More product categories
-   [ ] UI improvements and deployment

------------------------------------------------------------------------

## Contributing

This project is currently being developed and improved. Suggestions, bug
reports, and contributions are welcome.

------------------------------------------------------------------------

## Disclaimer

BuySmart AI is an experimental AI research assistant. It does not
guarantee the accuracy of product information, review analysis, or
recommendations. Always verify information with the manufacturer,
seller, and original review sources before making a purchase.

------------------------------------------------------------------------

## Author

Developed as a personal AI/ML project exploring web research,
Retrieval-Augmented Generation (RAG), embeddings, vector databases, and
evidence-based product comparison.
