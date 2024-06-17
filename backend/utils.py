import os
import PartSelectScraper

all_scraped_files = set()

def get_all_scraped_files():
    for file_name in os.listdir(PartSelectScraper.PAGES_FOLDER):
        all_scraped_files.add(file_name)


get_all_scraped_files()
print("PS17137081.txt" in all_scraped_files)