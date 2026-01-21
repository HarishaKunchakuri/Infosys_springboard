from flask import Flask, render_template, request
import json
import string

app = Flask(__name__)

# -----------------------------
# LOAD INDEX
# -----------------------------
with open("../indexer/inverted_index.json", "r", encoding="utf-8") as f:
    inverted_index = json.load(f)

with open("../indexer/idf.json", "r", encoding="utf-8") as f:
    idf = json.load(f)

# -----------------------------
# TOKENIZE QUERY
# -----------------------------
def tokenize(text):
    text = text.lower()
    translator = str.maketrans("", "", string.punctuation)
    text = text.translate(translator)
    return text.split()

# -----------------------------
# SEARCH
# -----------------------------
def search(query, top_k=5):
    scores = {}
    tokens = tokenize(query)
    found = False

    for word in tokens:
        if word not in inverted_index:
            continue

        found = True

        for doc_id, tf in inverted_index[word]:
            score = tf * idf.get(word, 0)
            scores[doc_id] = scores.get(doc_id, 0) + score

    if not found or not scores:
        return None

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

# -----------------------------
# ROUTE
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    query = ""
    results = None
    no_results = False

    if request.method == "POST":
        query = request.form.get("query")
        results = search(query)

        if results is None:
            no_results = True

    return render_template(
        "index.html",
        query=query,
        results=results,
        no_results=no_results
    )

if __name__ == "__main__":
    app.run(debug=True)
