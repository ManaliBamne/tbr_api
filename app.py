from flask import Flask, jsonify, request
import pandas as pd


from flask import Flask
from flask_cors import CORS


CSV_PATH = "books.csv"

app = Flask(__name__)
CORS(app)

def load_books():
    df = pd.read_csv(CSV_PATH)
    # normalize column names
    df.columns = [c.strip().lower() for c in df.columns]
    required_cols = {"title", "author", "genre", "mood_tag", "energy", "notes"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")
    return df

BOOKS_DF = load_books()

def pick_random(df):
    if df.empty:
        return None
    return df.sample(1).iloc[0]

def pick_by_mood(df, mood_tag):
    subset = df[df["mood_tag"].astype(str).str.lower() == mood_tag.lower()]
    if subset.empty:
        return None
    return subset.sample(1).iloc[0]

@app.route("/")
def health():
    return jsonify({"status": "ok"})

@app.route("/random", methods=["GET"])
def random_book():
    book = pick_random(BOOKS_DF)
    if book is None:
        return jsonify({"error": "no_books"}), 404
    return jsonify({
        "title": book["title"],
        "author": book["author"],
        "genre": book["genre"],
        "mood": book["mood_tag"],
        "energy": book["energy"],
        "notes": book["notes"]
    })

@app.route("/mood", methods=["GET"])
def mood_book():
    mood = request.args.get("tag")
    if not mood:
        return jsonify({"error": "missing_tag_param"}), 400
    book = pick_by_mood(BOOKS_DF, mood)
    if book is None:
        return jsonify({"error": "no_books_for_mood"}), 404
    return jsonify({
        "title": book["title"],
        "author": book["author"],
        "genre": book["genre"],
        "mood": book["mood_tag"],
        "energy": book["energy"],
        "notes": book["notes"]
    })

if __name__ == "__main__":
    app.run(debug=True)
