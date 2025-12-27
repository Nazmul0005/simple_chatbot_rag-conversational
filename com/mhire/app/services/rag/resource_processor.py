"""
Resource processing utilities (used by index_resources.py)
This file provides shared functionality but is not directly used in chat flow
"""
from pathlib import Path
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader


class ResourceProcessor:
    """Utility class for processing documents"""
    
    @staticmethod
    def get_text_splitter(chunk_size: int = 1000, chunk_overlap: int = 200):
        """Get text splitter for chunking documents"""
        return RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    
    @staticmethod
    def load_document(file_path: Path):
        """Load a document based on file type"""
        if file_path.suffix == '.pdf':
            loader = PyPDFLoader(str(file_path))
        elif file_path.suffix == '.txt':
            loader = TextLoader(str(file_path))
        elif file_path.suffix in ['.docx', '.doc']:
            loader = Docx2txtLoader(str(file_path))
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        return loader.load()
    
    @staticmethod
    def add_metadata(documents: List, resource_type: str, source: str):
        """Add metadata to documents"""
        for doc in documents:
            doc.metadata.update({
                'resource_type': resource_type,
                'source': source
            })
        return documents