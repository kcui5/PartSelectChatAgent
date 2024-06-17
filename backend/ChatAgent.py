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

    vector_store_id = os.environ["PSChatAgentVectorStoreID"]

    assistant = client.beta.assistants.create(
      name="PartSelect Chatbot Agent",
      instructions="You are a chatbot on the PartSelect website. Use you knowledge base to answer questions about refrigerator and dishwasher parts. Respond to unrelated queries with 'Sorry, I can't help with that!'",
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
