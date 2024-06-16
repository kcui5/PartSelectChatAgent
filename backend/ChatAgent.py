import VectorStore

from openai import OpenAI

client = OpenAI()

vector_store_id = VectorStore.load_vector_store_id()

assistant = client.beta.assistants.create(
    name="PartSelect Chatbot Agent",
    instructions="You are a chatbot on the PartSelect website. Use you knowledge base to answer questions about refrigerator and dishwasher parts. Respond to unrelated queries with 'Sorry, I can't help with that!'",
    model="gpt-4o",
    tools=[{"type": "file_search"}],
)
assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
)

thread = client.beta.threads.create(
  messages=[
    {
      "role": "user",
      "content": "Is part PS8727387 compatible with 63013003015?",
    }
  ]
)
 
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id, assistant_id=assistant.id
)
print("Created run")

messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

message_content = messages[0].content[0].text
annotations = message_content.annotations
citations = []
for index, annotation in enumerate(annotations):
    message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
    if file_citation := getattr(annotation, "file_citation", None):
        cited_file = client.files.retrieve(file_citation.file_id)
        citations.append(f"[{index}] {cited_file.filename}")

print(message_content.value)
print("\n".join(citations))