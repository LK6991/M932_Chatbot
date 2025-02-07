# Task-Oriented Dialog System Prototype

## Domain
A chatbot designed to retrieve information from a mock or online library.
Reason for this choice: 
In a highly digitalized world, reading remains a very basic interest or hobby,
so implementing a chatbot, even in a very basic form, to automate a bit the searching for online books was appealing.
The core idea was to check availability of books online, so the user can save time from individual checking across sources.
In its ideal form (check #Future Improvements) that would lead to a wider construction of functionalities, to scan across multiple sources.

## Scenarios
  Searching for a book (Mock Center)
  1) - Through genre selection (presentation of available genre categories, selection, book options per genre --> selection of a book)
  2) - Through libraries (presentation of mock libraries, book options --> selection of a book)
  3) - Rejecting these choices, leads to a presentation of the total list of available books --> selection of a book)

  Searching for a book (OpenLibrary)
  1) - Search by author name (The user picks an author, writes a number of books (from 1 to 10), and then selects one --> gets availability status and a link)
  2) - Search by book title (The user writes a title (it must be written precisely to match an OpenLibrary title) --> gets availability status of the book and a link)

## Data Sources
- I constructed a Python dictionary named mock_data, which is a kind of Mock Center for the chatbots
  *This basic dictionary has nested dictionaries within it, which represent five mock libraries
  *Within this nested dictionaries (the libraries), there are the most crucial dictionaries, which represent the books.
  *Every book has 3 keys: genre, price, author
- Real-world data: Utilized the API of OpenLibrary
  * The function fetch_data is a central function which establishes intercation with OPpen Library APIs, handles requests, error handling and caching
  * This function is called internally within any other task-specific function that retrieves data from OpenLibrary endpoints
  * It creates a CACHE.JSON (if not exist) and puts there data from the retrievals, to then utilize cache instead of calling all the time APIs.
  * This was implemented to avoid an aggressive retrieval from the API in case of repetitive efforts, as OpenLibrary states on its site its concerns.
  * Additionaly, for that reason, a careful limit was placed within the function alternative_book_ids (which searches for alternative editions of a given book)

## Challenges
- Difficulties to utilize the checkpoint keyword of yaml, since it is available only on stories and not rules.
- Experimenting with checkpoints lead to big confusions and threatened at some point the structure of the simple functionalities I had achieved.
- So, I did a step back here.
- The handling of API needs caution: even with the limits I placed, calling very frequently the actions that trigger the wider search might lead to a rejection.

## Setup Instructions
1. Download the repository
2. Make a rasa project with the rasa init command in an empty folder
3. Put the files of this repository in your rasa project without changing their hierarchy.
4. I present here, what is imported in the two python files (Basic.py, actions.py), so as to understand the packages to install in your environment before trying:

BASIC.PY: 
import request, logging, json, re, os
from bs4 import BeautifulSoup

ACTIONS.PY:
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction



## Example Runs
The examples are demonstrated better in the PowerPointfile I submitted!

## Future Improvements
- Make the dialogues less linear and more flexible, relying more on stories and less to rules
- Utilize more entities of yaml, that allow more creative setup and looping paths in case of wrong input
- Enhance NLU with bigger quantities of example, option that I did choose for now to avoid complexities in my effort.
- Utilization of a range of APIs of online libraries, and creating fluid functions that allow a book search across multiple sources!
- Extending the capabiilities of the chatbot, so as to perform a separate search for Audiobook!


