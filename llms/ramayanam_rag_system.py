#!/usr/bin/env python3
"""
Ramayanam RAG System
Advanced RAG implementation for Ramayanam Sanskrit texts with Ollama integration
"""

import os
import re
import json
import glob
import warnings
import requests
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging
from datetime import datetime

warnings.filterwarnings("ignore")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RamayanamSloka:
    """Structured representation of a Ramayanam sloka"""
    kanda: str  # e.g., "BalaKanda"
    sarga: int  # e.g., 1
    sloka_number: int  # e.g., 1
    sanskrit_text: str  # Original Sanskrit text
    word_meanings: str  # Word-by-word meanings
    translation: str  # English translation
    source_file: str  # Source file path
    devanagari_clean: str = ""  # Cleaned Devanagari text
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def get_full_reference(self) -> str:
        """Get full reference like 'BalaKanda.1.5'"""
        return f"{self.kanda}.{self.sarga}.{self.sloka_number}"
    
    def get_display_text(self) -> str:
        """Get formatted text for display"""
        return f"""Kanda: {self.kanda}
Sarga: {self.sarga}
Sloka: {self.sloka_number}

Sanskrit: {self.sanskrit_text}

Word Meanings: {self.word_meanings}

Translation: {self.translation}

Reference: {self.get_full_reference()}"""

