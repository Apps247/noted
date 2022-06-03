# Noted

#### Video Demo:  https://youtu.be/FOObHxlGFV0

#### Description:
Noted is a platform for users to clear each other's doubts on various books they've read. The platform is made with flask handling server requests, and SQL for the backend database. BootStrap4 elements have been used for the UI.

app.py: 
Main flask routes and functions, SQL queries

helpers.py: 
+ Jinja filters
+ Functions that interact with the Google Books API
+ Functions that map JSON data received from the Google Books API to Python dictionaries 

noted.db:
The SQL database used to store data, with 4 tables: users, questions, answers, votes

to_run.txt:
Text file to aid with development, doesn't contribute to app's functionality

static/styles.css:
Primarily color customization and sizing styles for elements

Note: details about the roles of these templates can be found below
templates/
    account.html: account page 
    
    answer_question.html: shows questions, list of existing answers, as well as field to submit an answer
    
    apology.html: A simple page to display an error message for planned cases

    ask_question.html: UI to choose chapter number and enter doubt, having chosen book already 

    index.html: Homepage, also functions as page to view question list for a chosen book 

    layout.html: Skeleton of UI, includes Navbar element code, header scripts, and header links

    login.html: Form for existing uses to log in 

    my_answers.html: Page that displays current users answers, using a combination of question tiles & answer tiles 

    register.html: Form for new users to register 

    search_books.html: Page for users to search for and view search results for books, while choosing a book to ask a question for 

    search_results.html: Shows cards for books and questions that match user's search query (details below)

    macros/
        answer_tile: Element code for the reused answer tile element. Displays the answer, as well as information about said answer, including net vote score (= upvote count -downvote count). Includes a parameter thrpugh which the upvote and downvote button can be hidden

        question_tile: Element code for the reused question_tile element. Displays the question, as well as information about said questions, including date asked and chapter number. Also shows book title (which links to the Google Books page for the book) and a cover of the book. Includes a minimal variant that shows less information. Shows the full question tile by default, but will show minimal variant if requested by parameter.

On the homepage, questions with the least answers are sorted to show on top in order to drive more attention their way. Secondary & tertiary sorts are recency (decreasing date), and increasing chapter number.

The app does not have a table for book data, as book data is retrieved as required using the Google Books API. This data includes the title of the book, authors of the book, and the book's cover image (if any). The question table stores the Google Books book ID of the book the question is based on, for each record.

Searching for existing questions is done by checking whether the entered search phrase exists in any question phrase or book name (retrieves list of names of books of existing questions). The search function ignores case, but needs all the characters present, in order, to enlist a question / book name in the search results.
Eg: The Book "Hello World Book" will be enlisted as a search result for search terms "Hello" and "hello world", but not "Hello Book". On the results page, clicking a question card takes the user to the question's page, with all answers made to that question. These answers are sorted by descending net vote score. Clicking a book card takes the user to a list of questions made in that book. On this page, questions are sorted by increasing chapter number, followed by decreasing answer count, followed by recency, as the user is likely looking for answers, and it would also help to see questions ordered by chapter for the selected book.

The actions listed below require the user to be signed in. When creating an account, the app asserts that the chosen username must be unique, and the chosen password should be at least 8 characters long. A user who already has an account may log in with their username and password. Passwords are stored in hashed forms in the database.

If a user doesn't find a question they were looking for, they may ask their own. When asking a question, the user is first presented with a search bar where they can search for the book they have a doubt in. Their search term is used to query Google Books, using the Google Books API, to list books they could be referring to in order of relevance. They then select a book from that list, and optionally choose the chapter number their doubt is in. Entering a question is compulsory. No formatting options are provided for question.

Users can answer others' questions, and aren't prevented from answering their own. No formatting options are provided for answers. Answers are shown sorted in descending order of their net vote score. Users can submit multiple answers to a single question.

Users can vote on others' answers based on their seeming helpfulness and/or reliability. Users may not vote on their own answers. 

On their account page, users can see the number of questions and answers they've submitted, as well as their "Upvote Score" (= (total upvote count for all their answers - total downvote count for all their answers)*10). They can also see a list of questions, sorted primarily by decreasing answer count, as the user is likely looking for answers to questions they've asked. Secondary & tertiary sorts are recency (decreasing date), and increasing chapter number. Users can also see a list of answers they've submitted, and the net vote score of each. Answers are grouped by questions and sorted in descending order of their net vote score. 

In structuring the backend database, I weighed using an SQL-based approach vs a NoSQL JSON-based approach. A JSON-based approach, with its redundancy, would have made it easy to work with net vote scores and number of answers for each question while sorting. However, I ended up choosing SQL due to the minimized storage footprint and consistency advantages. However, due to thiss, I did have to write certain long queries for sorting questions based on their answer counts, and sorting answers based on their net vote scores.

### TODO:
+ Improve search functionality to match individual words rather than the entire search phrase
+ Include restrict deletion access to questions and answers, and a system to handle affected users' Upvote Scores when a deletion occurs.