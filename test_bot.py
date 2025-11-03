from src.agent.graph_builder import BotPipeline

bot_pipeline = BotPipeline()
bot_pipeline.build_graph()
same_tool_queries = [
                    "what is the capital of France?",
                     ]

for query in same_tool_queries:
    response  = bot_pipeline.execute_graph(query, "e")
    print("Query: ", query)
    print("-"*80)
    print("Response: ", response)
    print("-"*80)
