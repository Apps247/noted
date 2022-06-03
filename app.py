
from logging import log

from sqlalchemy.sql.operators import exists

from helpers import login_required, map_book_json, request_book_data, request_book_list, apology, sort_by_scrore, universal_date
# import sqlite3
from cs50 import SQL
import os
from flask import Flask, render_template, redirect, request, session
from tempfile import mkdtemp
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime


app = Flask(__name__)

# + Code from C$50 finance distribution code
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# + Code from C$50 finance distribution code
# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# + Code adapted from C$50 finance distribution code
# Custom filter
app.jinja_env.filters["universal_date"] = universal_date

# + Code from C$50 finance distribution code
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# + Code from C$50 finance distribution code
# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


db = SQL('sqlite:///noted.db', connect_args={'check_same_thread': False})


@app.route('/')
def index(book_id='', mine = False):
    if (mine):
        questions = db.execute("SELECT *, (SELECT COUNT(*) FROM answers WHERE question_id = questions.id) AS answer_count FROM questions WHERE questions.user_id = ? ORDER BY answer_count DESC, date DESC, chapter_number ASC;",session["user_id"])
    else:
        if (book_id != ''):
            questions = db.execute("SELECT *, (SELECT COUNT(*) FROM answers WHERE question_id = questions.id) AS answer_count FROM questions WHERE questions.book_id = ? ORDER BY chapter_number ASC, answer_count DESC, date DESC;", book_id)
        else:          
            questions = db.execute("SELECT *, (SELECT COUNT(*) FROM answers WHERE question_id = questions.id) AS answer_count FROM questions ORDER BY answer_count ASC, date DESC, chapter_number ASC;")
    
    for question in questions:
        book_data = request_book_data(question['book_id'])
        question["book_name"] = book_data["name"]
        question["book_image_url"] = book_data["image_url"]
        question["book_preview_url"] = book_data["preview_url"]
        question["username"] = db.execute(
            "SELECT username FROM users WHERE id = ?", question["user_id"])[0]["username"]
    return render_template('index.html', questions=questions)

@app.route('/questions')
def questions():
    book_id = request.args.get("book_id")
    if book_id != '' and book_id is not None:
        return index(book_id = book_id)
    else:
        return index()

@app.route('/my_questions')
def my_questions():
    return index(mine=True)

@app.route('/login', methods=['GET', 'POST'])
def login():

    session.clear()

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        print("Username:", username)

        matching_users = db.execute(
            "SELECT id, password_hash FROM users WHERE username = ?", username)

        if len(matching_users) == 0:
            return apology("Username not found")

        else:
            user_data = matching_users[0]
            if check_password_hash(user_data["password_hash"], password):
                session["user_id"] = user_data["id"]
                return redirect("/")
            else:
                return apology(f"Incorrect password for {username}")
    else:
        return render_template("login.html")

