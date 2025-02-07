import logging
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from Basic import mock_data, unique_books, books_by_genre, list_libraries, cheapest_library, calculate_avg_price, search_books_by_author, book_available, get_book_id, alternative_book_ids, filter_books

# Configure logging
logger = logging.getLogger(__name__)

class ActionValidateNumber(Action):
    def name(self):
        return "action_validate_number"

    def run(self, dispatcher, tracker, domain):
        book_count = tracker.get_slot("book_count")
        
        if book_count and 1 <= int(book_count) <= 10:
            return []  # Proceed with the story
        
        # If the number is invalid
        dispatcher.utter_message(text="Invalid input! Only values between 1 and 10 are allowed.")
        return [SlotSet("book_count", None)]  # Reset the slot to ask again


class ActionSearchAlternativeEditions(Action):
    def name(self) -> str:
        return "action_search_alternative_editions"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        # Retrieve the stored book title
        book_title = tracker.get_slot("book_title")
        if not book_title:
            dispatcher.utter_message(text="Sorry, I couldn't find the book title. Please provide it again.")
            return []

        dispatcher.utter_message(text=f"Searching for other editions of '{book_title}'...")

        # Fetch alternative ISBNs
        alternative_ids, non_accessible_ids = alternative_book_ids(book_title, "noview", dispatcher=dispatcher)

        # Get the message directly from filter_books (which already formats it properly)
        message = filter_books(alternative_ids, non_accessible_ids)

        # Send the final message to the user
        dispatcher.utter_message(text=message)

        return [SlotSet("author_name", None), SlotSet("book_title", None)]


        
        
class ActionCheckAvailability(Action):
    def name(self) -> str:
        return "action_check_availability"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Extract book title from entities
        entities = tracker.latest_message.get('entities', [])

        if entities:
            book_title = entities[0].get('value', None)
        else:
            book_title = tracker.get_slot("book_title")  # Fallback to slot
        
        # Debugging logs
        logger.info(f"Extracted book_title from entity: {book_title}")

        if not book_title:
            dispatcher.utter_message(text="I couldn't understand the book title. Please try again.")
            return []

        # Call API to get book ID and availability
        book_title, book_id, olid = get_book_id(book_title)
        
        # Debugging logs
        logger.info(f"API Response - Title: {book_title}, ISBN: {book_id}, OLID: {olid}")
        availability_info, preview_status = book_available(book_title, book_id, olid)
        logger.info(f"Preview status: {preview_status}")
        
        # Send availability info to the user
        dispatcher.utter_message(text=availability_info)

        # Log the preview status to check if it's being set correctly
        logger.info(f"Setting slot preview_status to: {preview_status}")

        # Set the slot to be used in follow-up rules
        events = [SlotSet("preview_status", preview_status)]
        

        # Trigger further action if the book is unavailable
        if preview_status == "noview":
           dispatcher.utter_message(template="utter_ask_further_search")

           

        # Return the full list of slot updates
        return events
      
        
        
class ActionConfirmBookTitle(Action):

    def name(self) -> str:
        return "action_confirm_book_title"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        
        # Try to extract the book title from the entities
        book_title = tracker.latest_message.get('entities', [{}])[0].get('value', None)

        if book_title:
            dispatcher.utter_message(text=f"Detecting the book's ID for '{book_title}'...")
        else:
            dispatcher.utter_message(text="Book's name was not detected, maybe there was a mistype? Try again!")

        return []

class ActionConfirmAuthor(Action):
    def name(self) -> Text:
        return "action_confirm_author"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Retrieve author's name from the slot
        author_name = tracker.get_slot("author_name")
        logger.info(f"Received author name: {author_name}")

        if not author_name:
            message = "I couldn't understand the author's name. Please provide a valid author."
            dispatcher.utter_message(text=message)
            return []

        # Ask user how many books they want to see
        dispatcher.utter_message(text=f"How many books would you like to search for {author_name}? Specify a number from 1 to 10.")
        return []

