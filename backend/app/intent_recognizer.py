from google import genai
from google.genai import types
from datetime import datetime
from .config import settings

class IntentRecognizer:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.setup_chat()
        
    def setup_chat(self):
        """Initializes a chat with Gemini for intent recognition"""
        sys_instruction = """
        You are an assistant specialized in analyzing user requests.
        Your task is EXCLUSIVELY to determine:
        1. If the request requires the use of a tool
        2. Which specific tool to use
        3. What parameters are needed for the tool
        
        RETURN ONLY a JSON object with this structure:
        
        {
            "action": "use_tool" | "direct_answer" | "clarify" | "confirmation" | "error",
            "tool_name": "tool_name" (only if action is "use_tool"),
            "parameters": { ... necessary parameters ... } (only if action is "use_tool"),
            "clarification_question": "question" (only if action is "clarify"),
            "request_confirmation": "question" (only if action is "confirmation"),
            "execution_plan": [ ... ] (only for complex multi-step requests)
        }
        
        IMPORTANT: 
        - Your output must be EXCLUSIVELY valid JSON, no additional text
        - Maintain the conversation context to better understand user requests
        - When you receive responses to clarification requests, use them to complete the previous action
        """
        
        self.config = types.GenerateContentConfig(
            system_instruction=sys_instruction,
            temperature=0.0
        )
        
        # Create a persistent chat
        self.chat = self.client.chats.create(
            model='gemini-2.0-flash-thinking-exp',
            config=self.config
        )
        
        # Initialize conversation context
        self.last_intent = None
        self.in_clarification = False
    
    def reset_chat(self):
        """Resets the chat when necessary"""
        self.setup_chat()
        
    async def recognize_intent(self, user_message, user_id):
        """Recognizes the user's intent and returns a structured JSON"""
        
        if user_message.strip() == "\\resetintent":
            self.reset_chat()
            return {
                "action": "direct_answer",
                "message": "Intent recognition has been reset."
            }
        
        # Build the prompt with information about available tools
        tools_info = """
        Available tools and their detailed descriptions:
        
        === REMINDER TOOLS ===
        
        1. create_reminder:
           Description: Creates a new reminder for the user.
           Parameters:
           - text (required): The text content of the reminder.
           - due_date (required): Due date and time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
           Example: "Create a reminder for tomorrow's meeting at 3:00 PM" -> {"action": "use_tool", "tool_name": "create_reminder", "parameters": {"text": "Meeting", "due_date": "2024-06-11T15:00:00"}}
           
        2. get_reminders:
           Description: Retrieves the user's existing reminders.
           Optional parameters:
           - skip (optional): Number of reminders to skip (for pagination).
           - limit (optional): Maximum number of reminders to return.
           Example: "Show me my reminders" -> {"action": "use_tool", "tool_name": "get_reminders", "parameters": {}}
           
        3. update_reminder:
           Description: Updates an existing reminder.
           Parameters:
           - reminder_id (required): ID of the reminder to update.
           - text (required): New text content of the reminder.
           - due_date (required): New date and time in ISO 8601 format.
           - is_active (required): New status of the reminder, true if active, false otherwise.
           Example: "Update reminder 5 with 'Doctor' for the day after tomorrow at 9" -> {"action": "use_tool", "tool_name": "update_reminder", "parameters": {"reminder_id": 5, "text": "Doctor", "due_date": "2024-06-12T09:00:00", "is_active": true}}
           
        4. delete_reminder:
           Description: Deletes a reminder.
           Parameters:
           - reminder_id (required): ID of the reminder to delete.
           Example: "Delete reminder number 3" -> {"action": "use_tool", "tool_name": "delete_reminder", "parameters": {"reminder_id": 3}}
           
        === SEARCH AND UTILITY TOOLS ===
        
        5. perform_deep_search:
           Description: Performs a web search to obtain real-time information. Must be used for questions about current events, facts, weather, news, sports, or information that might not be known. Never simulate web search results.
           Parameters:
           - queryList (required): List of specific search queries that will provide the most relevant results for the user's question. the defualt is 2 queries but can be more up to 10.
           Example: "What are the latest news about NVIDIA?" -> {"action": "use_tool", "tool_name": "perform_deep_search", "parameters": {"queryList": ["latest news NVIDIA technology AI today", "latest news NVIDIA stock price today"]}}
           
        === MEMORY TOOLS ===
        
        7. store_memory:
           Description: Stores the user's personal information. You must use this tool whenever the user asks to remember something. Invoke this function for EACH piece of information separately - do not aggregate information.
           Parameters:
           - content (required): The exact content to store (e.g., "the WiFi password is 12345"). Include ALL relevant details.
           - category (optional): The category of the information (e.g., "password", "birthday", "recipe").
           Example: "Remember that my mother's birthday is May 15" -> {"action": "use_tool", "tool_name": "store_memory", "parameters": {"content": "The user's mother's birthday is May 15", "category": "birthday"}}
           
        8. retrieve_memory:
           Description: Searches for previously stored information. You must use this tool whenever the user asks for information that might have been stored previously. Based on the conversation context, automatically invent and formulate the most relevant search query even if the user has not explicitly mentioned what to search for.
           Parameters:
           - query (required): The search query you deduced from the conversation context.
           - limit (optional): Maximum number of results to return.
           Example: "What was the WiFi password?" -> {"action": "use_tool", "tool_name": "retrieve_memory", "parameters": {"query": "WiFi password", "limit": 3}}
           
        9. update_memory:
           Description: Updates previously stored information. You must use this tool when the user asks to change or update previously stored information.
           Parameters:
           - query (required): Query to find the information to update (e.g., "WiFi password"). Be as specific as possible.
           - new_content (required): The new complete content to store with ALL relevant details.
           Example: "Update the WiFi password to ABC123" -> {"action": "use_tool", "tool_name": "update_memory", "parameters": {"query": "WiFi password", "new_content": "The WiFi password is ABC123"}}
           
        10. delete_memory:
            Description: Deletes stored information. You must use this tool when the user asks to delete or remove previously stored information.
            Parameters:
            - query (required): Query to find the information to delete (e.g., "WiFi password"). Be as specific as possible.
            Example: "Forget the WiFi password" -> {"action": "use_tool", "tool_name": "delete_memory", "parameters": {"query": "WiFi password"}}
        
        HANDLING COMPLEX SCENARIOS:
        
        1. If you need clarification: 
           Example: "Remind me of something" -> {"action": "clarify", "clarification_question": "What exactly would you like me to remember?"}
           
        2. For multi-step operations (e.g., "create 2 reminders for tomorrow at 12 AM and 3 PM for to buy milk and chocolate"):
           Example: {"action": "use_tool", "execution_plan": [
              {"tool_name": "create_reminder", "parameters": {"text": "Buy milk", "due_date": "2024-06-11T00:00:00"}},
              {"tool_name": "create_reminder", "parameters": {"text": "Buy chocolate", "due_date": "2024-06-11T15:00:00"}}
           ]}
           
        3. For direct responses without needing a tool:
           Example: "How are you?" -> {"action": "direct_answer"}
           
        4. For requests that require confirmation or when the user explicitly asks for confirmation:
           Example: "Do a deep search with 5 queries but do not execute them, show me the query before you execute them" -> {"action": "confirmation", "request_confirmation": "These are the queries: *list of queries*"}
           
        5. For errors or unexpected situations:
           Example: "search latest new on web. do 15 queries " -> {"action": "error", "error_message": "I'm sorry, i can perform only 10 queries at a time"}
        """
        
        # Build the complete prompt
        if self.in_clarification:
            # If we're in the clarification phase, inform the model that the response is related to the previous request
            prompt = f"""
            PREVIOUS CONTEXT: {self.last_intent}
            
            User's response to the clarification request: "{user_message}"
            
            Based on this response, create a complete intent with all necessary parameters.
            {tools_info}
            
            Return ONLY a structured JSON object with all details necessary to complete the action.
            """
        else:
            # Normal prompt
            prompt = f"""
            Analyze this user request and determine which action to take:
            
            "{user_message}"
            
            {tools_info}
            
            Respond ONLY with a structured JSON object as requested.
            """
        
        currentTime = datetime.now().isoformat()
        prompt += f"\n\n Current time is: {currentTime}"
        # Send the message to the chat and get the response
        print(f"Prompt sent to the model: {user_message}")
        response = self.chat.send_message(prompt)
        
        import json
        import re
        
        def clean_response_text(text: str) -> str:
            """Cleans the response text by removing any markdown delimiters"""
            text = re.sub(r'```\w*', '', text)  # Removes ```json, ```python, etc.
            text = re.sub(r'```', '', text)     # Removes remaining ```
            return text.strip()
        # Extract and validate JSON from the response
        try:
            cleaned_text = clean_response_text(response.text)
            intent_json = json.loads(cleaned_text)
            
            # Save the last intent for context
            self.last_intent = intent_json
            
            # Check if it's a clarification request
            if intent_json.get("action") == "clarify":
                self.in_clarification = True
            else:
                self.in_clarification = False
            
            # Add user_id to the JSON if necessary for tool execution
            if intent_json.get("action") == "use_tool" and "parameters" in intent_json:
                intent_json["parameters"]["user_id"] = user_id
                
            # Handle the execution_plan case
            if "execution_plan" in intent_json:
                for step in intent_json["execution_plan"]:
                    if "parameters" in step:
                        step["parameters"]["user_id"] = user_id
                        
            return intent_json
        except json.JSONDecodeError:
            # Fallback in case of invalid JSON
            print(f"Error in JSON analysis: {response.text}")
            self.in_clarification = False
            return {
                "action": "direct_answer",
                "error": "Unable to interpret the request"
            }
