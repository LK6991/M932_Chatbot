import requests
from bs4 import BeautifulSoup
import re
import logging
import os
import json

mock_data = {
    "e-Library1": {
        "Pancakes_CookBook": {"price": 11, "author": "AJ", "genre": "Cooking"},
        "Futuristic_Sports": {"price": 15, "author": "AB", "genre": "Science Fiction"},
        "Apple_Trees": {"price": 20, "author": "AB", "genre": "Gardening"},
        "Ancient_Seeds": {"price": 25, "author": "Michael Brown", "genre": "Gardening"},
        "Chess_Mantras": {"price": 6, "author": "David Wilson", "genre": "Games"},
        "Cars_Mars": {"price": 11, "author": "AC", "genre": "Science Fiction"},
        "Purple_Waters": {"price": 7, "author": "Sarah Taylor", "genre": "Metaphysics"}
    },
    "e-Library2": {
        "Pancakes_CookBook": {"price": 12, "author": "John Doe", "genre": "Cooking"},
        "Futuristic_Sports": {"price": 16, "author": "AB", "genre": "Science Fiction"},
        "Apple_Trees": {"price": 21, "author": "Emily Johnson", "genre": "Gardening"},
        "Ancient_Seeds": {"price": 11, "author": "Michael Brown", "genre": "Gardening"},
        "Crepe_Recipes": {"price": 14, "author": "Anna White", "genre": "Cooking"},
        "Chess_Mantras": {"price": 7, "author": "David Wilson", "genre": "Games"},
        "Cars_Mars": {"price": 11, "author": "AC", "genre": "Science Fiction"},
        "Lake_Fishing": {"price": 7, "author": "Robert Green", "genre": "Hobbies"}
    },
    "e-Library3": {
        "Pancakes_CookBook": {"price": 14, "author": "John Doe", "genre": "Cooking"},
        "Futuristic_Sports": {"price": 17, "author": "Jane Smith", "genre": "Science Fiction"},
        "Apple_Trees": {"price": 22, "author": "Emily Johnson", "genre": "Gardening"},
        "Ancient_Seeds": {"price": 9, "author": "Michael Brown", "genre": "Gardening"},
        "Chess_Mantras": {"price": 10, "author": "David Wilson", "genre": "Games"},
        "Cars_Mars": {"price": 9, "author": "AC", "genre": "Science Fiction"},
        "Lake_Fishing": {"price": 6, "author": "Robert Green", "genre": "Hobbies"}
    },
    "e-Library4": {
        "Pancakes_CookBook": {"price": 14, "author": "John Doe", "genre": "Cooking"},
        "Purple_Waters": {"price": 11, "author": "Sarah Taylor", "genre": "Metaphysics"},
        "Apple_Trees": {"price": 22, "author": "Emily Johnson", "genre": "Gardening"},
        "Ancient_Seeds": {"price": 17, "author": "Michael Brown", "genre": "Gardening"},
        "Chess_Mantras": {"price": 10, "author": "David Wilson", "genre": "Games"},
        "Cars_Mars": {"price": 9, "author": "AC", "genre": "Science Fiction"}
    },
    "e-Library5": {
        "Pancakes_CookBook": {"price": 14, "author": "John Doe", "genre": "Cooking"},
        "Purple_Waters": {"price": 10, "author": "Sarah Taylor", "genre": "Metaphysics"},
        "Crepe_Recipes": {"price": 17, "author": "Anna White", "genre": "Cooking"},
        "Ancient_Seeds": {"price": 15, "author": "Michael Brown", "genre": "Gardening"},
        "Chess_Mantras": {"price": 10, "author": "David Wilson", "genre": "Games"},
        "Cars_Mars": {"price": 9, "author": "AC", "genre": "Science Fiction"},
        "Lake_Fishing": {"price": 8, "author": "Robert Green", "genre": "Hobbies"}
    }
}


def count_libraries(book_title):
    """Count the number of libraries where a specific book is present."""
    count = 0

    for library in mock_data:
        if book_title in mock_data[library]:
            count += 1

    return count

def list_libraries(book_title):
    """List the libraries where a specific book is available."""
    libraries = []

    for library in mock_data:
        if book_title in mock_data[library]:
            libraries.append(library)

    return libraries


def calculate_avg_price(book_title):
    """Calculate the average price of a specific book across different libraries."""
    total_price = 0
    count = 0

    for library in mock_data:
        if book_title in mock_data[library]:
            total_price += mock_data[library][book_title]['price']
            count += 1

    if count == 0:
        return None  # Book not found in any library

    average_price = total_price / count
    return average_price


