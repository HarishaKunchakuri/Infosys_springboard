import os
import math
import string
import json
from bs4 import BeautifulSoup

# -----------------------------
# CONFIG
# -----------------------------
PAGES_DIR = "../pages"
INDEX_FILE = "inverted_index.json"
IDF_FILE = "idf.json"

# -----------------------------
# HTML → TEXT
# -----------------------------
def extract_text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return soup.get_text(separator=" ")

# -----------------------------
# TOKENIZE
# -----------------------------
def tokenize(text):
    text = text.lower()
    translator = str.maketrans("", "", string.punctuation)
    text = text.translate(translator)
    return text.split()

# -----------------------------
# LOAD DOCUMENTS
# -----------------------------
def load_documents():
    docs = {}
    for file in os.listdir(PAGES_DIR):
        if file.endswith(".html"):
            with open(os.path.join(PAGES_DIR, file), "r", encoding="utf-8") as f:
                docs[file] = f.read()
    return docs

# -----------------------------
# TERM FREQUENCY
# -----------------------------
def compute_tf(tokens):
    tf = {}
    for word in tokens:
        tf[word] = tf.get(word, 0) + 1
    return tf

# -----------------------------
# BUILD INVERTED INDEX
# -----------------------------
def build_inverted_index(documents):
    inverted_index = {}

    for doc_id, html in documents.items():
        text = extract_text_from_html(html)
        tokens = tokenize(text)
        tf = compute_tf(tokens)

        for word, freq in tf.items():
            inverted_index.setdefault(word, []).append([doc_id, freq])

    return inverted_index

# -----------------------------
# IDF
# -----------------------------
def compute_idf(inverted_index, total_docs):
    idf = {}
    for word, postings in inverted_index.items():
        idf[word] = math.log(total_docs / len(postings))
    return idf

# -----------------------------
# SAVE
# -----------------------------
def save_to_disk(index, idf):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)

    with open(IDF_FILE, "w", encoding="utf-8") as f:
        json.dump(idf, f, indent=2)

# -----------------------------
# MAIN
# -----------------------------
def main():
    print("[INFO] Loading documents...")
    docs = load_documents()
    print(f"[INFO] Total documents: {len(docs)}")

    print("[INFO] Building inverted index...")
    inverted_index = build_inverted_index(docs)

    print("[INFO] Computing IDF...")
    idf = compute_idf(inverted_index, len(docs))

    print("[INFO] Saving index to disk...")
    save_to_disk(inverted_index, idf)

    print("[DONE] Milestone 3 completed successfully!")

if __name__ == "__main__":
    main()
