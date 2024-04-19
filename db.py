import psycopg2

class Database:
    def __init__(self, database_url) -> None:
        self.con = psycopg2.connect(database_url)
        self.cur = self.con.cursor()

    def create_books_table(self):
        q = """
        CREATE TABLE IF NOT EXISTS books (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            price NUMERIC(5,2) NOT NULL,
            rating TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.cur.execute(q)
        self.con.commit()

    def truncate_books_table(self):
        q = """
        TRUNCATE TABLE books
        """
        self.cur.execute(q)
        self.con.commit()

    def insert_book(self, book):
        q = """
        INSERT INTO books (title, price, rating, description) VALUES (%s, %s, %s, %s)
        """
        self.cur.execute(q, (book['title'], book['price'], book['rating'], book['description']))
        self.con.commit()

    def search_books(self, name_query, description_query, sort_by, order):
        q = f"""
        SELECT title, price, rating, description FROM books
        WHERE title ILIKE %s AND description ILIKE %s
        ORDER BY {sort_by} {'ASC' if order == 'ascending' else 'DESC'}
        """
        search_term = f"%{name_query}%"
        description_term = f"%{description_query}%"
        self.cur.execute(q, (search_term, description_term))
        return self.cur.fetchall()
