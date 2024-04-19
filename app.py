import streamlit as st
import pandas as pd
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Function to fetch books data from the database with optional filters and sorting
def fetch_books(search_query='', sort_by='title', order='asc'):
    con = connect_db()
    cur = con.cursor()
    search_query = f"%{search_query}%"
    order_sql = 'ASC' if order == 'asc' else 'DESC'

    query = f"""
    SELECT id, title, price, rating, description FROM books
    WHERE title ILIKE %s OR description ILIKE %s
    ORDER BY {sort_by} {order_sql}
    """
    cur.execute(query, (search_query, search_query))
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=['ID', 'Title', 'Price', 'Rating', 'Description'])
    cur.close()
    con.close()
    return df

# Function to establish a connection to the database
def connect_db():
    con = psycopg2.connect(os.getenv("DATABASE_URL"))
    return con

# Streamlit webpage setup
st.title('Book Display, Filter, and Search Portal')

# Search and filter options
search_query = st.text_input('Search for books (title, description)')
sort_options = ['title', 'price', 'rating']
sort_by = st.selectbox('Sort by', sort_options, index=0)
order_options = ['asc', 'desc']
order = st.selectbox('Order', order_options, index=0)

# Fetch and display books
books_df = fetch_books(search_query=search_query, sort_by=sort_by, order=order)
if not books_df.empty:
    st.write("Books found:", books_df.shape[0])
    st.dataframe(books_df)
else:
    st.write("No books found.")

