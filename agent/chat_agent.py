import json
import google.generativeai as genai
from typing import List

from app.config import GEMINI_API_KEY, logger
from agent.models import Message, ChatRequest, ChatResponse
from agent.prompts import SYSTEM_PROMPT
from retriever.retrieval import retrieve_assessments, format_retrieval_context

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    
def generate_chat_response(chat_request: ChatRequest) -> ChatResponse:
    try:
        # Extract the latest user query
        messages = chat_request.messages
        if not messages:
            return ChatResponse(
                reply="Hello! How can I help you with SHL assessments today?",
                recommendations=[],
                end_of_conversation=False
            )
            
        latest_user_message = ""
        # Build a conversation history string for the prompt
        history_text = ""
        for msg in messages:
            if msg.role == "user":
                latest_user_message = msg.content
            history_text += f"{msg.role.capitalize()}: {msg.content}\n"
            
        # Retrieve relevant assessments from ChromaDB
        retrieved_results = retrieve_assessments(latest_user_message, top_k=15)
        context_str = format_retrieval_context(retrieved_results)
        
        # Format the system prompt
        formatted_system_prompt = SYSTEM_PROMPT.format(retrieved_context=context_str)
        
        # We need to construct the full prompt since Gemini's API takes a list of contents
        # But we can also set the system_instruction.
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=formatted_system_prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.0,
            )
        )
        
        # Format conversation for Gemini
        gemini_messages = []
        for msg in messages:
            role = "model" if msg.role == "assistant" else "user"
            gemini_messages.append({"role": role, "parts": [msg.content]})
            
        response = model.generate_content(gemini_messages)
        
        # Parse JSON
        response_text = response.text
        try:
            parsed_json = json.loads(response_text)
            
            # Create typed response
            return ChatResponse(**parsed_json)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from model: {response_text}")
            return ChatResponse(
                reply="I encountered an error processing your request. Could you please rephrase?",
                recommendations=[],
                end_of_conversation=False
            )
            
    except Exception as e:
        logger.error(f"Error in generate_chat_response: {e}")
        return ChatResponse(
            reply="An unexpected error occurred. Please try again later.",
            recommendations=[],
            end_of_conversation=False
        )
