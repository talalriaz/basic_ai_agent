from langchain_core.tools import tool
from src.retrieval.vector_db import VectorDBManager


class ToolDefinitions:
    def __init__(self):
            pass
          
    def _get_time_tool(self):
            """Get current date and time"""
            @tool(response_format="content")
            def _get_current_time():
                """Get the current time"""
                from datetime import datetime
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                current_date = now.strftime("%Y-%m-%d") 
                return f"The current time is {current_time} and date is {current_date}"
            return _get_current_time

    def _get_hr_policies(self):
            """Get all policies related to HR and administration for employees"""
            @tool(response_format="content")
            def _get_hr(user_query: str):
                """Get all policies related to HR and administration for employees"""
                try:
                    vector_db_manager = VectorDBManager()
                    text = vector_db_manager.query_db(user_query,top_k=3)
                    return text
                except Exception as e:
                    return 'Error in retrieving context'
            return _get_hr