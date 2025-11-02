from langchain_core.tools import tool
import requests
from typing import Dict, Any
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
                return f"The current time is {current_time}"
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
    
    def _get_http_response(self):
        @tool(response_format="dict")
        def http_rest_tool(query: str) -> Dict[str, Any]:
            """
            HTTP tool to get response from real public API.
            """
            url = "https://dummyjson.com/quotes/random"
            
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "source": "real_api",
                        "quote": data.get("quote", "No quote found"),
                        "author": data.get("author", "Unknown")
                    }
            except Exception:
                pass 

            return {
                "source": "mock",
                "quote": "The latency is currently 120ms.",
                "author": "System Monitor"
            }
        return http_rest_tool