import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

import calendar


def request_book_list(query):  # + Code adapted from pset9: C$50 finance

    query = urllib.parse.quote(query)

    # Contact API
    print("Contacting API...")
    try:
        print("Getting book list")
        api_key = os.environ.get("API_KEY")
        url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{query}&orderBy=relevance&key={api_key}"
        print("URL:")
        print(url)

        response = requests.get(url)

        response.raise_for_status()
    except requests.RequestException:
        print (requests.RequestException)
        return None

    # Parse response
    book_list = []
    # try:

    # if (response.json())["error"]:
    #     return apology(response.json()["error"]["message"])

    data_list = response.json()["items"]
    # print(data_list)
    for item in data_list:
        mapped_book = map_book_json(item)

        if (mapped_book):
            book_list.append(mapped_book)

    return book_list
    # except (KeyError, TypeError, ValueError):
    #     return None


def request_book_data(book_id):
    # Contact API
    print("Contacting API...")
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://www.googleapis.com/books/v1/volumes/{book_id}?key={api_key}"
        print("URL:")
        print(url)

        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        print("Exception")
        print(requests.RequestException)
        return None

    print("Response")
    print(response.json())
    return map_book_json(response.json())


def map_book_json(book_json):
    data = book_json["volumeInfo"]
    if "authors" in data.keys():
        book = {
            "id": book_json["id"],
            "name": data["title"],
            "author_names": data["authors"],
            "preview_url" : data["previewLink"],
        }

        if "imageLinks" in data.keys():
            book["image_url"] = data["imageLinks"]["thumbnail"]
        if "pageCount" in data.keys():
            book["pages_count"] = int(data["pageCount"])

        return book

    else:
        return False


def apology(message: str):
    return render_template("apology.html", message = message)


def login_required(f):  # + Code from distribution code of C$50 finance
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def score(answer):
    return len(answer["upvotes"]) - len(answer["downvotes"])


def sort_by_scrore(answers):
    sorted = False
    while not sorted:
        sorted = True
        for i in range(0, len(answers) - 1):
            if score(answers[i]) < score(answers[i+1]):
                sorted = False
                answers[i], answers[i+1] = answers[i+1], answers[i]
    return answers

def universal_date(value):
    return f"{value[8:10]} {calendar.month_abbr[int(value[5:7])]} {value[0:4]}"