from google import genai
from google.genai import types
from datetime import datetime
from .config import settings
from .intent_recognizer import IntentRecognizer
from .tool_executor import ToolExecutor
import json

class ChatHandler:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.intent_recognizer = IntentRecognizer()
        self.tool_executor = ToolExecutor()
        self.setup_chat()
        
    def setup_chat(self):
        """Initializes the chat with Gemini for response generation"""
        sys_instruct = """
        You are Neko, a personal assistant. your goal is to help the user achieve their goals.
        
        the request is provided in the USER_MESSAGE field. on this field you must base the language and tone of your response.
        the system message is provided in the SYSTEM_MESSAGE field. do not include the SYSTEM_MESSAGE field in your response.
        
        You can:
        - search the web
        - get the current date and time
        - create reminders
        - retrieve reminders
        - update reminders
        - delete reminders
        - store memories
        - retrieve memories
        - update memories
        - delete memories
        
        Format responses using HTML.
        use <pre>text</pre> only for programming code blocks
        
        IMPORTANT:
        - Use ONLY the results provided by tools
        - Use ONLY HTML formatting
        - Always include links to sources when available
        """
        # - use <blockquote>text</blockquote> for quotations
        
        self.config = types.GenerateContentConfig(
            system_instruction=sys_instruct,
            temperature=1.5,
            max_output_tokens=5000
        )
        
        self.chat = self.client.chats.create(
            model='gemini-2.0-flash-thinking-exp',
            config=self.config
        )

    async def handle_message(self, message: str, user_id: int | None = None) -> dict:
        """Handles a message by applying the three-layer architecture"""
        print(f"Processing message: {message} for user: {user_id}")
        
        if message.strip() == "\\restartai":
            self.setup_chat()
            self.intent_recognizer = IntentRecognizer()
            return {
                "text": "The Gemini AI instance has been restarted."
            }
        
        # 1. INTENT RECOGNITION LAYER
        intent = await self.intent_recognizer.recognize_intent(message, user_id)
        print(f"Recognized intent: {intent}")
        
        # 2. TOOL EXECUTION LAYER (if necessary)
        tool_results = None
        if "execution_plan" in intent:
            # Gestire prima il caso di execution_plan
            tool_results = await self.tool_executor.execute_plan(
                intent["execution_plan"],
                user_id
            )
        elif intent["action"] == "use_tool":
            # Poi gestire il caso di strumento singolo
            intent["parameters"]["user_id"] = user_id
            tool_results = await self.tool_executor.execute_tool(
                intent["tool_name"], 
                intent["parameters"]
            )
        elif intent["action"] == "clarify":
            # Gestire le richieste di chiarimento
            return {
                "text": intent["clarification_question"]
            }
        
        # 3. RESPONSE GENERATION LAYER
        prompt = f"""
        USER_MESSAGE: {message}
        SYSTEM_MESSAGE: 
        """
        
        if tool_results:
            print(f"Tool results: {json.dumps(tool_results, indent=2, ensure_ascii=False)}")
            prompt += f"""
            Actual results obtained from tools:
            {json.dumps(tool_results, indent=2, ensure_ascii=False)}
            
            Generate a natural and informative response EXCLUSIVELY on these results.
            if there are some links, always include them in the response with label and real link. Always include and cite your sources when available.
            DO NOT invent or simulate information not present in the results.
            """
        else:
            prompt += """
            No tools were used for this request
            """
        currentTime = datetime.now().isoformat()
        prompt += f"\n\n Current time is: {currentTime}"
        prompt += "\n\n Use HTML format for response"
        print(f"Response to send to the model: {prompt}")
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
