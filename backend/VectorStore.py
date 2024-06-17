from PartSelectScraper import PAGES_FOLDER

from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

VECTOR_STORE_FILE = "VectorStoreID.txt"

client = OpenAI()

def load_vector_store_id():
    if os.path.exists(VECTOR_STORE_FILE):
        with open(VECTOR_STORE_FILE, 'rb') as file:
            vector_store_id = str(file.read())[2:-1]
            print("Loaded vector store id", vector_store_id)
            return vector_store_id
    else:
        print("Could not find vector store file")

def upload_to_vector_store(vector_store_id):
    file_paths = []
    for file_name in os.listdir(PartSelectScraper.PAGES_FOLDER):
        file_path = os.path.join(PartSelectScraper.PAGES_FOLDER, file_name)
        
        if os.path.isfile(file_path):
            file_paths.append(file_path)
    print(f"Found files {file_paths}")

    num_files = len(file_paths)
    for i in range(num_files // 10):
        curr_start = 10 * i
        curr_end = min(len(file_paths), 10 * (i + 1))
        curr_files = file_paths[curr_start:curr_end]
        print("Uploading files ", curr_files)
        file_streams = [open(path, "rb") for path in curr_files]
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store_id, files=file_streams
        )
        for file in file_streams:
            file.close()

if __name__ == "__main__":
    if not os.path.exists(VECTOR_STORE_FILE):
        vector_store = client.beta.vector_stores.create(name="PartSelect Pages")
        print("Created vector store with ID ", vector_store.id)
        with open("VectorStore.txt", "w") as file:
            file.write(vector_store.id)
        vector_store_id = vector_store.id
    else:
        vector_store_id = load_vector_store_id()

    upload_to_vector_store(vector_store_id)
