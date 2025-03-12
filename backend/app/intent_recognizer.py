from google import genai
from google.genai import types
from datetime import datetime
from .config import settings
from . import gemini_tools, memory_tools, list_tools

class IntentRecognizer:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.setup_chat()
        
    def setup_chat(self):
        """Initializes a chat with Gemini for intent recognition with integrated tools"""
        sys_instruction = """
        You are an assistant specialized in analyzing and fulfilling user requests.
        
        Your primary goal is to determine:
        1. If the request requires the use of a specialized tool
        2. Which specific tool to use
        3. What parameters are needed for the tool
        4. Execute the tool and provide the results directly
        5. you can use more than one tool at a time if needed to fulfill the request
        
        When no specialized tool is needed, use direct_answer_tool.
        When clarification is needed, use request_clarification_tool.
        When confirmation is needed, use confirm_action_tool.
        
        IMPORTANT: 
        - Maintain conversation context to understand sequential requests
        - When you receive responses to clarification requests, use them to complete previous actions
        """
        
        # Define exit function declarations
        direct_answer_declaration = types.FunctionDeclaration(
            name="direct_answer_tool",
            description="Use this when no specialized tool is needed and you can answer directly. Never use this for questions that require current information like weather, date, time, or news.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "dummyParameter": types.Schema(
                        type=types.Type.STRING,
                        description="Unused dummy parameter",
                    ),
                },
                required=["dummyParameter"],
            ),
        )
        
        request_clarification_declaration = types.FunctionDeclaration(
            name="request_clarification_tool",
            description="Use this when you need more information to fulfill the user's request.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "question": types.Schema(
                        type=types.Type.STRING, 
                        description="The clarification question to ask the user."
                    )
                },
                required=["question"],
            ),
        )
        
        confirm_action_declaration = types.FunctionDeclaration(
            name="confirm_action_tool",
            description="Use this when you need to confirm an action with the user. before calling this function, collect all informations needed to confirm the action and pass them as a single string.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "question": types.Schema(
                        type=types.Type.STRING, 
                        description="The confirmation question to ask the user."
                    ),
                    "informations": types.Schema(
                        type=types.Type.STRING, 
                        description="data to show to the user to help them confirm the action"
                    )
                },
                required=["question"],
            ),
        )
        
        # Set up all available tools
        self.tools = [
            types.Tool(function_declarations=[
                # Exit functions
                direct_answer_declaration,
                request_clarification_declaration,
                
                # Reminder tools
                gemini_tools.create_reminder_declaration,
                gemini_tools.get_reminders_declaration,
                gemini_tools.update_reminder_declaration,
                gemini_tools.delete_reminder_declaration,
                
                # Search and utility tools
                # gemini_tools.perform_grounded_search_declaration,
                gemini_tools.perform_deep_search_declaration,
                gemini_tools.get_current_datetime_declaration,
                
                # Memory tools
                memory_tools.store_memory_declaration,
                memory_tools.retrieve_memory_declaration,
                memory_tools.update_memory_declaration,
                memory_tools.delete_memory_declaration,
                # memory_tools.delete_memories_batch_declaration,
                memory_tools.get_user_memories_declaration,
                
                # List tools - ora correttamente dichiarati
                list_tools.get_list_declaration,
                list_tools.update_list_title_declaration,
                list_tools.clear_list_declaration,
                list_tools.add_list_item_declaration,
                list_tools.update_list_item_declaration,
                list_tools.delete_list_item_declaration,
                list_tools.mark_list_item_completed_declaration,
            ])
        ]
        
        # Set up the function mapping for execution
        self.function_mapping = {
            # Exit functions
            "direct_answer_tool": self.direct_answer_handler,
            "request_clarification_tool": self.request_clarification_handler,
            "confirm_action_tool": self.confirm_action_handler,
            
            # Reminder tools
            "create_reminder": gemini_tools.create_reminder_tool,
            "get_reminders": gemini_tools.get_reminders_tool,
            "update_reminder": gemini_tools.update_reminder_tool,
            "delete_reminder": gemini_tools.delete_reminder_tool,
            
            # Search and utility tools
            #"perform_grounded_search": gemini_tools.perform_grounded_search,
            "perform_deep_search": gemini_tools.perform_deep_search,
            "get_current_datetime": gemini_tools.get_current_datetime,
            
            # Memory tools
            "store_memory": memory_tools.store_memory_tool,
            "retrieve_memory": memory_tools.retrieve_memory_tool,
            "update_memory": memory_tools.update_memory_tool,
            "delete_memory": memory_tools.delete_memory_tool,
            # "delete_memories_batch": memory_tools.delete_memories_batch_tool,
            "get_user_memories": memory_tools.get_user_memories_tool,
            
            # List tools - già correttamente mappati
            "get_list": list_tools.get_list_tool,
            "update_list_title": list_tools.update_list_title_tool,
            "clear_list": list_tools.clear_list_tool,
            "add_list_item": list_tools.add_list_item_tool,
            "update_list_item": list_tools.update_list_item_tool,
            "delete_list_item": list_tools.delete_list_item_tool,
            "mark_list_item_completed": list_tools.mark_list_item_completed_tool
        }
        
        self.config = types.GenerateContentConfig(
            system_instruction=sys_instruction,
            temperature=0.0,
            tools=self.tools,
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode='ANY')
            )
        )
        
        # Create a persistent chat
        self.chat = self.client.chats.create(
            model='gemini-2.0-flash',
            config=self.config
        )
        
        # Initialize conversation context
        self.last_intent = None
        self.in_clarification = False
    
    def direct_answer_handler(self, dummyParameter: str, user_id: int = None) -> dict:
        """Handler for direct answers"""
        return {
            "status": "success",
            "action": "direct_answer",
            "message": dummyParameter
        }
    
    def request_clarification_handler(self, question: str, user_id: int = None) -> dict:
        """Handler for clarification requests"""
        self.in_clarification = True
        return {
            "status": "success",
            "action": "clarify",
            "clarification_question": question
        }
    
    def confirm_action_handler(self, question: str, informations: str, user_id: int = None) -> dict:
        """Handler for confirmation requests"""
        return {
            "status": "success",
            "action": "confirm_action",
            "confirmation_question": question,
            "informations": informations
        }
    
    def reset_chat(self):
        """Resets the chat when necessary"""
        self.setup_chat()
    
    async def handle_function_call(self, function_name: str, function_args: dict) -> dict:
        """Handle calls to available functions"""
        if function_name in self.function_mapping:
            print(f"Executing function: {function_name} with args: {function_args}")
            result = self.function_mapping[function_name](**function_args)
            return result
        else:
            print(f"Unknown function: {function_name}")
            return {"error": f"Unknown function: {function_name}"}
    
    async def recognize_intent(self, user_message, user_id):
        """Recognizes the user's intent, executes tools if needed, and returns results"""
        
        if user_message.strip() == "\\resetintent":
            self.reset_chat()
            return {
                "action": "direct_answer",
                "message": "Intent recognition has been reset."
            }
        
        # Build the prompt based on context
        if self.last_intent :
            prompt = f"""
            PREVIOUS REQUEST CONTEXT: {self.last_intent}
            
            Analyze this user request and fulfill it using available tools if needed: 
            "{user_message}"
            
            """
        else:
            prompt = f"""
            Analyze this user request and fulfill it using available tools if needed:
            
            "{user_message}"
            """
        
        currentTime = datetime.now().isoformat()
        prompt += f"\n\nCurrent time: {currentTime}"
        # prompt += f"\n\nRemember: you can use more than one tool at a time if needed"
        
        print(f"Prompt sent to the model: {prompt}")
        
        response = self.chat.send_message(prompt)
        
        # Prepare the result structure
        result = {
            "original_message": user_message,
            "action": None
        }
        
        # Handle function calls
        tool_results = []
        
        # Gestione delle chiamate di funzione una sola volta (senza ciclo while)
        if response.function_calls:
            print(f"Response has {len(response.function_calls)} function calls")
            
            # Process all function calls
            function_responses = []
            
            for function_call in response.function_calls:
                function_name = function_call.name
                function_args = dict(function_call.args)
                
                # Add user_id to args
                if user_id and "user_id" not in function_args:
                    function_args['user_id'] = user_id
                
                # Execute the function
                function_result = await self.handle_function_call(
                    function_name,
                    function_args
                )
                
                print(f"Function result: {function_result}")
                
                # Handle special exit functions
                if function_name == "direct_answer_tool":
                    result["action"] = "direct_answer"
                    result["message"] = function_args.get("message", "")
                    self.in_clarification = False
                    # Non serve continuare per direct_answer
                    break
                elif function_name == "request_clarification_tool":
                    result["action"] = "clarify"
                    result["clarification_question"] = function_args.get("question", "")
                    self.in_clarification = True
                    # Non serve continuare per request_clarification
                    break
                else:
                    # This is a regular tool call
                    result["action"] = "use_tool"
                    
                    # Store tool execution info
                    tool_info = {
                        "tool_name": function_name,
                        "parameters": {k: v for k, v in function_args.items() if k != "user_id"},
                        "result": function_result
                    }
                    tool_results.append(tool_info)
                    
                    # Update the main result with first operational tool info
                    if "tool_name" not in result:
                        result["tool_name"] = function_name
                        result["parameters"] = {k: v for k, v in function_args.items() if k != "user_id"}
                
                # Aggiungi la risposta della funzione (useremmo questa solo se continuassimo il ciclo)
                function_responses.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=function_name,
                            response={"content": function_result}
                        )
                    )
                )
            
            # If there were operational tools used, add their results
            if tool_results:
                # If multiple operational tools were executed, create an execution plan
                if len(tool_results) > 1:
                    execution_steps = []
                    for tool_info in tool_results:
                        execution_steps.append({
                            "tool_name": tool_info["tool_name"],
                            "parameters": tool_info["parameters"]
                        })
                    result["execution_plan"] = execution_steps
                    if "tool_name" in result:
                        del result["tool_name"]
                    if "parameters" in result:
                        del result["parameters"]
                    
                result["tool_results"] = tool_results
                
        
        # Save the intent for context
        self.last_intent = result
        
        # Return the comprehensive result
        return result
