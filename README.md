<p align="center">
  <img src="./AILogo.png" alt="Inferaread" width="200">
</p>

<h1 align="center">InferaRead - RAG PDF Query System</h1>

<p align="center">
    INFERAREAD is an advanced RAG PDF Query System powered by Groq API & LLaMA3/Gemma-7b-It
    <br />
    <strong>Explore the docs »</strong>
    <br />
    <br />
    <a href="https://github.com/akshatrajsaxena/Inferaread-LLMBot/issues">Report Bug</a>
    ·
    <a href="https://github.com/akshatrajsaxena/Inferaread-LLMBot/issues">Request Feature</a>
    <br />
</p>

An intelligent document analysis system that uses **Retrieval-Augmented Generation (RAG)** with **Groq API** for fast and accurate PDF document querying. This system prevents hallucinations by grounding responses strictly in the uploaded document content. Any user query which is out of context is flagged as unmarked and a predefined message appears stating that the query is not within the document.

## Working
- Uploading the Document:
  The file is saved temporarily ```(e.g., /tmp/input.pdf)```.
- Extracting Text from Document:
  For this purpose i used tools PyMuPDF. The PDF is parsed page-by-page. Text is extracted from each page while preserving layout and paragraph structure as much as possible.
```
import fitz
doc = fitz.open("input.pdf")
text = "\n\n".join([page.get_text() for page in doc])
```
- Preprocessing the Text: 
  This includes:
  - Remove extra whitespace and non-printable characters.
  - Optionally fix hyphenation and merge broken lines.
  - Normalize text (lowercasing, unicode normalization if needed).
  
- Chunking the Text into Passages:
  As the LLMs and embedding models have context length limits (e.g., 512 or 1024 tokens), this was the neccesary step. This is done using a sliding window approach to chunk text (e.g., 200-token chunks with 50-token overlap). We can also chunk by paragraphs or sentences if semantic coherence is important.
```
from langchain.text_splitter import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_text(text)
```
- Storing Embeddings and Metadata: This was done using the tools FAISS for fast similarity search.It Store mapping of chunk → original page or section. Save in a dictionary.
```
import faiss
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)
```
- Handling a User Query: When user submits a natural language question. The query is embedded using the same SentenceTransformer model used earlier. A FAISS nearest-neighbor search retrieves top-K most similar chunks based on cosine similarity or L2 distance.
```
query_embedding = model.encode([query])
D, I = index.search(query_embedding, top_k)
relevant_chunks = [chunks[i] for i in I[0]]
```
## Project Structure

```
InferaRead-rag-pdf-groq
├─ .env
├─ app
│  ├─ data
│  │  ├─ index
│  │  │  └─ faiss_index
│  │  │     ├─ index.faiss
│  │  │     └─ index.pkl
│  └─ model.ipynb
├─ frontend
│  ├─ app.py
│  ├─ config.py
│  ├─ requirements.txt
│  ├─ utils.py
```

##  Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/akshatrajsaxena/Inferaread-LLMBot
```

### 2. Get Groq API Key

1. Visit [Groq Console](https://console.groq.com/keys)
2. Sign up/Login and create an API key
3. Copy your API key

### 3. Configure Environment

Update the `.env` file with your Groq API key:

```env
GROQ_API_KEY=[Your GROQ API key Here]
```
### 4. Create your python environment and Install all Dependencies
```bash
python -m venv project
project\Scripts\activate
```
then install all the dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python run.py
```

## Project Status

**The project is constantly fine-tuning and updating, so it might contain bugs or incomplete features. Contributions and feedback are welcome!**

### Testing on my Cover Letter
![image](https://github.com/user-attachments/assets/b6d794d8-2489-4f87-b807-c64a3f2d8602)



## Using the Application

### 1. Access the Web Interface

Once running, open your browser and go to:
```
http://localhost:8000
```

### 2. Upload PDF Document and Ask Queries

1. Click "Choose File" in the upload section
2. Click "Upload & Process PDF"
3. Wait for processing to complete

## Model Information

- **LLM**: Llama3-8B-8192 (via Groq API)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **Text Splitter**: LangChain RecursiveCharacterTextSplitter
- **Chunk Size**: 500 characters with 50 character overlap

## Hallucination Prevention
The system implements several techniques to prevent hallucinations:

1. **Strict Context Grounding**: Responses are based only on retrieved document chunks.
2. **Low Temperature**: Temperature set to 0.1 for more deterministic outputs and negligible randomness.
3. **Explicit Instructions**: Clear prompts instructing the model to stay within context.
4. **Source Validation**: Shows number of sources used for each answer.
5. **Fallback Responses**: Clear messaging when information isn't found in the document


### PDF Processing Pipeline

1. **Text Extraction**: PyMuPDF extracts text from PDF pages
2. **Preprocessing**: Cleans and normalizes extracted text
3. **Chunking**: Splits text into overlapping chunks for better context
4. **Embedding**: Converts chunks to vector embeddings
5. **Indexing**: Stores vectors in FAISS index for fast retrieval

### Query Processing Pipeline

1. **Query Embedding**: Converts user question to vector
2. **Similarity Search**: Finds most relevant document chunks
3. **Context Preparation**: Combines retrieved chunks
4. **LLM Generation**: Groq API generates grounded response
5. **Response Validation**: Ensures answer stays within context

##  Dependencies

### Core Libraries

- **FastAPI**: Web framework for API
- **LangChain**: RAG pipeline and document processing
- **FAISS**: Vector similarity search
- **HuggingFace Transformers**: Embedding models
- **PyMuPDF**: PDF text extraction
- **OpenAI**: Groq API client

## Configuration Options

Customize the system by modifying these parameters in the code:

```python
CHUNK_SIZE = 500          # Text chunk size
CHUNK_OVERLAP = 50        # Overlap between chunks
MAX_RETRIEVED_CHUNKS = 5  # Number of chunks to retrieve
MODEL_NAME = "llama3-8b-8192"  # Groq model to use
```


### Common Issues

1. **"GROQ_API_KEY not found"**
   - Check your `.env` file
   - Ensure the API key is correct

2. **"No text found in PDF"**
   - PDF might be image-based (scanned)

3. **"Module not found"**
   - Run `pip install -r requirements.txt`
  - Or refer for [python documentation](https://docs.python.org/3/installing/index.html) for installing a missing dependencied
4. **Port already in use**
   - Change port in the code or kill existing processes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

##  Acknowledgments

- **Groq** for providing fast LLM inference
- **LangChain** for RAG framework
- **HuggingFace** for embedding models
- **Facebook AI** for FAISS vector search
