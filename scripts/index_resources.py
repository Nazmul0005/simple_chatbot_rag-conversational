"""
Script to process resources and create FAISS vector index
Run this once initially and whenever new resources are added
"""

import os
import sys
from pathlib import Path
from typing import List
from google import genai
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader
)


# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from com.mhire.app.config.config import Config


class ResourceIndexer:
    def __init__(self):
        self.config = Config()
        genai.Client(api_key=self.config.GEMINI_API_KEY)
        
        # Initialize embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=self.config.GEMINI_API_KEY
        )
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Paths
        self.resources_dir = project_root / "com/mhire/app/data/resources"
        self.vector_db_path = project_root / "com/mhire/app/data/vector_db"
        
        # Create directories if they don't exist
        self.resources_dir.mkdir(parents=True, exist_ok=True)
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
    
    def load_document(self, file_path: Path):
        """Load a single document based on file type"""
        try:
            if file_path.suffix == '.pdf':
                loader = PyPDFLoader(str(file_path))
            elif file_path.suffix == '.txt':
                loader = TextLoader(str(file_path))
            elif file_path.suffix in ['.docx', '.doc']:
                loader = Docx2txtLoader(str(file_path))
            else:
                print(f"⚠️  Unsupported file type: {file_path}")
                return []
            
            documents = loader.load()
            
            # Add metadata
            for doc in documents:
                doc.metadata.update({
                    'source': file_path.name,
                    'resource_type': file_path.parent.name,  # e.g., 'mental_health'
                    'file_path': str(file_path)
                })
            
            return documents
        
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            return []
    
    def load_all_resources(self) -> List:
        """Load all documents from resources directory"""
        all_documents = []
        
        # Supported file extensions
        supported_extensions = ['.pdf', '.txt', '.docx', '.doc']
        
        print(f"\n📂 Scanning resources directory: {self.resources_dir}")
        
        # Walk through all subdirectories
        for root, dirs, files in os.walk(self.resources_dir):
            for file in files:
                file_path = Path(root) / file
                
                if file_path.suffix in supported_extensions:
                    print(f"📄 Loading: {file_path.relative_to(self.resources_dir)}")
                    docs = self.load_document(file_path)
                    all_documents.extend(docs)
        
        print(f"\n✅ Loaded {len(all_documents)} document(s)")
        return all_documents
    
    def create_vector_index(self, documents: List):
        """Create FAISS vector index from documents"""
        if not documents:
            print("⚠️  No documents to index!")
            return
        
        print(f"\n🔪 Splitting documents into chunks...")
        chunks = self.text_splitter.split_documents(documents)
        print(f"✅ Created {len(chunks)} chunks")
        
        print(f"\n🧠 Generating embeddings and creating FAISS index...")
        print("   (This may take a few minutes depending on content size)")
        
        try:
            # Create FAISS index
            vectorstore = FAISS.from_documents(
                documents=chunks,
                embedding=self.embeddings
            )
            
            # Save to disk
            faiss_index_path = self.vector_db_path / "faiss_index"
            vectorstore.save_local(str(faiss_index_path))
            
            print(f"\n✅ FAISS index created successfully!")
            print(f"📍 Saved to: {faiss_index_path}")
            print(f"📊 Total chunks indexed: {len(chunks)}")
            
            # Display resource breakdown
            self._display_index_stats(chunks)
            
        except Exception as e:
            print(f"\n❌ Error creating FAISS index: {e}")
            raise
    
    def _display_index_stats(self, chunks):
        """Display statistics about indexed resources"""
        resource_types = {}
        sources = set()
        
        for chunk in chunks:
            rtype = chunk.metadata.get('resource_type', 'unknown')
            source = chunk.metadata.get('source', 'unknown')
            
            resource_types[rtype] = resource_types.get(rtype, 0) + 1
            sources.add(source)
        
        print("\n" + "="*50)
        print("📊 INDEX STATISTICS")
        print("="*50)
        print(f"Total unique documents: {len(sources)}")
        print(f"Total chunks: {len(chunks)}")
        print("\nBreakdown by resource type:")
        for rtype, count in resource_types.items():
            print(f"  • {rtype}: {count} chunks")
        print("="*50)
    
    def run(self):
        """Main execution flow"""
        print("\n" + "="*50)
        print("🚀 RESOURCE INDEXING STARTED")
        print("="*50)
        
        # Load all documents
        documents = self.load_all_resources()
        
        if not documents:
            print("\n⚠️  No documents found in resources directory!")
            print(f"📁 Please add resources to: {self.resources_dir}")
            print("\nSupported formats: PDF, TXT, DOCX, DOC")
            print("\nExample structure:")
            print("  resources/")
            print("    ├── mental_health/")
            print("    │   └── coping_strategies.pdf")
            print("    ├── finance/")
            print("    │   └── budgeting_guide.docx")
            print("    └── legal/")
            print("        └── tenant_rights.txt")
            return
        
        # Create vector index
        self.create_vector_index(documents)
        
        print("\n✅ INDEXING COMPLETE!")
        print("\n💡 Next steps:")
        print("  1. Start your chatbot application")
        print("  2. The RAG system will use this index for retrievals")
        print("  3. Re-run this script whenever you add new resources")
        print("\n" + "="*50)


if __name__ == "__main__":
    try:
        indexer = ResourceIndexer()
        indexer.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Indexing interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)