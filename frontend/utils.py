import requests
import streamlit as st
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from config import Config

def backendActivity() -> Dict[str, Any]:
    try:
        response = requests.get(f"{Config.BACKEND_URL}/api/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": f"HTTP {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": "Connection refused - Backend not running"}
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "Request timeout"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def formatResult(response_text: str, max_length: int = 1000) -> str:
    if len(response_text) <= max_length:
        return response_text
    truncated = response_text[:max_length]
    last_sentence = truncated.rfind('.')    
    if last_sentence > max_length * 0.8:  # If we can find a sentence end. This is done to avoid cutting off mid-sentence
        return truncated[:last_sentence + 1] + "\n\n... [Response truncated]"
    else:
        return truncated + "... [Response truncated]"

def chatBubble(message: str, is_user: bool = True, timestamp: str = None) -> str:
    if timestamp is None:
        timestamp = datetime.now().strftime('%H:%M:%S')
    if is_user:
        return f"""
        <div style="
            background-color: #007bff;
            color: white;
            padding: 0.8rem;
            border-radius: 15px 15px 5px 15px;
            margin: 0.5rem 0;
            margin-left: 20%;
            text-align: right;
        ">
            <strong>You:</strong> {message}
            <br><small style="opacity: 0.8;">{timestamp}</small>
        </div>
        """
    else:
        return f"""
        <div style="
            background-color: #e9ecef;
            color: #495057;
            padding: 0.8rem;
            border-radius: 15px 15px 15px 5px;
            margin: 0.5rem 0;
            margin-right: 20%;
        ">
            <strong>InferaRead:</strong> {message}
            <br><small style="opacity: 0.6;">{timestamp}</small>
        </div>
        """
        # the above if else is used to create a chat bubble for the user and the bot, with different styles and alignments. If the message is from the user, it will be aligned to the right with a blue background, and if it is from the bot, it will be aligned to the left with a light gray background.

def fileUpload(uploaded_file) -> Dict[str, Any]:
    if uploaded_file is None:
        return {"valid": False, "error": "No file uploaded"}
    if not uploaded_file.name.lower().endswith('.pdf'):
        return {"valid": False, "error": "Only PDF files are supported"}
    fileSize = len(uploaded_file.getvalue()) / (1024 * 1024)
    if fileSize > Config.MAX_FILE_SIZE_MB:
        return {"valid": False, "error": f"File size ({fileSize:.1f}MB) exceeds limit ({Config.MAX_FILE_SIZE_MB}MB)"}
    return {"valid": True, "size_mb": fileSize}

def systemStatus() -> Dict[str, Any]:
  
    try:
        health_response = requests.get(f"{Config.BACKEND_URL}/api/health", timeout=5)
        status_response = requests.get(f"{Config.BACKEND_URL}/api/status", timeout=5)
        if health_response.status_code == 200 and status_response.status_code == 200:
            health_data = health_response.json()
            status_data = status_response.json()
            
            return {"healthy": True,"backend_status": health_data.get("status", "unknown"),"document_loaded": status_data.get("document_loaded", False),"current_document": status_data.get("current_document"),"model": status_data.get("model", "Unknown"),"embedding_model": status_data.get("embedding_model", "Unknown")}
        else:
            return {"healthy": False, "error": "API endpoints not responding correctly"}
            
    except Exception as e:
        return {"healthy": False, "error": str(e)}

def preprocessQuery(query: str) -> str:
    query = ' '.join(query.split())
    max_length = 1000
    if len(query) > max_length:
        query = query[:max_length]
    query = query.replace('<script>', '').replace('</script>', '')
    query = query.replace('<', '&lt;').replace('>', '&gt;')
    
    return query.strip()

def fileFormat(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.1f} GB"

def chatDownload(chat_history: List[Dict], metadata: Dict = None) -> str:
    export_data = {
        "export_info": {"timestamp": datetime.now().isoformat(),"total_queries": len(chat_history),"app_version": "1.0.0"
        },
        "metadata": metadata or {},"chat_history": chat_history
    }
    
    return json.dumps(export_data, indent=2, ensure_ascii=False)

def queryStats(chat_history: List[Dict]) -> Dict[str, Any]:
    if not chat_history:
        return {"total_queries": 0,"avg_query_length": 0,"avg_response_length": 0,"most_common_words": [],"query_frequency": {}}
    
    total_queries = len(chat_history)
    query_lengths = [len(entry.get('query', '').split()) for entry in chat_history]
    response_lengths = [len(entry.get('response', '').split()) for entry in chat_history]
    avg_query_length = sum(query_lengths) / len(query_lengths) if query_lengths else 0
    avg_response_length = sum(response_lengths) / len(response_lengths) if response_lengths else 0
    
    all_words = []
    for entry in chat_history:
        query = entry.get('query', '').lower()
        words = [word.strip('.,!?;:"()[]') for word in query.split()]
        all_words.extend([word for word in words if len(word) > 3])    
    word_freq = {}
    for word in all_words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    most_common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {"total_queries": total_queries,"avg_query_length": round(avg_query_length, 1),"avg_response_length": round(avg_response_length, 1),"most_common_words": most_common_words,"query_lengths": query_lengths,"response_lengths": response_lengths}

def querySuggestion(current_query: str, chat_history: List[Dict]) -> List[str]:
    suggestions = []
    if len(current_query.strip()) < 3:
        return Config.DEFAULT_QUERY_EXAMPLES[:5]
    current_words = set(current_query.lower().split())
    
    for entry in chat_history:
        query = entry.get('query', '')
        query_words = set(query.lower().split())
        overlap = len(current_words.intersection(query_words))
        if overlap > 0 and query not in suggestions:
            suggestions.append(query)
    contextual_suggestions = []
    
    if any(word in current_query.lower() for word in ['what', 'how', 'why']):
        contextual_suggestions.extend([
            "What are the main conclusions?","How does this relate to previous findings?","Why is this approach significant?"
        ])
    
    if any(word in current_query.lower() for word in ['summary', 'summarize']):
        contextual_suggestions.extend([
            "Summarize the key points in bullet format","Provide a brief summary of the document","What are the main takeaways?"
        ])
    
    all_suggestions = suggestions + contextual_suggestions
    return list(dict.fromkeys(all_suggestions))[:5]  # Remove duplicates and limit

def error(error_type: str, details: str = "") -> str:
    error_messages = {
        "upload": "**Upload Error**\n\nThere was a problem uploading your document.",
        "query": "**Query Error**\n\nUnable to process your question.",
        "connection": "**Connection Error**\n\nCannot connect to the backend server.",
        "timeout": "**Timeout Error**\n\nThe request took too long to complete.",
        "file_size": "**File Size Error**\n\nThe uploaded file is too large.",
        "file_type": "**File Type Error**\n\nOnly PDF files are supported.",
        "server": "**Server Error**\n\nThe server encountered an internal error."
    }
    base_message = error_messages.get(error_type, "**Unknown Error**\n\nAn unexpected error occurred.")
    if details:
        return f"{base_message}\n\n**Details:** {details}"
    
    return base_message

def timestamp(timestamp: str = None) -> str:
    if timestamp is None:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = timestamp
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(timestamp)