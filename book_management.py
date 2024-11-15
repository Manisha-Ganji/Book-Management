# book_service.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this if UI is running on a different port
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Define the data model for a Book
class Book(BaseModel):
    title: str
    author: str
    genre: str
    available: bool

# Connect to the database (SQLite)
def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create the book table (if it doesn't exist)
def create_books_table():
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        genre TEXT NOT NULL,
        available BOOLEAN NOT NULL
    );
    ''')
    conn.commit()
    conn.close()

create_books_table()

# Add a new book
@app.post("/books/", response_model=Book)
def add_book(book: Book):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO books (title, author, genre, available)
    VALUES (?, ?, ?, ?);
    ''', (book.title, book.author, book.genre, book.available))
    conn.commit()
    conn.close()
    return book

# Get details of a specific book by ID
@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    conn.close()
    if book:
        return Book(id=book['id'], title=book['title'], author=book['author'], genre=book['genre'], available=book['available'])
    raise HTTPException(status_code=404, detail="Book not found")

# Search books by title or author
@app.get("/books/search/", response_model=List[Book])
def search_books(query: str):
    conn = get_db_connection()
    books = conn.execute('''
    SELECT * FROM books WHERE title LIKE ? OR author LIKE ?;
    ''', ('%' + query + '%', '%' + query + '%')).fetchall()
    conn.close()
    return [Book(id=book['id'], title=book['title'], author=book['author'], genre=book['genre'], available=book['available']) for book in books]
