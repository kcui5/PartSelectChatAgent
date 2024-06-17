import requests
from bs4 import BeautifulSoup
import pickle
import os

BASE_URL = 'https://www.partselect.com'

PAGES_FOLDER = "pages"
SAVED_LINKS_FOLDER = "links"
POPULAR_DISHWASHER_PARTS_LINKS_FILE = os.path.join(SAVED_LINKS_FOLDER, "popular dishwasher parts.pkl")
POPULAR_REFRIGERATOR_PARTS_LINKS_FILE = os.path.join(SAVED_LINKS_FOLDER, "popular refrigerator parts.pkl")
DISHWASHER_BRANDS_AND_RELATED_LINKS_FILE = os.path.join(SAVED_LINKS_FOLDER, "dishwasher brands and related.pkl")
REFRIGERATOR_BRANDS_AND_RELATED_LINKS_FILE = os.path.join(SAVED_LINKS_FOLDER, "refrigerator brands and related.pkl")

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

def scrape_site(link):
    """Scrape content on product site"""
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
        print(f"Wrote content to file {name}")

def scrape_popular_parts(page, file_name):
    """Scrape 'Popular __ Parts' links"""
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

    with open(file_name, 'wb') as file:
        pickle.dump(links, file)
    return links

def scrape_brands_and_related_parts(page, file_name):
    """Scrape 'Refrigerator/Dishwasher Brands' and 'Related Refrigerator/Dishwasher Parts' links"""
    url = BASE_URL + page

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    class_name = "nf__links"
    ul_elems = soup.find_all('ul', class_=class_name)
    assert(len(ul_elems) == 3)
    # ul_elem[0] contains Refrigerator/Dishwasher Brands and ul_elem[1] contains Related Refrigerator/Dishwasher Parts
    links = []
    for i in range(2):
        ul_elem = ul_elems[i]
        li_elems = ul_elem.find_all('li')

        for li in li_elems:
            a_tag = li.find('a', href=True)
            if a_tag:
                links.append(a_tag['href'])
    
    with open(file_name, 'wb') as file:
        pickle.dump(links, file)
    return links

def scrape_popular_parts_from_list(file_name):
    """Scrape 'Popular __ Parts' links from file containing list of pages"""
    if os.path.exists(file_name):
        with open(file_name, 'rb') as file:
            links = pickle.load(file)
        print("Loaded links")
    else:
        print("Could not load links")
        return

    for link in links:
        f_name = link[1:-4]
        f_name = f_name.replace("-", "")
        f_name = os.path.join(SAVED_LINKS_FOLDER, f_name + ".pkl")

        scrape_popular_parts(link, f_name)

def scrape_brands_and_related_parts_from_list(file_name):
    """Scrape all parts from file containing list"""
    if os.path.exists(file_name):
        with open(file_name, 'rb') as file:
            links = pickle.load(file)
        print("Loaded links")
    else:
        print("Could not load links")
        return
    for link in links[8:]:
        f_name = link[1:-4]
        f_name = f_name.replace("-", "")
        f_name = os.path.join(SAVED_LINKS_FOLDER, f_name + ".pkl")
        scrape_links_from_file(f_name)

def scrape_links_from_file(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'rb') as file:
            links = pickle.load(file)
        print("Loaded links")
    else:
        print("Could not load links")
        return
    
    for l in links:
        scrape_site(l)

if __name__ == "__main__":
    scrape_popular_parts("/Dishwasher-Parts.htm", POPULAR_DISHWASHER_PARTS_LINKS_FILE)
    scrape_links_from_file(POPULAR_DISHWASHER_PARTS_LINKS_FILE)
    scrape_popular_parts("/Refrigerator-Parts.htm", POPULAR_REFRIGERATOR_PARTS_LINKS_FILE)
    scrape_links_from_file(POPULAR_REFRIGERATOR_PARTS_LINKS_FILE)
    scrape_brands_and_related_parts("/Dishwasher-Parts.htm", DISHWASHER_BRANDS_AND_RELATED_LINKS_FILE)
    scrape_popular_parts_from_list(DISHWASHER_BRANDS_AND_RELATED_LINKS_FILE)
    scrape_brands_and_related_parts_from_list(DISHWASHER_BRANDS_AND_RELATED_LINKS_FILE)
    scrape_brands_and_related_parts("/Refrigerator-Parts.htm", REFRIGERATOR_BRANDS_AND_RELATED_LINKS_FILE)
    scrape_popular_parts_from_list(REFRIGERATOR_BRANDS_AND_RELATED_LINKS_FILE)
    scrape_brands_and_related_parts_from_list(REFRIGERATOR_BRANDS_AND_RELATED_LINKS_FILE)