class RamayanamCorpusLoader:
    """Load and process Ramayanam corpus from file system"""
    
    def __init__(self, data_path: str = "./data/slokas/Slokas"):
        self.data_path = Path(data_path)
        if not self.data_path.exists():
            logger.error(f"Data path not found: {data_path}")
            raise FileNotFoundError(f"Data path not found: {data_path}")
        
    def extract_sloka_info(self, file_path: Path) -> Tuple[str, int, str]:
        """Extract kanda, sarga, and file type from filename"""
        # Example: BalaKanda_sarga_1_sloka.txt
        filename = file_path.stem
        parts = filename.split('_')
        
        if len(parts) >= 4:
            kanda = parts[0]  # BalaKanda
            sarga = int(parts[2])  # 1
            file_type = parts[3]  # sloka, meaning, translation
            return kanda, sarga, file_type
        
        raise ValueError(f"Invalid filename format: {filename}")
    
    def parse_sanskrit_file(self, file_path: Path) -> Dict[int, str]:
        """Parse Sanskrit sloka file and extract individual slokas"""
        slokas = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Split by lines and process each sloka
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Parse format: "kanda::sarga::sloka_number::sanskrit_text"
                # Example: "1::1::1::तपस्स्वाध्यायनिरतं..."
                if '::' in line:
                    try:
                        # Split by :: and get parts
                        text_parts = line.split('::', 3)
                        if len(text_parts) >= 4:
                            # Third part (index 2) is the sloka number
                            sloka_num = int(text_parts[2])
                            # Fourth part is the Sanskrit text
                            sanskrit_text = text_parts[3].strip()
                            
                            # Remove verse markers like ।।1.1.1।। from the end
                            if '।।' in sanskrit_text:
                                # Take everything before the last verse marker
                                sanskrit_text = sanskrit_text.split('।।')[0].strip()
                            
                            if sanskrit_text:
                                slokas[sloka_num] = sanskrit_text
                                
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error parsing line in {file_path}: {line[:50]}... - {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
        
        return slokas
    
    def parse_meaning_file(self, file_path: Path) -> Dict[int, str]:
        """Parse meaning file"""
        meanings = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if '→' in line and '::' in line:
                    try:
                        parts = line.split('→', 1)
                        sloka_num = int(parts[0])
                        rest = parts[1]
                        
                        # Extract meaning text after reference numbers
                        text_parts = rest.split('::', 3)
                        if len(text_parts) >= 4:
                            meaning_text = text_parts[3].strip()
                            meanings[sloka_num] = meaning_text
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error parsing meaning line: {line[:50]}... - {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Error reading meaning file {file_path}: {e}")
        
        return meanings
    
    def parse_translation_file(self, file_path: Path) -> Dict[int, str]:
        """Parse translation file"""
        translations = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if '→' in line and '::' in line:
                    try:
                        parts = line.split('→', 1)
                        sloka_num = int(parts[0])
                        rest = parts[1]
                        
                        # Extract translation text
                        text_parts = rest.split('::', 3)
                        if len(text_parts) >= 4:
                            translation_text = text_parts[3].strip()
                            translations[sloka_num] = translation_text
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error parsing translation line: {line[:50]}... - {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Error reading translation file {file_path}: {e}")
        
        return translations
    
    def clean_sanskrit_text(self, text: str) -> str:
        """Clean Sanskrit text by removing numbers and extra punctuation"""
        # Remove reference numbers at the beginning
        text = re.sub(r'^\d+::\d+::\d+::', '', text)
        # Remove extra punctuation at the end
        text = re.sub(r'।+$', '।', text)
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def load_kanda(self, kanda_name: str) -> List[RamayanamSloka]:
        """Load all slokas from a specific kanda"""
        kanda_path = self.data_path / kanda_name
        if not kanda_path.exists():
            logger.warning(f"Kanda path not found: {kanda_path}")
            return []
        
        # Group files by sarga
        sarga_files = {}
        
        for file_path in kanda_path.glob("*.txt"):
            try:
                kanda, sarga, file_type = self.extract_sloka_info(file_path)
                
                if sarga not in sarga_files:
                    sarga_files[sarga] = {}
                
                sarga_files[sarga][file_type] = file_path
                
            except ValueError as e:
                logger.warning(f"Skipping file {file_path}: {e}")
                continue
        
        # Process each sarga
        all_slokas = []
        
        for sarga, files in sorted(sarga_files.items()):
            logger.info(f"Processing {kanda_name} Sarga {sarga}")
            
            # Load each file type
            sanskrit_slokas = {}
            meanings = {}
            translations = {}
            
            if 'sloka' in files:
                sanskrit_slokas = self.parse_sanskrit_file(files['sloka'])
            
            if 'meaning' in files:
                meanings = self.parse_meaning_file(files['meaning'])
            
            if 'translation' in files:
                translations = self.parse_translation_file(files['translation'])
            
            # Combine into RamayanamSloka objects
            all_sloka_numbers = set(sanskrit_slokas.keys()) | set(meanings.keys()) | set(translations.keys())
            
            for sloka_num in sorted(all_sloka_numbers):
                sanskrit_text = sanskrit_slokas.get(sloka_num, "")
                meaning_text = meanings.get(sloka_num, "")
                translation_text = translations.get(sloka_num, "")
                
                if sanskrit_text or meaning_text or translation_text:
                    sloka = RamayanamSloka(
                        kanda=kanda_name,
                        sarga=sarga,
                        sloka_number=sloka_num,
                        sanskrit_text=sanskrit_text,
                        word_meanings=meaning_text,
                        translation=translation_text,
                        source_file=str(files.get('sloka', '')),
                        devanagari_clean=self.clean_sanskrit_text(sanskrit_text)
                    )
                    all_slokas.append(sloka)
        
        logger.info(f"Loaded {len(all_slokas)} slokas from {kanda_name}")
        return all_slokas
    
    def load_all_kandas(self) -> List[RamayanamSloka]:
        """Load all available kandas"""
        all_slokas = []
        
        # Get all kanda directories
        kandas = [d.name for d in self.data_path.iterdir() if d.is_dir()]
        kandas.sort()  # Ensure consistent order
        
        logger.info(f"Found kandas: {kandas}")
        
        for kanda in kandas:
            kanda_slokas = self.load_kanda(kanda)
            all_slokas.extend(kanda_slokas)
        
        logger.info(f"Total slokas loaded: {len(all_slokas)}")
        return all_slokas

class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, base_url: str = "http://192.168.68.73:11434"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except Exception as e:
            logger.error(f"Error listing models: {e}")
        return []
    
    def generate(self, model: str, prompt: str, **kwargs) -> str:
        """Generate text using Ollama"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                **kwargs
            }
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', '')
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error generating with Ollama: {e}")
        
        return ""
    
    def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat with Ollama using messages format"""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                **kwargs
            }
            
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('message', {}).get('content', '')
            else:
                logger.error(f"Ollama chat API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error chatting with Ollama: {e}")
        
        return ""

class RamayanamEmbeddingModel:
    """Embedding model for Ramayanam texts"""
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"✓ Loaded embedding model: {model_name} ({self.dimension} dims)")
        except ImportError:
            logger.error("sentence-transformers not available. Install with: pip install sentence-transformers")
            self.model = None
            self.dimension = 384  # Default dimension
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts to embeddings"""
        if self.model is None:
            # Return random embeddings as fallback
            return np.random.random((len(texts), self.dimension))
        
        return self.model.encode(texts, normalize_embeddings=True)
    
    def get_dimension(self) -> int:
        return self.dimension

class RamayanamRAGSystem:
    """Complete RAG system for Ramayanam"""
    
    def __init__(self, 
                 data_path: str = "./data/slokas/Slokas",
                 db_path: str = "./ramayanam_chroma_db",
                 ollama_url: str = "http://192.168.68.73:11434"):
        
        # Initialize components
        self.loader = RamayanamCorpusLoader(data_path)
        self.embedding_model = RamayanamEmbeddingModel()
        self.ollama = OllamaClient(ollama_url)
        
        # Initialize vector database
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=db_path)
            self.collection = self.client.get_or_create_collection(
                name="ramayanam_slokas",
                metadata={"description": "Ramayanam Sanskrit slokas with meanings and translations"}
            )
            logger.info("✓ ChromaDB initialized")
        except ImportError:
            logger.error("ChromaDB not available. Install with: pip install chromadb")
            self.collection = None
        
        self.slokas = []
        self.default_model = "llama3.2:3b"  # Default Ollama model
        
    def load_corpus(self, kandas: Optional[List[str]] = None):
        """Load Ramayanam corpus"""
        if kandas:
            # Load specific kandas
            self.slokas = []
            for kanda in kandas:
                kanda_slokas = self.loader.load_kanda(kanda)
                self.slokas.extend(kanda_slokas)
        else:
            # Load all kandas
            self.slokas = self.loader.load_all_kandas()
        
        logger.info(f"Loaded {len(self.slokas)} total slokas")
    
    def index_corpus(self):
        """Index the loaded corpus in vector database"""
        if not self.slokas:
            logger.error("No slokas loaded. Call load_corpus() first.")
            return
        
        if self.collection is None:
            logger.error("Vector database not available")
            return
        
        logger.info(f"Indexing {len(self.slokas)} slokas...")
        
        # Prepare texts for embedding
        texts_for_embedding = []
        metadata = []
        ids = []
        
        for i, sloka in enumerate(self.slokas):
            # Combine Sanskrit, meaning, and translation for better search
            combined_text = f"{sloka.sanskrit_text} {sloka.word_meanings} {sloka.translation}"
            texts_for_embedding.append(combined_text)
            
            # Prepare metadata
            metadata.append({
                "kanda": sloka.kanda,
                "sarga": sloka.sarga,
                "sloka_number": sloka.sloka_number,
                "reference": sloka.get_full_reference(),
                "sanskrit": sloka.sanskrit_text,
                "meanings": sloka.word_meanings,
                "translation": sloka.translation,
                "source": sloka.source_file
            })
            
            ids.append(f"sloka_{i}")
        
        # Generate embeddings in batches
        batch_size = 100
        for i in range(0, len(texts_for_embedding), batch_size):
            batch_texts = texts_for_embedding[i:i+batch_size]
            batch_metadata = metadata[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(texts_for_embedding) + batch_size - 1)//batch_size}")
            
            embeddings = self.embedding_model.encode(batch_texts)
            
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=batch_texts,
                metadatas=batch_metadata,
                ids=batch_ids
            )
        
        logger.info("✓ Corpus indexed successfully")
    
    def search(self, query: str, top_k: int = 5) -> List[RamayanamSloka]:
        """Search for relevant slokas"""
        if self.collection is None:
            logger.error("Vector database not available")
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Search vector database
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=['metadatas', 'distances']
        )
        
        # Convert results back to RamayanamSloka objects
        search_results = []
        for metadata, distance in zip(results['metadatas'][0], results['distances'][0]):
            sloka = RamayanamSloka(
                kanda=metadata['kanda'],
                sarga=metadata['sarga'],
                sloka_number=metadata['sloka_number'],
                sanskrit_text=metadata['sanskrit'],
                word_meanings=metadata['meanings'],
                translation=metadata['translation'],
                source_file=metadata['source']
            )
            search_results.append(sloka)
        
        return search_results
    
    def get_context(self, query: str, top_k: int = 5) -> str:
        """Get formatted context for LLM generation"""
        results = self.search(query, top_k)
        
        context_parts = []
        for i, sloka in enumerate(results, 1):
            context_parts.append(f"""Reference {i} ({sloka.get_full_reference()}):
Sanskrit: {sloka.sanskrit_text}
Word Meanings: {sloka.word_meanings}
Translation: {sloka.translation}
""")
        
        return "\n".join(context_parts)
    
    def generate_response(self, query: str, model: Optional[str] = None, top_k: int = 5) -> str:
        """Generate response using RAG with Ollama"""
        if not self.ollama.is_available():
            return "Error: Ollama is not available. Please ensure Ollama is running."
        
        model = model or self.default_model
        
        # Check if model is available
        available_models = self.ollama.list_models()
        if not available_models:
            return "Error: No models available in Ollama."
        
        if model not in available_models:
            # Use first available model
            model = available_models[0]
            logger.info(f"Model {self.default_model} not found, using {model}")
        
        # Get relevant context
        context = self.get_context(query, top_k)
        
        # Create prompt
        prompt = f"""You are an expert on the Ramayanam, the ancient Sanskrit epic. Use the following context from the Ramayanam to answer the user's question. If the context doesn't contain relevant information, say so clearly.

Context from Ramayanam:
{context}

User Question: {query}

Please provide a comprehensive answer based on the context above. Include relevant Sanskrit verses when appropriate, and explain their meanings clearly."""
        
        # Generate response
        response = self.ollama.generate(model, prompt)
        
        if not response:
            return "Error: Failed to generate response from Ollama."
        
        return response
    
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        """Chat interface with context from Ramayanam"""
        if not self.ollama.is_available():
            return "Error: Ollama is not available."
        
        model = model or self.default_model
        
        # Get the last user message for context retrieval
        last_user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "")
                break
        
        if last_user_message:
            # Get relevant context
            context = self.get_context(last_user_message, top_k=3)
            
            # Add system message with context
            system_message = {
                "role": "system",
                "content": f"""You are an expert on the Ramayanam. Use this context when relevant:

{context}

Provide helpful and accurate information about the Ramayanam, Sanskrit culture, and Hindu philosophy."""
            }
            
            chat_messages = [system_message] + messages
        else:
            chat_messages = messages
        
        return self.ollama.chat(model, chat_messages)
    
    def interactive_chat(self):
        """Interactive chat interface"""
        print("🕉️  Ramayanam RAG Chat System")
        print("=" * 50)
        print("Ask questions about the Ramayanam! Type 'quit' to exit.")
        print(f"Using model: {self.default_model}")
        print("=" * 50)
        
        if not self.ollama.is_available():
            print("❌ Ollama is not available. Please start Ollama and try again.")
            return
        
        available_models = self.ollama.list_models()
        print(f"Available models: {', '.join(available_models)}")
        print()
        
        messages = []
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("🙏 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                messages.append({"role": "user", "content": user_input})
                
                print("\n🤖 Assistant: ", end="", flush=True)
                response = self.chat(messages)
                print(response)
                
                messages.append({"role": "assistant", "content": response})
                
                # Keep only last 10 messages to avoid context overflow
                if len(messages) > 10:
                    messages = messages[-10:]
                    
            except KeyboardInterrupt:
                print("\n\n🙏 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

def main():
    """Main function to demonstrate the Ramayanam RAG system"""
    print("🕉️  Ramayanam RAG System")
    print("=" * 50)
    
    # Initialize system
    rag_system = RamayanamRAGSystem()
    
    # Load and index corpus
    print("📚 Loading Ramayanam corpus...")
    rag_system.load_corpus()
    
    print("🔍 Indexing corpus...")
    rag_system.index_corpus()
    
    print("✅ System ready!")
    
    # Test queries
    test_queries = [
        "Who is Rama and what are his qualities?",
        "Tell me about Sita",
        "What happened when Rama went to the forest?",
        "Who is Hanuman and what did he do?",
        "What is the story of Rama and Ravana?"
    ]
    
    print("\n🧪 Testing with sample queries:")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print("-" * 40)
        
        response = rag_system.generate_response(query, top_k=3)
        print(f"🤖 Response: {response}")
        print("\n" + "="*80)
    
    # Start interactive chat
    print("\n🚀 Starting interactive chat...")
    rag_system.interactive_chat()

if __name__ == "__main__":
    main()