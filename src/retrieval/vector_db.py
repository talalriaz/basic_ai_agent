import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from PyPDF2 import PdfReader
from langchain_openai import OpenAIEmbeddings
from src.utils.config import load_config


class VectorDBManager:
    def __init__(self):
        cfg = load_config()["retrieval"]
        self.data_path = cfg['data_path']
        self.chunk_size = cfg['chunk_size']
        self.chunk_overlap = cfg['chunk_overlap']
        self.vector_store_path = cfg['vector_store_path']
        self.embedding_model_name = cfg['embedding_model_name']
        self.embedding_model = OpenAIEmbeddings(model=self.embedding_model_name)

    def load_documents(self,pdf_docs):
        """
        Load text from the specified documents using PdfReader.

        Returns:
            text: string of text extracted from the given pdf files.
        """
        text = ""
        for pdf_path in pdf_docs:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"File {pdf_path} not found")
            pdf_reader = PdfReader(pdf_path)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def split_text(self,text: str):
        """
        Split the text content of the given list of Document objects into smaller chunks.

        Args:
            text (str): text content to split.

        Returns:
            chunks: representing the split text chunks.
        """
        # Initialize text splitter with specified parameters
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            add_start_index=True,
        )
        chunks = text_splitter.split_text(text)
        print(f"Split documents into {len(chunks)} chunks.")
        return chunks  


    def save_embeddings(self,text_chunks: list[str]):
        """
        Save the given list of Document objects to a FAISS database.

        Args:
            text_chunks (list[str]): List of text chunks to save.

        Returns:
            None
        """

        db = FAISS.from_texts(
            text_chunks, self.embedding_model, distance_strategy=DistanceStrategy.COSINE
        )
        db.save_local(self.vector_store_path)
        print(f"Saved {len(text_chunks)} chunks to {self.vector_store_path}.")

    def ingest_documents(self):
        """
        Ingest the list of document file paths into the vector database.

        Args:
            None

        Returns:
            None
        """
        pdf_docs = [os.path.join(self.data_path,doc) for doc in os.listdir(self.data_path) if doc.endswith('.pdf')]
        text = self.load_documents(pdf_docs)
        text_chunks = self.split_text(text)
        self.save_embeddings(text_chunks)
        print("Ingestion complete.")


    def load_db(self):
        try:
            db = FAISS.load_local(self.vector_store_path, self.embedding_model, allow_dangerous_deserialization= True)
        except Exception as e:
            print(f"Error loading FAISS database: {str(e)}")
            return None
        return db

    def query_db(self,query_text,top_k=3):
        db = self.load_db()
        results = db.similarity_search_with_relevance_scores(query_text, k=top_k)

        if len(results) == 0 or results[0][1] < 0.25:
            print(f"Unable to find matching results.")

        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        return context_text

if __name__ == "__main__":
    vector_db_manager = VectorDBManager()
    vector_db_manager.ingest_documents()
