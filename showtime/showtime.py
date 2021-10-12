import re

from flask import Flask, render_template, request, jsonify, make_response, url_for
import json

from typing import List

app = Flask(__name__)

PORT = 3500
LINKS = "_links"
VERB_TO_KEY = {
    'GET': 'read',
    'POST': 'create',
    'DELETE': 'remove',
    'PUT': 'modify',
}
with open('../databases/movies.json', "r") as jsf:
    movies = json.load(jsf)["movies"]


# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>", 200)


# to test templates of Flask
@app.route("/template", methods=['GET'])
def template():
    return make_response(render_template('index.html', body_text='This is my HTML template for Movie service'), 200)


# get the complete json file
@app.route("/json", methods=['GET'])
def get_json():
    # res = make_response(jsonify(INFO), 200)
    res = make_response(jsonify(movies), 200)
    return res


# get a movie info by its ID
@app.route("/movies/<id>", methods=['GET'])
def get_movie_byid(id):
    for movie in movies:
        if str(movie["id"]) == str(id):
            res = make_response(jsonify(movie), 200)
            return res
    return make_response(jsonify({"error": "Movie ID not found"}), 400)


"""
Creates a new movie via POST verb
Searches through movie arrays for an id match. If a match is found, returns a 409 Conflict code
If no match is found, returns a 201 Created, as no data is generated so the output data is the same as the input data
Idea : Generate a uuid with a controller (this is routing layer), and only return the generated uuid
"""


@app.route("/movies", methods=["POST"])
def create_movie():
    req = request.get_json()
    for movie in movies:
        if str(movie["id"]) == str(req['id']):
            return make_response(jsonify({"error": "movie ID already exists"}), 409)

    movies.append(req)
    res = make_response("", 201)
    return res


"""
Deletes a movies via DELETE verb
Searches through the array looking for a match. If a match is found, return 204 No Content code
If no match is found, returns a 404 Bad Request code
"""


@app.route("/movies/<id>", methods=["DELETE"])
def del_movie(id):
    for movie in movies:
        if str(movie["id"]) == str(id):
            movies.remove(movie)
            return make_response("", 204)

    res = make_response(jsonify({"error": "movie ID not found"}), 404)
    return res


# get a movie info by its name
# through a query
@app.route("/movies", methods=['GET'])
def get_movie_bytitle():
    array = []
    if request.args:
        req = request.args
        for movie in movies:
            if str(req["title"]) in str(movie["title"]):
                array.append(movie)

    if not array:
        res = make_response(jsonify({"error": "movie title not found"}), 400)
    else:
        res = make_response(jsonify(array), 200)
    return res


# change a movie rating
@app.route("/movies/<id>", methods=["PATCH"])
def partial_update_movie_rating(id, rate):
    for movie in movies:
        if str(movie["id"]) == str(id):
            movie["rating"] = int(rate)
            res = make_response(jsonify(movie), 200)
            return res

    res = make_response(jsonify({"error": "movie ID not found"}), 201)
    return res


# change a movie rating
@app.route("/movies/<id>", methods=["PUT"])
def update_movie_rating(id, rate, director, title):
    for movie in movies:
        if str(movie["id"]) == str(id):
            movie["rating"] = int(rate)
            movie[""]
            res = make_response(jsonify(movie), 200)
            return res

    res = make_response(jsonify({"error": "movie ID not found"}), 201)
    return res


@app.after_request
def add_next_routes(response):
    json_object = response.get_json()
    if type(json_object) is dict:
        url_tuples = []
        for rule in app.url_map.iter_rules():
            options = {}
            for arg in rule.arguments:
                options[arg] = "[{0}]".format(arg)
            url_tuples.append(
                (url_for(rule.endpoint, **options).replace("%5B", "<").replace("%5D", ">"),
                 list(set(VERB_TO_KEY.keys()).intersection(rule.methods)))
            )
        json_object[LINKS] = lookup_next_routes_regex(url_tuples, str(request.url_rule))
        response.data = json.dumps(json_object)
    return response


def lookup_next_routes_regex(tuples: List[tuple], base_url: str):
    base_url = base_url.strip("/") + "(/[aA-zZ]*/?)?"
    map_urls = {}
    for cur_tuple in tuples:
        if re.search(base_url, cur_tuple[0]):
            for verb in cur_tuple[1]:
                map_urls[VERB_TO_KEY[verb]] = cur_tuple[0]
    return map_urls


if __name__ == "__main__":
    print("Server running in port %s" % PORT)
    app.run(host="localhost", port=PORT)