def get_book_price(library_name, book_title):
    """Retrieve the price of a specific book in a specific library."""
    if library_name in mock_data and book_title in mock_data[library_name]:
        return mock_data[library_name][book_title]['price']
    else:
        return None


def library_contents(library_name):
    """Print the number of books available in a specific library."""
    if library_name in mock_data:
        book_count = len(mock_data[library_name])
        print(f"{library_name} has {book_count} books.")
    else:
        print(f"Library '{library_name}' not found.")


def cheapest_library(book_title):
    """Find the library with the cheapest price for a specific book."""
    cheapest_price = float('inf')
    cheapest_library = None

    for library, books in mock_data.items():
        if book_title in books:
            price = books[book_title]['price']
            if price < cheapest_price:
                cheapest_price = price
                cheapest_library = library

    if cheapest_library is not None:
        return cheapest_library, cheapest_price
    else:
        return None, None


def unique_books():
    """Count the total number of unique books across all libraries and return the list of unique books."""
    unique_books = set()

    for library, books in mock_data.items():
        for book in books:
            unique_books.add(book)

    return len(unique_books), list(unique_books)

def books_by_genre(genre):
    """Retrieve unique books across all libraries based on the genre key."""
    books_by_genre = set()

    for library, books in mock_data.items():
        for book, details in books.items():
            if details['genre'] == genre:
                books_by_genre.add(book)

    return list(books_by_genre)

def books_by_author(author):
    """Retrieve books across all libraries written by a specific author."""
    books_by_author = set()

    for library, books in mock_data.items():
        for book, details in books.items():
            if details['author'] == author:
                books_by_author.add(book)

    return list(books_by_author)


# Define the cache file
CACHE_FILE = "cache.json"

# Load existing cache if available
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as file:
        try:
            cache = json.load(file)
        except json.JSONDecodeError:
            cache = {}  # In case of a corrupted file
else:
    cache = {}

