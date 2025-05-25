# 🤖 Advanced RAG PDF Query System

An intelligent document analysis system that uses **Retrieval-Augmented Generation (RAG)** with **Groq API** for fast and accurate PDF document querying. This system prevents hallucinations by grounding responses strictly in the uploaded document content.

## 🌟 Features

- **PDF Document Processing**: Upload and extract text from PDF files
- **Intelligent Chunking**: Smart text segmentation for optimal retrieval
- **Vector Embeddings**: Uses HuggingFace sentence transformers for semantic search
- **FAISS Vector Store**: Fast similarity search and retrieval
- **Groq API Integration**: Lightning-fast inference with Llama3-8B model
- **Hallucination Prevention**: Responses grounded strictly in document content
- **Web Interface**: Clean, modern UI for easy interaction
- **Real-time Processing**: Fast document processing and query responses

## 🏗️ Project Structure

```
inferaread-RAG-pdf-groq/
│
├── app/                      # Main backend logic
│   └── model.ipynb          # Complete RAG implementation
│
├── data/
│   ├── uploads/             # Uploaded PDFs
│   ├── processed/           # Chunked/cleaned data
│   └── index/               # Vector DB index (FAISS files)
│
├── requirements.txt         # Python dependencies
├── .env                     # API keys and configuration
├── README.md               # This file
└── run.py                  # Development runner
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd inferaread-RAG-pdf-groq
```

### 2. Get Groq API Key

1. Visit [Groq Console](https://console.groq.com/keys)
2. Sign up/Login and create an API key
3. Copy your API key

### 3. Configure Environment

Update the `.env` file with your Groq API key:

```env
GROQ_API_KEY=your_actual_groq_api_key_here
```

### 4. Run the Application

```bash
python run.py
```

Choose option 1 (Jupyter Notebook) and run all cells in `app/model.ipynb`.

## 🔧 Alternative Setup Methods

### Method 1: Jupyter Notebook (Recommended)

```bash
# Install Jupyter if not installed
pip install jupyter

# Start Jupyter
jupyter notebook app/

# Open model.ipynb and run all cells
```

### Method 2: Direct Python Execution

```bash
# Install requirements
pip install -r requirements.txt

# Run the notebook as Python (requires conversion)
cd app/
python -c "exec(open('model.ipynb').read())"
```

## 📱 Using the Application

### 1. Access the Web Interface

Once running, open your browser and go to:
```
http://localhost:8000
```

### 2. Upload PDF Document

1. Click "Choose File" in the upload section
2. Select your PDF document
3. Click "Upload & Process PDF"
4. Wait for processing to complete

### 3. Ask Questions

1. Enter your question in the query box
2. Click "Ask Question"
3. Get AI-powered answers based on your document

## 🤖 Model Information

- **LLM**: Llama3-8B-8192 (via Groq API)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **Text Splitter**: LangChain RecursiveCharacterTextSplitter
- **Chunk Size**: 500 characters with 50 character overlap

## 🛡️ Hallucination Prevention

The system implements several techniques to prevent hallucinations:

1. **Strict Context Grounding**: Responses are based only on retrieved document chunks
2. **Low Temperature**: Temperature set to 0.1 for more deterministic outputs
3. **Explicit Instructions**: Clear prompts instructing the model to stay within context
4. **Source Validation**: Shows number of sources used for each answer
5. **Fallback Responses**: Clear messaging when information isn't found in the document

## 🔍 Technical Details

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

## 📦 Dependencies

### Core Libraries

- **FastAPI**: Web framework for API
- **LangChain**: RAG pipeline and document processing
- **FAISS**: Vector similarity search
- **HuggingFace Transformers**: Embedding models
- **PyMuPDF**: PDF text extraction
- **OpenAI**: Groq API client

### Full Requirements

See `requirements.txt` for complete dependency list.

## 🌐 API Endpoints

- `GET /`: Main web interface
- `POST /upload`: Upload and process PDF
- `POST /query`: Query the processed document
- `GET /health`: System health check

## 🛠️ Configuration Options

Customize the system by modifying these parameters in the code:

```python
CHUNK_SIZE = 500          # Text chunk size
CHUNK_OVERLAP = 50        # Overlap between chunks
MAX_RETRIEVED_CHUNKS = 5  # Number of chunks to retrieve
MODEL_NAME = "llama3-8b-8192"  # Groq model to use
```

## 🧪 Testing

### Test with Sample Questions

Try these questions with your uploaded PDF:

- "What is the main topic of this document?"
- "Can you summarize the key points?"
- "What are the conclusions mentioned?"
- "Are there any recommendations provided?"

### Error Handling

The system handles common errors:

- Invalid PDF files
- Empty or corrupted documents
- API connectivity issues
- Missing environment variables

## 🚨 Troubleshooting

### Common Issues

1. **"GROQ_API_KEY not found"**
   - Check your `.env` file
   - Ensure the API key is correct

2. **"No text found in PDF"**
   - PDF might be image-based (scanned)
   - Try OCR preprocessing

3. **"Module not found"**
   - Run `pip install -r requirements.txt`

4. **Port already in use**
   - Change port in the code or kill existing processes

### Performance Optimization

- Use GPU if available for embedding models
- Adjust chunk size based on document type
- Fine-tune retrieval parameters
- Cache embeddings for repeated queries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Groq** for providing fast LLM inference
- **LangChain** for RAG framework
- **HuggingFace** for embedding models
- **Facebook AI** for FAISS vector search

## 📞 Support

For issues and questions:

1. Check the troubleshooting section
2. Review the error messages
3. Create an issue on GitHub
4. Contact the development team

---

**Built with ❤️ using Groq API and modern RAG techniques**