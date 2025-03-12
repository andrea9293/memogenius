from google import genai
from google.genai import types
from datetime import datetime
from .config import settings
from .intent_recognizer import IntentRecognizer
import json

class ChatHandler:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.intent_recognizer = IntentRecognizer()
        self.setup_chat()
        
    def setup_chat(self):
        """Initializes the chat with Gemini for response generation"""
        sys_instruct = """
        You are Neko, a personal assistant. Your goal is to help the user in all requested activities.
        
        The request is provided in the USER_MESSAGE field. Base the language and tone of your response on this field.
        The system message is provided in the SYSTEM_MESSAGE field. Do not include the SYSTEM_MESSAGE field in your response.
        
        Format responses using HTML.
        Use <pre>text</pre> only for programming code blocks.
        
        IMPORTANT:
        - Use ONLY the results provided by tools
        - Use ONLY HTML formatting
        - Always include links to sources when available
        - Be concise but informative
        - Match the user's language (Italian or English)
        """
        
        self.config = types.GenerateContentConfig(
            system_instruction=sys_instruct,
            temperature=1.5
        )
        
        self.chat = self.client.chats.create(
            model='gemini-2.0-flash-thinking-exp',
            config=self.config
        )

    async def handle_message(self, message: str, user_id: int | None = None) -> dict:
        """Handles a message using the intent recognizer's integrated tool execution"""
        print(f"Processing message: {message} for user: {user_id}")
        
        if message.strip() == "\\restartai":
            self.setup_chat()
            self.intent_recognizer = IntentRecognizer()
            return {
                "text": "The Gemini AI instance has been restarted."
            }
        
        # Use the intent recognizer to analyze and execute tools if needed
        intent_result = await self.intent_recognizer.recognize_intent(message, user_id)
        print(f"Intent recognizer result: {json.dumps(intent_result, indent=2, ensure_ascii=False)}")
        
        # Handle different action types
        if intent_result["action"] == "direct_answer":
            prompt = f"""
            USER_MESSAGE: {message}
            SYSTEM_MESSAGE: 
            Generate a natural and friendly response. I delegate the response to you.
            """
            # The appropriate direct response is: "{intent_result.get('message', '')}"
        
        elif intent_result["action"] == "clarify":
            prompt = f"""
            USER_MESSAGE: {message}
            SYSTEM_MESSAGE: 
            
            I need to ask the user for clarification.
            The clarification question is: "{intent_result.get('clarification_question', 'Could you provide more information?')}"
            """
        
        elif intent_result["action"] == "use_tool":
            prompt = f"""
            USER_MESSAGE: {message}
            SYSTEM_MESSAGE: 
            
            Tool execution results:
            {json.dumps(intent_result.get("tool_results", []), indent=2, ensure_ascii=False)}
            
            Generate a natural and informative response based EXCLUSIVELY on these results.
            If there are links, always include them in the response with label and real link.
            Always include and cite your sources when available.
            DO NOT invent or simulate information not present in the results.
            """
        
        else:
            # Fallback per azioni sconosciute
            prompt = f"""
            USER_MESSAGE: {message}
            SYSTEM_MESSAGE: 
            
            I'm not sure how to process this request. Please generate a polite response asking the user to try again or rephrase their request.
            """
        
        # Aggiungi informazioni sul timestamp e formattazione
        currentTime = datetime.now().isoformat()
        # prompt += f"\n\n Current time is: {currentTime}"
        prompt += "\n\n Use HTML format for response"
        
        print(f"Prompt for response generation: {prompt}")
        response = self.chat.send_message(prompt)
        
        return {
            "text": self.clean_response_text(response.text)
        }
        
    def clean_response_text(self, text: str) -> str:
        """Cleans the response text by removing any markdown delimiters"""
        import re
        text = re.sub(r'```\w*', '', text)
        text = re.sub(r'```', '', text)
        return text
