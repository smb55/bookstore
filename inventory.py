import re
import json
from pathlib import Path
from typing import Dict, Tuple, List, Union, Any
from datetime import datetime


class Book:
    def __init__(self, title: str, author: str, ISBN: str) -> None:
        self.title = title
        self.author = author
        self.ISBN = ISBN

    # add a method to convert this object to a dictionary for serialisation
    def to_dict(self) -> Dict[str, str]:
        return {"title": self.title, "author": self.author, "ISBN": self.ISBN}


class Inventory:
    def __init__(self) -> None:
        self.books: Dict[str, Tuple[Book, int]] = {}  # Maps ISBN to (Book, quantity)
        # The accounting software would record most details of the sales
        # since this is quite complex with shipping, tax, cost of goods sold, etc
        # We will include sale number, datetime, ISBN, and quantity in our sales list.
        self.sales: List[Dict[str, Union[str, int, datetime]]] = []
        # Set a counter for the sale number
        self.next_sale = 1

    def process_sale(self, isbn: str, qty: int) -> str:
        """Process a sale for a specific quantity of a specific book."""
        # First check there is enough stock in the inventory, and if so remove it
        outcome: bool = self.remove_book(isbn, qty)
        if not outcome:
            return "Insufficient stock"
        # Process the sale
        sale = {"sale_number": self.next_sale, "isbn": isbn, "datetime": datetime.now(), "qty": qty}
        self.sales.append(sale)
        self.next_sale += 1
        return "Success"

    def add_book(self, book: Book, quantity: int) -> None:
        # check if the book is already in the inventory
        if book.ISBN in self.books:
            # if so add the quantity to the number in inventory
            self.books[book.ISBN] = (
                self.books[book.ISBN][0],
                self.books[book.ISBN][1] + quantity,
            )
        else:
            # otherwise, add the book and quantity to the inventory
            self.books[book.ISBN] = (book, quantity)

    def remove_book(self, ISBN: str, quantity: int) -> bool:
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
    
    # To make this program a proper backend, rather than printing results they should be returned
    # This would enable a front end to process and display them.

    def list_inventory(self) -> None:
        for ISBN, (book, quantity) in self.books.items():
            print(f"{book.title} by {book.author}, ISBN: {ISBN}, Qty: {quantity}")

    def search_books(self, search_term: str) -> None:
        term = re.escape(search_term)
        pattern = f".*{term}.*"
        matches: List[Tuple[str, str, int]] = []
        for book in self.books.items():
            if re.search(pattern, book[1][0].title):
                # save matches in format (ISBN, Title, Qty in stock)
                matches.append((book[0], book[1][0].title, book[1][1]))

        if matches != []:
            print("Matches found:")
            for ISBN, title, qty in matches:
                print("ISBN:", ISBN, "Title:", title, "Qty in stock:", qty)
        else:
            print("No matches found.")

    # Serialisation - save and load data from file
    def save_data(self, path: Union[str, Path]) -> str:
        """Save the object data to the full path specified"""
        try:
            norm_path = Path(path)
            # convert objects to dictionaries for serialisation
            serialisable_books = {
                isbn: (book.to_dict(), qty) for isbn, (book, qty) in self.books.items()
            }
            with norm_path.open("w") as f:
                json.dump(serialisable_books, f, indent=4)
            return "Success!"
        except Exception as e:
            return str(e)

    def load_data(self, path: Union[str, Path]) -> str:
        """Load data from the path specified. This replaces any current data."""
        try:
            norm_path = Path(path)
            with norm_path.open("r") as f:
                books_data = json.load(f)
            self.books = {
                isbn: (Book(**book_info), qty)
                for isbn, (book_info, qty) in books_data.items()
            }
            return "Success!"
        except Exception as e:
            return str(e)

    # Add handling of transactions - implement a method to record sales. Remove from inventory and log
    # the sale with book, qty, time. Have a way to store this and query it.


# Set up some things to run for testing purposes:

# Get the directory where the current script is located
current_dir = Path(__file__).parent
# Define the path to the inventory data file
inventory_data_path = current_dir / "inventory_data.json"

book1 = Book("How to Python", "Some Nerd", "123")
book2 = Book("How to Play Rugby", "Some Lad", "321")
book3 = Book("How to Make Money", "Some Scammer", "888")

library_inventory = Inventory()
library_inventory.add_book(book1, 5)
library_inventory.add_book(book2, 8)
library_inventory.add_book(book3, 99)
# list inventory to verify books have been added
library_inventory.list_inventory()

response = library_inventory.save_data(inventory_data_path)
print(response)
# remove some books
library_inventory.remove_book(book3.ISBN, 10)
# check it worked
library_inventory.list_inventory()
# run a search
library_inventory.search_books("Rugby")
# load the data from before the books were removed
response = library_inventory.load_data(inventory_data_path)
print(response)
# confirm we are back at initial stock level
library_inventory.list_inventory()
# process a sale
library_inventory.process_sale("123", 3)
# confirm stock level has been reduced and the sale recorded
library_inventory.list_inventory()
print(library_inventory.sales)