@app.route('/search', methods=["POST"])
def search():
    query = request.form.get("query")
    print("Query:",query)

    existing_books = [request_book_data(book["book_id"]) for book in db.execute("SELECT DISTINCT book_id FROM questions;")]
    book_list = [book for book in existing_books if book["name"].lower().__contains__(query.lower())]

    print("Existing Books")
    print(existing_books)
    print()
    print("Book List")
    print(book_list)

    question_list = db.execute('SELECT *, (SELECT COUNT(*) FROM answers WHERE question_id = questions.id) AS answer_count FROM questions WHERE lower(questions.question) LIKE ? ORDER BY answer_count DESC;',f"%{query.lower()}%")
    for question in question_list:
        book_data = [book for book in existing_books if book["id"] == question["book_id"]][0]
        question["book_name"] = book_data["name"]
        question["book_image_url"] = book_data["image_url"]
        question["username"] = db.execute(
            "SELECT username FROM users WHERE id = ?", question["user_id"])[0]["username"]


    return render_template("search_results.html",books=book_list, questions=question_list, query=query)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        # if len(password)

        if username == '' or password == '':
            return apology("Please fill out all fields")
        elif len(password) < 8:
            return apology("Passwords must be at leasr 8 characters long")
        elif password != request.form.get('confirm-password'):
            return apology("Passwords do not match")
        else:
            existing_users_with_username = db.execute("SELECT COUNT(*) FROM users WHERE username = ?",username)[0]['COUNT(*)']
            if existing_users_with_username > 0:
                return apology(f"Sorry, the username \"{username}\" is already in use.")
            session["user_id"] = db.execute(
                "INSERT INTO users VALUES (NULL,?,?)", username,  generate_password_hash(password))
            return redirect("/")

    else:
        return render_template("register.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect("/login")


@app.route('/account')
@login_required
def account():
    user_data = db.execute('SELECT id, username FROM users WHERE id = ?',session["user_id"])[0]

    upvote_count = int(db.execute("SELECT COUNT(*) FROM votes, answers WHERE votes.answer_id = answers.id AND votes.positive = TRUE AND answers.user_id = ?",session["user_id"])[0]["COUNT(*)"])
    downvote_count = int(db.execute("SELECT COUNT(*) FROM votes, answers WHERE votes.answer_id = answers.id AND votes.positive = FALSE AND answers.user_id = ?",session["user_id"])[0]["COUNT(*)"])
    user_data["score"] = 10*(upvote_count-downvote_count)

    question_count = int(db.execute("SELECT COUNT(*) FROM questions WHERE user_id = ?",session["user_id"])[0]["COUNT(*)"])
    user_data["question_count"] = question_count

    answer_count = int(db.execute("SELECT COUNT(*) FROM answers WHERE user_id = ?",session["user_id"])[0]["COUNT(*)"])
    user_data["answer_count"] = answer_count

    return render_template("account.html", user_data=user_data)


@app.route('/ask_question', methods=['GET', 'POST'])
@login_required
def ask_question():
    if request.method == "POST":
        # try:
        book_id = request.args.get("book_id")
        chapter_number = request.form.get("chapter_number")
        if chapter_number != '':
            try:
                chapter_number = int(chapter_number)
            except ValueError:
                return apology("Chapter number must be an integer")
        else:
            chapter_number = None

        question = request.form.get("question")
        
        if len(question) > 0:
            print(book_id)
            print(chapter_number)
            print(question)

            db.execute("INSERT INTO questions VALUES(NULL, ?, ?, ?, ?, ?)",
                    book_id, chapter_number, question, datetime.now() ,session["user_id"])

            return redirect("/")
        
        else:
            return apology("Please enter your question")

    else:
        book_id = request.args.get("book_id")
        book_data = request_book_data(book_id)
        return render_template("ask_question.html", book=book_data)

@app.route('/answer_question', methods=['GET', 'POST'])
@login_required
def answer_question(mine = False):
    if request.method == "POST":
        question_id = request.args.get("question_id")
        answer = request.form.get("answer")
        print("Answer:", answer)
        db.execute("INSERT INTO answers VALUES (NULL, ?, ?, ?, ?)",
                   question_id, answer, datetime.now() , session["user_id"])

        return redirect(f"/answer_question?question_id={question_id}")

    else:
        question_id = request.args.get("question_id")
        print("Question ID:", question_id)
        question = db.execute(
            "SELECT * FROM questions WHERE id = ?", question_id)[0]
        book_data = request_book_data(question['book_id'])
        question["book_name"] = book_data["name"]
        question["book_image_url"] = book_data["image_url"]
        question["username"] = db.execute(
            "SELECT username FROM users WHERE id = ?", question["user_id"])[0]["username"]

        answers = db.execute(
            "SELECT * FROM answers WHERE question_id = ?", question_id)

        for answer in answers:
            answer["username"] = db.execute(
                "SELECT username FROM users WHERE id = ?", answer["user_id"])[0]["username"]
            answer["upvotes"] = (db.execute("SELECT voter_id FROM votes WHERE answer_id = ? AND positive = TRUE", answer["id"]))
            answer["downvotes"] = (db.execute("SELECT voter_id FROM votes WHERE answer_id = ? AND positive = FALSE", answer["id"]))

        return render_template("answer_question.html", question=question, answers=sort_by_scrore(answers))

@app.route('/my_answers')
@login_required
def my_answers():
    answers = db.execute(
            "SELECT *, ((SELECT COUNT(*) FROM votes WHERE votes.answer_id = answers.ID AND votes.positive = TRUE)-(SELECT COUNT(*) FROM votes WHERE votes.answer_id = answers.ID AND votes.positive = FALSE)) AS score FROM answers WHERE user_id = ? ORDER BY score DESC", session["user_id"])
    questions = []
    for answer in answers:
        if answer['question_id'] in [question['id'] for question in questions]: # + Idea from https://stackoverflow.com/a/7271523/11120544
            question["answers"].append(answer)            
        else:
            question = db.execute(
            "SELECT * FROM questions WHERE id = ? ORDER BY date DESC", answer["question_id"])[0]
            book_data = request_book_data(question['book_id'])
            question["book_name"] = book_data["name"]
            question["book_image_url"] = book_data["image_url"]
            question["username"] = db.execute(
                "SELECT username FROM users WHERE id = ?", question["user_id"])[0]["username"]
            question["answers"] = [answer]            
            questions.append(question)

    username =  db.execute(
            "SELECT username FROM users WHERE id = ?", question["user_id"])[0]["username"]

    return render_template("my_answers.html",questions=questions,username = username)

@app.route('/upvote_answer')
@login_required
def upvote_answer():
    answer_id = request.args.get("answer_id")

    existing_upvotes_by_this_user : int = db.execute("SELECT COUNT(id) FROM votes WHERE voter_id = ? AND answer_id = ? AND positive = TRUE",session["user_id"],answer_id)[0]['COUNT(id)']

    print("EUV",existing_upvotes_by_this_user)

    if (existing_upvotes_by_this_user == 0):
        db.execute("DELETE FROM votes WHERE voter_id = ? AND answer_id = ?",session["user_id"],answer_id) # * Remove existing down(by prev condition)vote
        db.execute("INSERT INTO votes VALUES(NULL, ?, ?, TRUE)", answer_id, session["user_id"],)
    else:
        db.execute("DELETE FROM votes WHERE voter_id = ? AND answer_id = ?",session["user_id"],answer_id) # * Remove existing uppvote


    return redirect(request.referrer)

@app.route('/downvote_answer')
@login_required
def downvote_answer():
    answer_id = request.args.get("answer_id")

    existing_downvotes_by_this_user : int = db.execute("SELECT COUNT(id) FROM votes WHERE voter_id = ? AND answer_id = ? AND positive = FALSE",session["user_id"],answer_id)[0]['COUNT(id)']

    print("EDV",existing_downvotes_by_this_user)

    if (existing_downvotes_by_this_user == 0):
        db.execute("DELETE FROM votes WHERE voter_id = ? AND answer_id = ?",session["user_id"],answer_id) # * Remove existing up(by prev condition)votes
        db.execute("INSERT INTO votes VALUES(NULL, ?, ?, FALSE)", answer_id, session["user_id"],)
    else:
        db.execute("DELETE FROM votes WHERE voter_id = ? AND answer_id = ?",session["user_id"],answer_id) # * Remove existing downvotes
         

    return redirect(request.referrer)


@app.route('/search_books', methods=['GET', 'POST'])
@login_required
def search_books():
    print("Searching Books")
    if request.method == "POST":
        query = request.form.get("query")

        book_list = request_book_list(query)

        print("Length:", len(book_list))

        return render_template("search_books.html", books=book_list, query=query)

    else:
        return render_template("search_books.html")
