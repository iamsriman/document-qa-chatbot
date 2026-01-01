from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

class QAService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.3
        )
        
    def answer_question(self, vector_store, question: str) -> str:
        """Answer question using RAG"""
        
        # Retrieve relevant documents using invoke instead of get_relevant_documents
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke(question)  # Changed from get_relevant_documents
        
        # Combine context from retrieved documents
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Create prompt
        prompt = f"""Use the following pieces of context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        Context: {context}
        
        Question: {question}
        
        Answer:"""
        
        # Get answer from LLM
        response = self.llm.invoke(prompt)
        
        # Extract text from response
        if hasattr(response, 'content'):
            return response.content
        else:
            return str(response)