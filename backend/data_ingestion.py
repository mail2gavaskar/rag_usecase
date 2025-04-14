import os
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredHTMLLoader,
    TextLoader
)
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import PGVector
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

class DocumentProcessor:
    def __init__(self):
        # Initialize Ollama embeddings
        self.embeddings = OllamaEmbeddings(
            model="llama3.2:3b",
            base_url="http://localhost:11434"
        )
        
        # Initialize PGVector connection
        self.vector_store = PGVector(
            connection_string=os.getenv('POSTGRES_CONNECTION_STRING'),
            embedding_function=self.embeddings,
            collection_name="bank_documents"
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    def load_document(self, file_path: str) -> List[Document]:
        """Load document based on file extension"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            loader = PyPDFLoader(file_path)
        elif file_extension == '.docx':
            loader = Docx2txtLoader(file_path)
        elif file_extension == '.html':
            loader = UnstructuredHTMLLoader(file_path)
        elif file_extension == '.txt':
            loader = TextLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
            
        return loader.load()

    def process_documents(self, directory_path: str) -> None:
        """Process all documents in a directory"""
        for filename in os.listdir(directory_path):
            if filename.startswith('.'):
                continue
                
            file_path = os.path.join(directory_path, filename)
            try:
                print(f"Processing {filename}...")
                documents = self.load_document(file_path)
                
                # Split documents into chunks
                chunks = self.text_splitter.split_documents(documents)
                
                # Add metadata
                for chunk in chunks:
                    chunk.metadata.update({
                        'source': filename,
                        'file_type': os.path.splitext(filename)[1].lower()
                    })
                
                # Store in vector database
                self.vector_store.add_documents(chunks)
                print(f"Successfully processed {filename}")
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

    def get_similar_documents(self, query: str, k: int = 5) -> List[Document]:
        """Retrieve similar documents for a query"""
        return self.vector_store.similarity_search(query, k=k)

if __name__ == "__main__":
    processor = DocumentProcessor()
    data_directory = "../data"  # Path to your documents
    processor.process_documents(data_directory) 