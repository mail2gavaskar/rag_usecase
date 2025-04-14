import os
from typing import List, Dict, Tuple
from langchain_core.documents import Document
from langchain_community.chat_models import ChatOllama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import re
from dotenv import load_dotenv

load_dotenv()

class DocumentAnalyzer:
    def __init__(self):
        self.llm = ChatOllama(
            model="llama3.2:3b",
            base_url="http://localhost:11434",
            temperature=0.7
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Simple token counter (approximate)
        self.token_counter = lambda text: len(re.findall(r'\w+', text)) + len(re.findall(r'[^\w\s]', text))
        
        self.summary_prompt = PromptTemplate(
            input_variables=["documents"],
            template="""
            Please provide a comprehensive summary of the following documents, focusing on key points,
            important dates, and relevant financial information:
            
            {documents}
            
            Summary:
            """
        )
        
        self.recommendation_prompt = PromptTemplate(
            input_variables=["documents", "query", "chat_history"],
            template="""
            Based on the following documents and previous conversation context, provide specific recommendations
            for the given query. Focus on actionable insights and relevant data points:
            
            Documents:
            {documents}
            
            Query: {query}
            
            Previous Conversation:
            {chat_history}
            
            Recommendations:
            """
        )

    def count_tokens(self, text: str) -> int:
        """Count approximate tokens in a text string"""
        return self.token_counter(text)

    def generate_summary(self, documents: List[Document]) -> Tuple[str, Dict]:
        """Generate summary and return token counts"""
        chain = LLMChain(llm=self.llm, prompt=self.summary_prompt)
        doc_text = "\n\n".join([doc.page_content for doc in documents])
        
        # Count input tokens
        input_tokens = self.count_tokens(doc_text)
        
        # Generate summary
        summary = chain.run(documents=doc_text)
        
        # Count output tokens
        output_tokens = self.count_tokens(summary)
        
        return summary, {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens
        }

    def get_recommendations(self, documents: List[Document], query: str) -> Tuple[Dict, Dict]:
        """Get recommendations and return token counts"""
        chain = LLMChain(
            llm=self.llm,
            prompt=self.recommendation_prompt,
            memory=self.memory
        )
        
        doc_text = "\n\n".join([doc.page_content for doc in documents])
        
        # Count input tokens
        input_tokens = self.count_tokens(doc_text) + self.count_tokens(query)
        
        # Get recommendations
        response = chain.run(documents=doc_text, query=query)
        
        # Count output tokens
        output_tokens = self.count_tokens(response)
        
        return {
            "recommendations": response,
            "sources": [doc.metadata.get('source', 'Unknown') for doc in documents]
        }, {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens
        }

    def analyze_document(self, document: Document) -> Dict:
        """Perform comprehensive analysis of a single document"""
        analysis_prompt = PromptTemplate(
            input_variables=["document"],
            template="""
            Analyze the following document and provide:
            1. Key points and main arguments
            2. Important dates and deadlines
            3. Financial implications
            4. Risk factors
            5. Action items
            
            Document:
            {document}
            
            Analysis:
            """
        )
        
        chain = LLMChain(
            llm=self.llm,
            prompt=analysis_prompt
        )
        
        return {
            "analysis": chain.run(document=document.page_content),
            "metadata": document.metadata
        }

    def get_chat_history(self) -> List[Dict]:
        """Retrieve the conversation history"""
        return self.memory.chat_memory.messages 