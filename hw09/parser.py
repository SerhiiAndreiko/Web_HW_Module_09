# import json
# from pathlib import Path
# from pprint import pprint
# import requests
# from bs4 import BeautifulSoup
# import concurrent.futures

# from database.connect import connect_db
# from database.seeds import seeds


# json_dest = Path(__file__).parent.joinpath("database").joinpath("json")


# def parse_url_author(url_data: str) -> dict:
#     result = {}
#     url, base_author_name = url_data
#     next = None
#     if not url:
#         return result, next
#     css_author = "h3.author-title"
#     css_born = "div.author-details > p > strong"
#     css_born = "div.author-details span.author-born-date"
#     css_born_location = "div.author-details span.author-born-location"
#     css_desc = "div.author-description"
#     # print(url)
#     html_doc = requests.get(url)
#     if html_doc.status_code != 200:
#         return result, next
#     soup = BeautifulSoup(html_doc.content, "html.parser")
#     author_name = soup.select_one(css_author).text.strip()
#     author_born = soup.select_one(css_born).text.strip()
#     author_born_location = soup.select_one(css_born_location).text.strip()
#     author_desc = soup.select_one(css_desc).text.strip()
#     result = {
#         base_author_name: {
#             "fullname": author_name,
#             "born_date": author_born,
#             "born_location": author_born_location,
#             "description": author_desc,
#         }
#     }
#     return result


# def parse_url_quotes(url: str) -> tuple[list[dict], next]:
#     result = []
#     next = None
#     if not url:
#         return result, next
#     css_selector_next = "nav .next > a"
#     # print(url)
#     html_doc = requests.get(url)
#     if html_doc.status_code != 200:
#         return result, next
#     soup = BeautifulSoup(html_doc.content, "html.parser")
#     quotes_block = soup.select("div.quote")
#     next = soup.select_one(css_selector_next)

#     for quote in quotes_block:
#         quote_text = quote.select_one("span.text")
#         tag = quote.select_one("div.tags")
#         author_block = quote.select_one("span:nth-child(2)")
#         author_name = author_block.select_one("small.author")
#         author_link = author_block.select_one("a")
#         q_text = quote_text.text.strip()
#         q_author = {
#             "author_name": author_name.text.strip(),
#             "author_link": author_link.get("href"),
#         }
#         q_tags = [t.text.strip() for t in tag.find_all("a", attrs={"class": "tag"})]
#         result.append({"tags": q_tags, "author": q_author, "quote": q_text})
#     if next:
#         next = next.get("href")
#     return result, next


# def parse_data_quotes(
#     base_url: str = "https://quotes.toscrape.com", max_records: int = 1000
# ) -> list[dict]:
#     store_ = []
#     url = base_url
#     while True:
#         if not url:
#             break
#         result, next_url = parse_url_quotes(url)
#         store_.extend(result)
#         if max_records:
#             max_records -= 1
#             if max_records <= 0:
#                 print("Limit on the number of accepted records, stop.")
#                 break
#         if not next:
#             break
#         if next_url:
#             url = base_url + next_url
#         else:
#             break
#     return store_


# def parse_data_authors(
#     data: list[dict], base_url: str = "https://quotes.toscrape.com"
# ) -> dict:
#     store_ = {}
#     url = base_url
#     urls = set()
#     for record in data:
#         author = record.get("author")
#         if author:
#             author_name = author.get("author_name")
#             author_link = author.get("author_link")
#             url = base_url + author_link
#             urls.add((url, author_name))
#             # author_info = parse_url_author((url, author_name))
#             # store_.append(author_info)
#     # pprint(urls)

#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         results = executor.map(parse_url_author, urls)

#     for result in results:
#         store_.update(result)

#     return store_






# def main():
#     print("> Get Quotes")
#     data_quotes = parse_data_quotes(max_records=None)
#     print(f"< Loaded Quotes: {len(data_quotes)}")
#     print("> Get Authors (ThreadPool)")
#     data_authors = parse_data_authors(data_quotes)
#     print(f"< Loaded Authors: {len(data_authors)}")
#     # pprint(data_authors)
#     print("= Tune Authors Names on Quotes")
#     data_quotes = correction_quotes_author_name(data_quotes, data_authors)
#     # pprint(data_quotes)
#     print("> Save json files for Authors and Quotes")
#     quotes_path = json_dest.joinpath("quotes.json")
#     authors_path = json_dest.joinpath("authors.json")
#     save_to_json(quotes_path, data_quotes)
#     save_to_json(authors_path, list(data_authors.values()))
#     print(f"< Saved json files: {str(authors_path.name)}, {str(quotes_path.name)}")
#     print("> Save json files to Database")
#     save_to_database()
#     print("< Saved json files to Database")

