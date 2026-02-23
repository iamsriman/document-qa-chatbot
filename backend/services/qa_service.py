from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

class QAService:
    def __init__(self):
        # Configure new Gemini client
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        
    def answer_question(self, vector_store, question: str) -> str:
        """Answer question using RAG"""
        
        try:
            # Retrieve relevant documents
            retriever = vector_store.as_retriever(search_kwargs={"k": 3})
            docs = retriever.invoke(question)
            
            # Combine context from retrieved documents
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Create prompt
            prompt = f"""Use the following pieces of context to answer the question at the end. 
            If you don't know the answer, just say that you don't know, don't try to make up an answer.
            
            Context: {context}
            
            Question: {question}
            
            Answer:"""
            
            # Use gemini-2.5-flash (latest available model from your list)
            response = self.client.models.generate_content(
                model='models/gemini-2.5-flash',
                contents=prompt
            )
            
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error in answer_question: {error_msg}")
            return f"I'm sorry, I encountered an error: {error_msg}"