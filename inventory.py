import re
import json
from pathlib import Path

class Book:
    def __init__(self, title, author, ISBN):
        self.title = title
        self.author = author
        self.ISBN = ISBN

    # add a method to convert this object to a dictionary for serialisation
    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "ISBN": self.ISBN
        }

class Inventory:
    def __init__(self):
        self.books = {}  # Maps ISBN to (Book, quantity)

    def add_book(self, book, quantity):
        # check if the book is already in the inventory
        if book.ISBN in self.books:
            # if so add the quantity to the number in inventory
            self.books[book.ISBN] = (self.books[book.ISBN][0], self.books[book.ISBN][1] + quantity)
        else:
            # otherwise, add the book and quantity to the inventory
            self.books[book.ISBN] = (book, quantity)

    def remove_book(self, ISBN, quantity):
        # if the book exists and there are enough in stock
        if ISBN in self.books and self.books[ISBN][1] >= quantity:
            # remove the quantity requested
            self.books[ISBN] = (self.books[ISBN][0], self.books[ISBN][1] - quantity)
            # if this leaves zero books, remove the book from inventory completely
            if self.books[ISBN][1] == 0:
                del self.books[ISBN]
            return True
        # if there weren't enough books to remove, return False
        return False

    def list_inventory(self):
        for ISBN, (book, quantity) in self.books.items():
            print(f"{book.title} by {book.author}, ISBN: {ISBN}, Qty: {quantity}")
    
    def search_books(self, search_term):
        term = re.escape(search_term)
        pattern = f".*{term}.*"
        matches = []
        for book in self.books.items():
            if re.search(pattern, book[1][0].title):
                # save matches in format (ISBN, Title, Qty in stock)
                matches.append((book[0], book[1][0].title, book[1][1]))
        
        if matches != []:
            print("Matches found:")
            for (ISBN, title, qty) in matches:
                print("ISBN:", ISBN, "Title:", title, "Qty in stock:", qty)
        else:
            print("No matches found.")

    # Serialisation - save and load data from file
    def save_data(self, path):
        '''Save the object data to the full path specified'''
        try:
            norm_path = Path(path)
            # convert objects to dictionaries for serialisation
            serialisable_books = {isbn: (book.to_dict(), qty) for isbn, (book, qty) in self.books.items()}
            with norm_path.open('w') as f:
                json.dump(serialisable_books, f, indent=4)
            return "Success!"
        except Exception as e:
            return str(e)  
    
    def load_data(self, path):
        '''Load data from the path specified. This replaces any current data.'''
        try:
            norm_path = Path(path)
            with norm_path.open('r') as f:
                books_data = json.load(f)
            self.books = {isbn: (Book(**book_info), qty) for isbn, (book_info, qty) in books_data.items()}
            return "Success!"
        except Exception as e:
            return str(e)

    # Add handling of transactions - implement a method to record sales. Remove from inventory and log
    # the sale with book, qty, time. Have a way to store this and query it.

# Set up some things to run for testing purposes:

# Get the directory where the current script is located
current_dir = Path(__file__).parent
# Define the path to the inventory data file
inventory_data_path = current_dir / 'inventory_data.json'

book1 = Book("How to Python", "Some Nerd", "123")
book2 = Book("How to Play Rugby", "Some Lad", "321")
book3 = Book("How to Make Money", "Some Scammer", "888")

library_inventory = Inventory()
library_inventory.add_book(book1, 5)
library_inventory.add_book(book2, 8)
library_inventory.add_book(book3, 99)

library_inventory.list_inventory()

response = library_inventory.save_data(inventory_data_path)
print(response)

library_inventory.remove_book(book3.ISBN, 10)

library_inventory.list_inventory()

library_inventory.search_books("Rugby")

response = library_inventory.load_data(inventory_data_path)
print(response)

library_inventory.list_inventory()
