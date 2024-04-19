import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from db import Database
import streamlit as st

load_dotenv()
BASE_URL = 'http://books.toscrape.com/catalogue/page-{page}.html'
mydb = Database(os.getenv('DATABASE_URL'))

# Create table for books
mydb.create_books_table()

# Optional: Clear previous data
mydb.truncate_books_table()

# Scrape data
page = 1
while True:
    url = BASE_URL.format(page=page)
    print(f"Scraping {url}")
    response = requests.get(url)
    
    if response.status_code != 200:
        break

    soup = BeautifulSoup(response.content, 'html.parser')
    products = soup.select('article.product_pod')

    if not products:
        break

    for product in products:
        book = {}
        book['title'] = product.select_one('h3 a').get('title', 'No title')
        book['price'] = float(product.select_one('p.price_color').text.strip('£'))
        book['rating'] = product.select_one('p.star-rating')['class'][1]  # e.g., 'Three'
        description_url = 'http://books.toscrape.com/catalogue/' + product.select_one('h3 a')['href']
        
        # Fetch description from detail page
        detail_response = requests.get(description_url)
        detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
        book['description'] = detail_soup.select_one('.product_page p').text

        # Insert into database
        mydb.insert_book(book)

    page += 1

# Streamlit app
def main():
    st.title('Book Search and Filter App')
    with st.form("search_form"):
        name_query = st.text_input('Search by Book Name')
        description_query = st.text_input('Search by Description')
        sort_by = st.selectbox('Sort by', ['Rating', 'Price'])
        order = st.selectbox('Order', ['Ascending', 'Descending'])
        submit_button = st.form_submit_button("Search")

    if submit_button:
        results = mydb.search_books(name_query, description_query, sort_by, order)
        for result in results:
            st.text(f"{result['title']} - £{result['price']} - Rated: {result['rating']} - {result['description']}[:100]...")

if __name__ == "__main__":
    main()
