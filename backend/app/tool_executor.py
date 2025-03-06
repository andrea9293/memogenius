from . import gemini_tools, memory_tools, list_tools

class ToolExecutor:
    def __init__(self):
        # Mapping of available tools
        self.tool_map = {
            # Reminder tools
            "create_reminder": gemini_tools.create_reminder_tool,
            "get_reminders": gemini_tools.get_reminders_tool,
            "update_reminder": gemini_tools.update_reminder_tool,
            "delete_reminder": gemini_tools.delete_reminder_tool,
            
            # Search and utility tools
            "perform_deep_search": gemini_tools.perform_deep_search,
            # "get_current_datetime": gemini_tools.get_current_datetime,
            
            # Memory tools
            "store_memory": memory_tools.store_memory_tool,
            "retrieve_memory": memory_tools.retrieve_memory_tool,
            "update_memory": memory_tools.update_memory_tool,
            "delete_memory": memory_tools.delete_memory_tool,
            
            # List tools
            "get_list": list_tools.get_list_tool,
            "update_list_title": list_tools.update_list_title_tool,
            "clear_list": list_tools.clear_list_tool,
            "add_list_item": list_tools.add_list_item_tool,
            "update_list_item": list_tools.update_list_item_tool,
            "delete_list_item": list_tools.delete_list_item_tool,
            "mark_list_item_completed": list_tools.mark_list_item_completed_tool
        }
    
    async def execute_tool(self, tool_name, parameters):
        """Executes a single tool with the specified parameters"""
        if tool_name not in self.tool_map:
            return {
                "error": f"Unknown tool: {tool_name}",
                "status": "error"
            }
        
        try:
            print(f"Executing tool {tool_name} with parameters: {parameters}")
            result = self.tool_map[tool_name](**parameters)
            print(f"Result of tool {tool_name}: {result}")
            return {
                "status": "success",
                "tool_name": tool_name,
                "parameters": parameters,
                "result": result
            }
        except Exception as e:
            print(f"Error executing tool {tool_name}: {str(e)}")
            return {
                "status": "error",
                "tool_name": tool_name,
                "parameters": parameters,
                "error": str(e)
            }
    
    async def execute_plan(self, execution_plan, user_id):
        """Executes a multi-step execution plan"""
        results = []
        for step in execution_plan:
            # Make sure user_id is included in the parameters
            if "parameters" in step:
                step["parameters"]["user_id"] = user_id
            
            # Execute the tool
            result = await self.execute_tool(step["tool_name"], step["parameters"])
            results.append(result)
            
            # Stop if there's an error
            if result["status"] == "error":
                break
        
        return results
