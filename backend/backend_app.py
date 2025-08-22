from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL="/api/docs"  # (1) swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL="/static/masterblog.json" # (2) ensure you create this dir and file

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API' # (3) You can change this if you like
    }
)

app = Flask(__name__)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(POSTS)


@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()

    # Error Handling
    if not data or "title" not in data or "content" not in data:
        return jsonify({"error": "Missing title or content"}), 400

    # create new ID
    new_id = len(POSTS) + 1

    new_post = {
        "id": new_id,
        "title": data["title"],
        "content": data["content"]
    }

    POSTS.append(new_post)

    return jsonify(new_post), 201

@app.route('/api/posts/<id>', methods=['DELETE'])
def delete_post(id):
    for post in POSTS:
        if str(post.get("id")) == id:
            POSTS.remove(post)
            return jsonify({"message": f"Post with id {id} has been deleted successfully."}), 200
    return jsonify({"error": "Post not found"}), 400


@app.route('/api/posts/<id>', methods=['PUT'])
def update_post(id):
    data = request.get_json()
    for post in POSTS:
        if str(post.get("id")) == id:
            if "title" in data and data["title"] is not None:
                post["title"] = data["title"]
            if "content" in data and data["content"] is not None:
                post["content"] = data["content"]
            return jsonify({
                "id": post["id"],
                "title": post["title"],
                "content": post["content"]
            }), 200

    return jsonify({"error": "Post not found"}), 404


@app.route('/api/posts/search', methods=['GET'])
def search_post():
    title_query = request.args.get("title")
    content_query = request.args.get("content")

    results = []

    for post in POSTS:
        title_match = title_query and title_query.lower() in post["title"].lower()
        content_match = content_query and content_query.lower() in post["content"].lower()

        if title_match or content_match:
            results.append(post)

    return jsonify(results), 200


@app.route('/api/posts', methods=['GET'])
def list_posts():
    sort_field = request.args.get("sort")
    direction = request.args.get("direction")

    # validation
    if sort_field and sort_field not in ["title", "content"]:
        return jsonify({"error": "Invalid sort field. Must be 'title' or 'content'."}), 400
    if direction and direction not in ["asc", "desc"]:
        return jsonify({"error": "Invalid direction. Must be 'asc' or 'desc'."}), 400

    # sorting
    if sort_field:
        reverse = direction == "desc"
        posts = sorted(POSTS, key=lambda x: x[sort_field].lower(), reverse=reverse)
    else:
        posts = POSTS

    return jsonify(posts), 200



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
