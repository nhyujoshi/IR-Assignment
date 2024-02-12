# Importing Modules
import os
import os.path
import requests
from bs4 import BeautifulSoup
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh import scoring
import urllib.robotparser

# Defining Variables for crawling website and Whoosh Index Directory
url = "https://pureportal.coventry.ac.uk/en/organisations/ihw-centre-for-health-and-life-sciences-chls/publications/"
index_dir = "IndexDirectory"

# Defining Variables for Robot.txt Parser and setting robots.txt URL
rp = urllib.robotparser.RobotFileParser()
rp.set_url("https://pureportal.coventry.ac.uk/en/robots.txt")

def crawl():

    # Fetch the Coventry Publication page if allowed by robots.txt
    rp.read()
    if rp.can_fetch("*", url):
        response = requests.get(url)
    
    soup = BeautifulSoup(response.text, "html.parser")

    # Defining Whoosh Index Schema
    schema = Schema(title=TEXT(stored=True), authors=TEXT(stored=True), publication_year=ID(stored=True),publication_link=ID(stored=True, unique=True), author_profile_link=ID(stored=True))

    # Creating IndexDirectory if it doesn't exist already
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
    
    # Creating Whoosh Index
    ix = create_in(index_dir, schema)
    writer = ix.writer()

    # Defining the div from crawled website
    publication_elements = soup.find_all("div", class_= "result-container")

    # Extracting Title, Authors, Publication Year, Publication Link and Author Profile Link
    for publication in publication_elements:
        title_element = publication.find("h3" , class_="title")
        if title_element:
            title = title_element.get_text(strip = True)
        else:
            title = "N/A"
        
        authors_elements = publication.find_all("a" , class_ = "link person")
        if authors_elements:
            authors = [author.get_text(strip = True) for author in authors_elements]
        else:
            authors = ["N/A"]

        publication_year_element = publication.find("span" , class_= "date")
        if publication_year_element:
            publication_year = publication_year_element.get_text(strip = True)
        else:
            publication_year = "N/A"
        
        publication_link_element = publication.find("a" , class_= "link")
        if publication_link_element:
            publication_link = publication_link_element["href"]
        else:
            publication_link = "N/A"

        author_profile_link_element = publication.find('a', class_='link person')
        if author_profile_link_element:
            author_profile_link = author_profile_link_element['href']
        else:
            author_profile_link = "N/A"
        
        # Writing extracted data into Whoosh Index
        writer.add_document(title = title, authors = ', '.join(authors), publication_year = publication_year,
                            publication_link = publication_link, author_profile_link = author_profile_link)
    
    # Commiting write into Whoosh Index
    writer.commit()


def search(query):

    # Open IndexDirectory
    ix = open_dir(index_dir)
    
    # Defining Array to store Search Results
    search_results = []

    with ix.searcher(weighting=scoring.TF_IDF()) as searcher:
        # Parse the query to search by title or author
        query_parser = MultifieldParser(["title", "authors"], ix.schema)
        query = query_parser.parse(query)
       
        # Execute search to retrieve results
        results = searcher.search(query, terms = True)

        for result in results:
            search_results.append({
                "title": result['title'],
                "authors": result['authors'],
                "publication_year": result['publication_year'],
                "publication_link": result['publication_link'],
                "author_profile_link": result['author_profile_link'],
            })
    
    return search_results