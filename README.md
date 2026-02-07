A BASIC DIGITAL LIBRARY ASSISTANT

## Domain
A chatbot designed to retrieve information from a mock or online library.
Reason for this choice: 
In a highly digitalized world, reading remains a fundamental interest and hobby.
Implementing a chatbot - even in a very basic form - to automate the search for online books felt meaningful.
The core idea was to check the online availability of books so users can save time instead of checking multiple sources individually. 
In its ideal form (see Future Improvements), this could expand into broader functionality that scans multiple online sources simultaneously.

## Scenarios
  Searching for a book (Mock Center)
  1) - Through genre selection (presentation of available genres --> selection --> book options per genre -- book selection)
  2) - Through libraries (presentation of mock libraries --> book options --> selection of a book)
  3) - Rejecting the aforementioned options, leads to a presentation of the full list of available books --> selection of a book)

  Searching for a book (OpenLibrary)
  1) - Search by author name (The user picks an author, requests a number of books (from 1 to 10), and then selects one --> receives availability status and a link)
  2) - Search by book title (The user enters a title (must match precisely an OpenLibrary title) --> rceeives availability status and a link)

## Data Sources

1. I constructed a Python dictionary named mock_data, which acts as a Mock Center for the chatbot.
   
* This dictionary contains nested dictionaries representing five mock libraries.
* Inside these nested dictionaries are book dictionaries.
* Each book has three keys: genre, price, and author.

3. Real-world data: OpenLibrary API

* The function fetch_data is a central function that establishes interaction with the OpenLibrary API, handles requests, error handling, and caching.
* It is called internally by task-specific functions that retrieve data from OpenLibrary endpoints.
* It creates CACHE.JSON (if it does not exist) and stores retrieved data to avoid repeated API calls.
* This was implemented to avoid excessive API requests, as OpenLibrary warns against aggressive querying.

Additionally, a careful limit was placed in the function alternative_book_ids, which searches for alternative editions of a given book.

## Challenges
- Difficulty using the checkpoint keyword in YAML, since it is available only in stories and not in rules.
- Experimenting with checkpoints caused confusion and at some point threatened the structure of the simple functionality already implemented.
- As a result, I stepped back temporarily from using checkpoints.
- API handling requires caution: even with limits in place, frequent calls that trigger broader searches may lead to request rejection.

## Setup Instructions

1. Download the repository.
2. Create a Rasa project using the `rasa init` command in an empty folder.
3. Place the files from this repository into your Rasa project without changing their hierarchy.
4. Below are the imports used in the two Python files (`Basic.py`, `actions.py`) so you can install the required packages beforehand.

**BASIC.PY imports**
- import request, logging, json, re, os
- from bs4 import BeautifulSoup

**ACTIONS.PY imports**
- from typing import Any, Text, Dict, List
- from rasa_sdk import Action, Tracker
- from rasa_sdk.executor import CollectingDispatcher
- from rasa_sdk.events import SlotSet, FollowupAction

## Example Runs
The examples are demonstrated in the PowerPoint report of my assignment's submission.

## Future Improvements
Make dialogues less linear and more flexible, relying more on stories and less on rules. 

Use more YAML entities to enable more creative dialogue flows and looping paths in case of incorrect input.

Improve NLU with more examples (kept minimal for now to avoid unnecessary complexity).

Use multiple online-library APIs and implement functions that search across sources.

Extend chatbot capabilities to support audiobook searches.