def fetch_data(url):
    # Check if the URL is already cached
    if url in cache:
        print(f"Returning cached data for URL: {url}")
        return cache[url]
    else:
        print(f"Cache miss for URL: {url}. Fetching from API...")

    # Headers for the API request
    headers = {
        'User-Agent': 'Library Look-Up Assistant (your_email@example.com)'
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            cache[url] = response.json()

            # Save updated cache to the file
            with open(CACHE_FILE, "w") as file:
                json.dump(cache, file)

            print(f"Successfully fetched data from API for URL: {url}")
            return cache[url]
        else:
            print(f"Failed to fetch data. HTTP Status: {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        print("API request timed out!")
        return None

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

    
# Function to search books by author name
def search_books_by_author(author_name):
    url = f"https://openlibrary.org/search.json?author={author_name}"
    data = fetch_data(url)
    if data and 'docs' in data:
        return [book.get('title', 'No Title') for book in data['docs']]
    else:
        return []

def get_book_id(book_title):
    search_url = f"https://openlibrary.org/search.json?title={book_title}&fields=title,author_name,isbn,key"
    data = fetch_data(search_url)

    if not data or "docs" not in data:
        return book_title, None, None

    exact_match = None
    close_match = None

    for doc in data["docs"]:
        if "title" in doc:
            title_lower = doc["title"].lower()
            requested_lower = book_title.lower()

            if title_lower == requested_lower:  # Exact match
                exact_match = doc
                break
            elif requested_lower in title_lower:  # Partial match (e.g., "Animal Farm" vs "Animal Farm and Related Readings")
                close_match = doc

    best_match = exact_match or close_match
    if best_match:
        isbn = best_match["isbn"][0] if "isbn" in best_match and best_match["isbn"] else None
        olid = best_match["key"].split("/")[-1] if "key" in best_match else None
        return best_match["title"], isbn, olid  # Return the best found match

    return book_title, None, None  # No relevant match found

  
def book_available(book_title, book_id, olid):
    """
    Fetches the availability of a book using its ISBN or OLID from Open Library API.
    """

    preview_status = "unknown" 
    preview_url = "No link available."
    
    # Try fetching by ISBN first
    if book_id:
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{book_id}&jscmd=availability&format=json"
        data = fetch_data(url)

        if data and f'ISBN:{book_id}' in data:
            book_data = data[f'ISBN:{book_id}']
            preview_status = book_data.get("preview", "noview")
            preview_url = book_data.get('info_url', "No link available.")
        else:
            preview_status = "not_found"

    # If ISBN lookup fails, try OLID
    if preview_status == "not_found" and olid:
        url = f"https://openlibrary.org/api/books?bibkeys=OLID:{olid}&jscmd=availability&format=json"
        data = fetch_data(url)

        if data and f'OLID:{olid}' in data:
            book_data = data[f'OLID:{olid}']
            preview_status = book_data.get("preview", "noview")
            preview_url = book_data.get('info_url', "No link available.")
        else:
            preview_status = "unknown"

    # Interpret the preview status
    if preview_status == "full":
        message = "The entire book is available for free online reading."
    elif preview_status == "restricted":
        message = "A preview of the book is available for online reading."
    elif preview_status == "borrow":
        message = "You can borrow this book!"
    elif preview_status == "noview":
        message = "No online preview is available for this book."
    else:
        message = "Availability status unknown."

    # Final message with book details
    final_message = f"Keys found for book '{book_title}': ISBN={book_id if book_id else 'N/A'}, OLID={olid if olid else 'N/A'}\n"
    final_message += message + f"\nMore details: {preview_url}"

    return final_message, preview_status

def alternative_book_ids(book_title, status, max_results=7, max_isbns=1, dispatcher=None):
    search_url = f"https://openlibrary.org/search.json?title={book_title}&fields=title,author_name,isbn,key"
    search_results = fetch_data(search_url)

    alternative_ids = []  # Stores accessible books
    non_accessible_ids = []  # Stores non-accessible books
    accepted_isbns = 0  # Counter for found useful ISBNs
    total_checked = 0  # Counter for total ISBNs checked

    # Loop through search results but limit to 'max_results' count
    for idx, doc in enumerate(search_results.get("docs", [])):
        if idx >= max_results:  # Limit by books
            break  

        if "key" in doc and "title" in doc:
            if doc["title"].lower() == book_title.lower():
                if "isbn" in doc:
                    for alt_isbn in doc["isbn"]:
                        total_checked += 1  # Count every ISBN checked

                        # Stop if we reached max ISBNs (not just books)
                        if total_checked >= max_results:
                            break  

                        preview_status = book_available(book_title, alt_isbn, "N/A")

                        # If it's accessible, store it in alternative_ids
                        if preview_status in ["restricted", "full", "borrow"]:
                            isbn_status = {
                                "isbn": alt_isbn,
                                "status": preview_status
                            }
                            alternative_ids.append(isbn_status)
                            accepted_isbns += 1

                            # Stop if we found enough useful results
                            if accepted_isbns >= max_isbns:
                                break  
                        else:
                            # Store the non-accessible ISBNs
                            non_accessible_ids.append({
                                "isbn": alt_isbn,
                                "status": preview_status
                            })

    # User-friendly response
    if alternative_ids:
        first_alternative = alternative_ids[0]
        message = f"Identified {total_checked} alternative editions.\n"
        message += f"Retrieved ISBN: {first_alternative['isbn']}, Status: {first_alternative['status']}"
    else:
        message = f"Unfortunately, I searched over {total_checked} alternative options of the book, "
        message += "but neither one seems available for free."

    if dispatcher:
        dispatcher.utter_message(text=message)
    else:
        print(message)  # Fallback for debugging or non-bot environments

    return alternative_ids, non_accessible_ids  # Return both accessible & non-accessible ISBNs
    
def filter_books(alternative_ids, non_accessible_ids):
    """
    Determines and returns a message based on the availability of alternative book sources.

    Args:
        alternative_ids (list): A list of dictionaries containing accessible ISBNs and their status.
        non_accessible_ids (list): A list of dictionaries containing non-accessible ISBNs.

    Returns:
        str: A user-friendly message with a link to an accessible book if available,
             otherwise a fallback message with a link to a non-accessible book.
    """
    
    if alternative_ids:  # If there is at least one accessible source
        first_accessible = alternative_ids[0]  # Get the first accessible book
        isbn = first_accessible["isbn"]
        preview_url = f"https://openlibrary.org/isbn/{isbn}"  # Construct preview link

        message = (
            f"✅ Available link for partial or full preview of the book found!\n"
            f"📖 ISBN: {isbn}\n"
            f"🔗 You can check this link: {preview_url}"
        )
    
    elif non_accessible_ids:  # If no accessible books, use the first non-accessible
        first_non_accessible = non_accessible_ids[0]  # Get the first non-accessible book
        isbn = first_non_accessible["isbn"]
        info_url = f"https://openlibrary.org/isbn/{isbn}"  # Construct info link

        message = (
            f"ℹYou can visit this link for more information: {info_url}"
        )
    
    else:  # If both lists are empty
        message = "No book editions were found for this title. Please try another search."
    
    print(message)  # Display the message
    return message  # Return the message for further use