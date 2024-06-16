import requests
from bs4 import BeautifulSoup
import pickle
import os

BASE_URL = 'https://www.partselect.com'

PAGES_FOLDER = "pages"
POPULAR_DISHWASHER_PARTS_LINKS_FILE = "popular dishwasher parts.pkl"

"""Elements to scrape for each part website"""
to_fetch = [
    ("h1", "class", "title-lg mt-1 mb-3"),
    ("span", "itemprop", "productID"),
    ("span", "itemprop", "mpn"),
    ("span", "itemprop", "name"),
    ("h2", "class", "title-md"),
    ("div", "itemprop", "description"),
    ("div", "class", "col-md-6 mt-3"),
    ("div", "class", "pd__crossref mb-3 js-resultsRenderer")
]

def get_popular_parts(page):
    """Scrape popular dishwasher parts links"""
    url = BASE_URL + page

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    class_name = 'nf__part__detail__title'
    a_elements = soup.find_all('a', class_=class_name)
    assert(len(a_elements) >= 1)
    
    links = []
    for a in a_elements:
        print(a.get('href'))
        links.append(a.get('href'))

    with open(POPULAR_DISHWASHER_PARTS_LINKS_FILE, 'wb') as file:
        pickle.dump(links, file)
    return links

def clean_text(s):
    """Removes \n, \r, - and unnecessary spaces"""
    comps = s.split(" ")
    res = []
    for comp in comps:
        if comp == "":
            continue
        else:
            comp = comp.split("\n")
            for c in comp:
                nc = c.split("\r")
                for n in nc:
                    if n == "" or n == "-":
                        continue
                    res.append(n)
    return " ".join(res)

def get_popular_dishwasher_parts_contents():
    if os.path.exists(POPULAR_DISHWASHER_PARTS_LINKS_FILE):
        with open(POPULAR_DISHWASHER_PARTS_LINKS_FILE, 'rb') as file:
            links = pickle.load(file)
        print("Loaded links")
    else:
        links = get_popular_parts("/Dishwasher-Parts.htm")
        print("Retrieved links")
    
    for link in links:
        CONTENT = ""
        url = BASE_URL + link
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        for fetch in to_fetch:
            if fetch[1] == "class":
                elems = soup.find_all(fetch[0], class_=fetch[2])
            elif fetch[1] == "itemprop":
                elems = soup.find_all(fetch[0], itemprop=fetch[2])
            else:
                print("Unrecognized identifier!")
                assert(False)
            assert(len(elems) >= 1)
            for elem in elems:
                txt = clean_text(elem.text)
                if fetch[2] == "productID":
                    txt = "PartSelect Number: " + txt
                elif fetch[2] == "mpn":
                    txt = "Manufacturer Part Number: " + txt
                elif fetch[2] == "name":
                    txt = "Manufactured by " + txt
                CONTENT += txt + "\n"
                if fetch[2] == "productID":
                    name = elem.text + ".txt"
        file_name = os.path.join(PAGES_FOLDER, name)
        with open(file_name, "w") as file:
            file.write(CONTENT)
            print(f"Wrote content to file {name}.txt")

if __name__ == "__main__":
    get_popular_dishwasher_parts_contents()