class ActionSearchBooksByAuthor(Action):

    def name(self) -> Text:
        return "action_search_books_by_author"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Retrieve author's name and number of books from slots
        author_name = tracker.get_slot("author_name")
        book_count = tracker.get_slot("book_count")

        logger.info(f"Received author name: {author_name} and book count: {book_count}")

        if not author_name:
            message = "I couldn't understand the author's name. Please provide a valid author."
            dispatcher.utter_message(text=message)
            return []

        if not book_count or not str(book_count).isdigit():
            message = "Please specify how many books you'd like to see."
            dispatcher.utter_message(text=message)
            return [SlotSet("book_count", None)]

        # Convert book_count to integer safely
        book_count = int(book_count)
        
        # Validate book_count for maximum limit
        if book_count > 10:
            message = "Please specify a number lower or equal to 10."
            dispatcher.utter_message(text=message)
            return [SlotSet("book_count", None)]  # Resetting the slot to prompt again

        # Fetch books using the existing function from Basic_script
        books = search_books_by_author(author_name)
        logger.info(f"API response for {author_name}: {books}")

        # Validate API response and extract book titles
        if isinstance(books, list) and len(books) > 0:
            book_titles = ', '.join(books[:book_count])
            message = f"Here are {book_count} books by {author_name}: {book_titles}"
        else:
            message = f"No books found for {author_name}."

        logger.info(f"Final message to user: {message}")
        dispatcher.utter_message(text=message)
        dispatcher.utter_message(text="Type a book's title (precisely) and I will check its availability in Open Library!")

        # Reset slots after completion to avoid stale values
        return [SlotSet("book_count", None)]

class ValidateSelectedBook(Action):
    def name(self):
        return "validate_mockBook_title"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        book_name = tracker.get_slot("mockBook_title")

        # Check if the book is in any of the genre lists
        book_found = any(book_name in books for books in mock_data.values())

        if book_found:
            dispatcher.utter_message(f"Great choice! You selected {book_name}.")
            return [SlotSet("mockBook_title", book_name)]
        else:
            dispatcher.utter_message("I couldn't find that book. Please choose one from the available list.")
            return [SlotSet("mockBook_title", None)]

class ActionBookDetails(Action):
    def name(self) -> str:
        return "action_book_details"

    def run(self, dispatcher, tracker, domain):
        # Get selected book title from slot
        mockBook_title = tracker.get_slot("mockBook_title")

        if not mockBook_title:
            dispatcher.utter_message(text="I didn't understand the book title. Please try again.")
            return []

        # Fetch available libraries
        libraries = list_libraries(mockBook_title)

        # Fetch the average price
        avg_price = calculate_avg_price(mockBook_title)

        # Fetch the cheapest library and its price
        cheapest_lib, cheapest_price = cheapest_library(mockBook_title)

        # Fetch Genre and Author from mock_data
        book_genre = "Unknown Genre"
        book_author = "Unknown Author"

        for library, books in mock_data.items():
            if mockBook_title in books:
                book_genre = books[mockBook_title].get("genre", "Unknown Genre")  # Get genre
                book_author = books[mockBook_title].get("author", "Unknown Author")  # Get author
                break  # Stop searching once the book is found

        if not libraries:
            dispatcher.utter_message(
                text=f"Sorry, the book '{mockBook_title}' is not available in any library."
            )
            return []

        # Prepare response message
        response = f"Genre: {book_genre} | Author: {book_author}\n"
        response += f"The book '{mockBook_title}' is available in the following libraries: {', '.join(libraries)}. "
        response += f"\nAverage price: ${avg_price:.2f}. "

        # Add cheapest library price
        if cheapest_lib and cheapest_price:
            response += f"\nBEST OFFER: {cheapest_lib} for ${cheapest_price:.2f}."
        else:
            response += "\nHowever, no pricing information is available."

        dispatcher.utter_message(text=response)
        return []