# if __name__ == "__main__":
#     main()

import json
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

from database.connect import connect_db
from database.seeds import seeds

json_dest = Path(__file__).parent.joinpath("database").joinpath("json")

# Define constants for CSS selectors and URLs
CSS_AUTHOR = "h3.author-title"
CSS_BORN = "div.author-details span.author-born-date"
CSS_BORN_LOCATION = "div.author-details span.author-born-location"
CSS_DESC = "div.author-description"
BASE_URL = "https://quotes.toscrape.com"


def get_html_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None


def parse_author_info(url, base_author_name):
    response = get_html_content(url)
    if response is None:
        return {}

    soup = BeautifulSoup(response.content, "html.parser")
    author_name = soup.select_one(CSS_AUTHOR).text.strip()
    author_born = soup.select_one(CSS_BORN).text.strip()
    author_born_location = soup.select_one(CSS_BORN_LOCATION).text.strip()
    author_desc = soup.select_one(CSS_DESC).text.strip()

    return {
        base_author_name: {
            "fullname": author_name,
            "born_date": author_born,
            "born_location": author_born_location,
            "description": author_desc,
        }
    }


def parse_quotes(url):
    response = get_html_content(url)
    if response is None:
        return [], None

    soup = BeautifulSoup(response.content, "html.parser")

    quotes_block = soup.select("div.quote")
    next_page = soup.select_one("nav .next > a")

    quotes = []
    for quote in quotes_block:
        quote_text = quote.select_one("span.text").text.strip()
        tag = [t.text.strip() for t in quote.select("div.tags a.tag")]
        author_name = quote.select_one("span small.author").text.strip()
        author_link = quote.select_one("span a").get("href")

        quotes.append({
            "tags": tag,
            "author": {
                "author_name": author_name,
                "author_link": author_link
            },
            "quote": quote_text
        })

    next_url = next_page.get("href") if next_page else None

    return quotes, next_url


def parse_data_quotes(base_url=BASE_URL, max_records=1000):
    store = []
    url = base_url

    while url and (max_records is None or max_records > 0):
        quotes, next_url = parse_quotes(url)
        store.extend(quotes)

        if next_url:
            url = base_url + next_url
        else:
            break

        if max_records is not None:
            max_records -= len(quotes)

    return store



def parse_data_authors(data, base_url=BASE_URL):
    urls = [(base_url + record["author"]["author_link"], record["author"]["author_name"]) for record in data]

    with ThreadPoolExecutor() as executor:
        results = executor.map(parse_author_info, *zip(*urls))

    return {k: v for result in results for k, v in result.items()}

def save_to_json(file_path: Path, data: list[dict]):
    with file_path.open("w", encoding="UTF-8", newline="") as fd:
        json.dump(data, fd, ensure_ascii=False)

def save_to_database():
    if connect_db():
        seeds()


def correction_quotes_author_name(
    data_quotes: list[dict], data_authors: dict
) -> list[dict]:
    result = []
    for record in data_quotes:
        author = record.get("author")
        if author:
            author_name = author.get("author_name")
            data_author = data_authors.get(author_name)
            if data_author:
                record["author"] = data_author.get("fullname")
        result.append(record)
    return result

def main():
    print("> Get Quotes")
    data_quotes = parse_data_quotes(max_records=None)
    print(f"< Loaded Quotes: {len(data_quotes)}")

    print("> Get Authors (ThreadPool)")
    data_authors = parse_data_authors(data_quotes)
    print(f"< Loaded Authors: {len(data_authors)}")

    print("= Tune Authors Names on Quotes")
    data_quotes = correction_quotes_author_name(data_quotes, data_authors)

    print("> Save json files for Authors and Quotes")
    quotes_path = json_dest.joinpath("quotes.json")
    authors_path = json_dest.joinpath("authors.json")
    save_to_json(quotes_path, data_quotes)
    save_to_json(authors_path, list(data_authors.values()))
    print(f"< Saved json files: {str(authors_path.name)}, {str(quotes_path.name)}")

    print("> Save json files to Database")
    save_to_database()
    print("< Saved json files to Database")

if __name__ == "__main__":
    main()
