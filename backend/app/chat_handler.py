from google import genai
from google.genai import types
from .config import settings
from . import gemini_tools, memory_tools

sys_instruct = """
    You are a Personal Assistant named Neko. You speak in Italian or English as the human wishes.
    
    You have specific tools available and MUST use them:

    1. For ANY web searches: ALWAYS use perform_grounded_search tool
    2. For reminders: use create_reminder, get_reminders, update_reminder, delete_reminder tools
    3. For current time: use get_current_datetime tool
    4. For remember and your memory management (RAG): use store_memory, retrieve_memory, update_memory, delete_memory tools

    NEVER invent or simulate responses. ALWAYS use the appropriate tool.

    Format responses using HTML tags:
    - <b>text</b> for bold
    - <i>text</i> for italic
    - <u>text</u> for underline
    - <s>text</s> for strikethrough
    - <pre>text</pre> for code
    - <a href="URL">text</a> for links
    - \n for line breaks (never use <br>)
    - <blockquote>text</blockquote> for quotes

    For lists:
    • Use bullet points with \n
    • Format important terms in <b>bold</b>
    • Use <i>italic</i> for emphasis

    IMPORTANT: 
    - ALWAYS use tools for real-time data
    - NEVER generate fictional responses
    - Use ONLY HTML formatting, no Markdown
    - Always include source links when using web search
    - If you don't know exact time, use get_current_datetime tool without asking confirmation
    - When storing or updating memories, include all relevant details
    - For ambiguous memory queries, ask the user to be more specific
"""

class ChatHandler:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.setup_chat()

    def setup_chat(self):
        """Initialize chat with Gemini and configure available tools"""
        self.tools = [
            types.Tool(function_declarations=[
                gemini_tools.create_reminder_declaration,
                gemini_tools.get_reminders_declaration,
                gemini_tools.update_reminder_declaration,
                gemini_tools.delete_reminder_declaration,
                gemini_tools.perform_grounded_search_declaration,
                gemini_tools.get_current_datetime_declaration,
                
                # memory tools
                memory_tools.store_memory_declaration,
                memory_tools.retrieve_memory_declaration,
                memory_tools.update_memory_declaration,
                memory_tools.delete_memory_declaration
            ])
        ]
        
        self.config = types.GenerateContentConfig(
            tools=self.tools,
            system_instruction=sys_instruct,
            temperature=0.7
        )
        
        self.chat = self.client.chats.create(
            model='gemini-2.0-flash',
            config=self.config
        )

    async def handle_function_call(self, function_name: str, function_args: dict) -> dict:
        """Handle calls to available functions"""
        function_mapping = {
            "create_reminder": gemini_tools.create_reminder_tool,
            "get_reminders": gemini_tools.get_reminders_tool,
            "update_reminder": gemini_tools.update_reminder_tool,
            "delete_reminder": gemini_tools.delete_reminder_tool,
            "perform_grounded_search": gemini_tools.perform_grounded_search,
            "get_current_datetime": gemini_tools.get_current_datetime,
            
            # memory tools
            "store_memory": memory_tools.store_memory_tool,
            "retrieve_memory": memory_tools.retrieve_memory_tool,
            "update_memory": memory_tools.update_memory_tool,
            "delete_memory": memory_tools.delete_memory_tool
        }
        
        if function_name in function_mapping:
            print(f"Function {function_name} called with args: {function_args} and user_id: {function_args['user_id']}")
            result = function_mapping[function_name](**function_args)
        else:
            result = {"error": f"Unknown function: {function_name}"}
            
        print(f"Function {function_name} called with args: {function_args} and returned: {result}")
        return result

    async def handle_message(self, message: str, user_id: int | None = None) -> dict:
        """Handle a message and return the appropriate response"""
        print(f"Processing message: {message} for user: {user_id}")
        response = self.chat.send_message(message)
        result = {"text": ""}

        while True:
            if response.function_calls:
                print(f"Response has {len(response.function_calls)} function calls")
                # Collect all function responses in one pass
                function_responses = []
                
                for function_call in response.function_calls:
                    function_name = function_call.name
                    function_args = dict(function_call.args)
                    
                    if user_id:
                        function_args['user_id'] = user_id

                    print(f"Executing function: {function_name} with args: {function_args}")
                    function_result = await self.handle_function_call(
                        function_name, 
                        function_args
                    )
                    print(f"Function result: {function_result}")
                    
                    # Add response to list instead of sending immediately
                    function_responses.append(
                        types.Part(
                            function_response=types.FunctionResponse(
                                name=function_name,
                                response={"content": function_result}
                            )
                        )
                    )
                
                # Send all responses in a single message
                response = self.chat.send_message(
                    types.Content(
                        parts=function_responses,
                        role="function"
                    )
                )
            elif response.text:
                result["text"] = response.text
                break

        return result