"""
class ActionBookDetails(Action):
    def name(self):
        return "action_book_details"

    def run(self, dispatcher, tracker, domain):
        # Get selected book from slot
        mockBook_title = tracker.get_slot("mockBook_title")

        if not mockBook_title:
            dispatcher.utter_message(text="I didn't understand the book title. Please try again.")
            return []

        # Fetch available libraries
        libraries = list_libraries(mockBook_title)

        # Fetch the average price
        avg_price = calculate_avg_price(mockBook_title)

        # Fetch the cheapest library and its price
        cheapest_lib, cheapest_price = cheapest_library(mockBook_title)

        if not libraries:
            dispatcher.utter_message(
                text=f"Sorry, the book '{mockBook_title}' is not available in any library."
            )
            return []

        # Prepare response message
        response = f"The book '{mockBook_title}' is available in the following libraries: {', '.join(libraries)}.\n"

        # Add the average price
        response += f"The average price for this book is ${avg_price:.2f}.\n"

        # Add cheapest library price
        if cheapest_lib and cheapest_price:
            response += f"The best option is at {cheapest_lib} for ${cheapest_price:.2f}."
        else:
            response += "However, no pricing information is available."

        dispatcher.utter_message(text=response)

        return []
"""
class ActionShowBooksByGenre(Action):
    def name(self):
        return "action_show_books_by_genre"

    def run(self, dispatcher, tracker, domain):
        # Get selected genre from slot
        selected_genre = tracker.get_slot("chosen_genre")

        if not selected_genre:
            dispatcher.utter_message(text="I didn't understand the genre. Please try again.")
            return []

        # Fetch books for the selected genre
        books = books_by_genre(selected_genre)

        if not books:
            dispatcher.utter_message(text=f"Sorry, no books found in the genre '{selected_genre}'.")
            return []

        # Prepare book list
        book_list = [f"{book}" for book in books]

        # Respond with book list
        dispatcher.utter_message(
            text="Here are the books available in your selected genre:\n" + "\n".join(book_list)
        )

        return []


        
class ActionMockLibrarySuggestions(Action):
    def name(self) -> Text:
        return "action_mocklibrary_suggestions"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        num_libraries = len(mock_data)
        total_unique_books, _ = unique_books()

        message = f"OK, we have access to {num_libraries} MockLibraries with a total of {total_unique_books} unique books. Do you want to see the available genres we have as a starting point?"
        dispatcher.utter_message(text=message)

        return []


class ActionPresentGenres(Action):
    def name(self) -> Text:
        return "action_present_genres"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logger.info("Executing ActionPresentGenres after affirmation.")
        genres = set()

        for library, books in mock_data.items():
            for book, details in books.items():
                genres.add(details['genre'])

        genres_list = list(genres)
        genres_message = f"We have the following genres available: {', '.join(genres_list)}."

        dispatcher.utter_message(text=genres_message)

        return []

        
class ActionBooksPerLibrary(Action):
    def name(self) -> Text:
        return "action_books_perLibrary"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = "Would you like to check books per library?"
        dispatcher.utter_message(text=message)

        return []
        

class ActionPresentLibraryBooks(Action):
    def name(self) -> str:
        return "action_present_library_books"

    def run(self, dispatcher, tracker, domain):
        # Get the user's chosen library
        selected_library = tracker.get_slot("library_index")

        # DEBUGGING: Print the slot value
        print(f"DEBUG: Retrieved slot value for library_index: {selected_library}")

        # Ensure the slot is not empty
        if not selected_library:
            dispatcher.utter_message(text="I didn't receive a valid library selection. Please try again.")
            return [SlotSet("library_index", None)]

        # Map user input (numbers) to actual library names
        library_mapping = {
            "1st": "e-Library1",
            "2nd": "e-Library2",
            "3rd": "e-Library3",
            "4th": "e-Library4",
            "5th": "e-Library5",
            "1":"e-Library1",
            "2":"e-Library2",
            "3":"e-Library3",
            "4":"e-Library4",
            "5":"e-Library5"
        }

        # Convert if necessary
        selected_library = library_mapping.get(selected_library, selected_library)

        # Ensure the chosen library exists in mock_data
        if selected_library not in mock_data:
            dispatcher.utter_message(text=f"'{selected_library}' is not a valid library. Please pick one from 1st to 5th.")
            return [SlotSet("library_index", None)]  # Reset slot only if invalid
        
        # Retrieve books in the selected library
        books = mock_data[selected_library].keys()
        if not books:
            dispatcher.utter_message(text=f"Sorry, there are no books in {selected_library}.")
            return []

        # Format response message
        book_list = ", ".join(books)
        response_message = f"Books available in {selected_library}: {book_list}."
        dispatcher.utter_message(text=response_message)

        return [SlotSet("library_index", selected_library)]  # Keep slot with correct value




class ActionHandleSecondNoResponse(Action):
    def name(self) -> Text:
        return "action_handle_second_no_response"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        total_unique_books, unique_books_list = unique_books()
        books_message = f"List of unique books: {', '.join(unique_books_list)}"
        dispatcher.utter_message(text=books_message)

        return []
