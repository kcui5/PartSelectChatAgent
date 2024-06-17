import os

PAGES_FOLDER = "pages"

def get_all_scraped_files():
    all_scraped_files = set()
    for file_name in os.listdir(PAGES_FOLDER):
        all_scraped_files.add(file_name[:-4])
    return all_scraped_files

if __name__ == "__main__":
    print(get_all_scraped_files())