from modal import App, Image, Secret, web_endpoint

app = App("PartSelect-Chat-Agent")

handler_image = (
    Image.debian_slim()
    .pip_install("openai")
)

@app.function(image=handler_image, secrets=[Secret.from_name("PSChatAgentOpenAIKey"), Secret.from_name("PSChatAgentVectorStoreID")])
@web_endpoint(method="POST")
def ask(req: dict):
    import os
    from openai import OpenAI

    query: str = req["userQuery"]
    print("Received", query)

    client = OpenAI()

    # Check if the query is relevant using a preliminary function calling check
    relevancy_tools = [
        {
            "type": "function",
            "function": {
                "name": "is_relevant",
                "description": "Returns whether the given query is relevant to the PartSelect website and inventory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "isRelevant": {
                            "type": "boolean",
                            "description": "whether or not the query is relevant"
                        }

                    },
                    "required": ["isRelevant"],
                },
                
            }
        }
    ]
    relevancy_messages = []
    relevancy_messages.append({
        "role": "system",
        "content": "You are a chatbot on the PartSelect website. Given a user query to the chatbot you must decide whether or not the query is related to the PartSelect website and its appliances parts. Queries should be strictly relevant to the parts listed on the PartSelect website and inventory including but not limited to refrigerators and dishwashers. Just because the query mentions an appliance does not mean it is relevant, it must pertain to the PartSelect website"
    })
    relevancy_messages.append({
        "role": "user",
        "content": query
    })
    try:
      relevancy_response = client.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=relevancy_messages,
          tools=relevancy_tools,
          tool_choice={"type": "function", "function": {"name": "is_relevant"}}
      )
      relevancy_result = relevancy_response.choices[0].message.tool_calls[0].function.arguments[14]
      if relevancy_result == "f":
         return "Sorry, I can't help with that!"
    except:
       return "Sorry, I can't help with that!"

    # Now ask relevant question to GPT-4O with knowledge base
    vector_store_id = os.environ["PSChatAgentVectorStoreID"]

    assistant = client.beta.assistants.create(
      name="PartSelect Chatbot Agent",
      instructions="You are a friendly and helpful chatbot on the PartSelect website. Use your knowledge base to answer questions about appliance parts, mainly refrigerator and dishwasher parts. Respond to unrelated queries with 'Sorry, I can't help with that!' Completely adopt the persona of a customer service agent.",
      model="gpt-4o",
      tools=[{"type": "file_search"}],
      tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
    )

    thread = client.beta.threads.create(
      messages=[
        {
          "role": "user",
          "content": query,
        }
      ]
    )
    
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant.id
    )

    messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

    message_content = messages[0].content[0].text
    print(message_content.value)

    return message_content.value
