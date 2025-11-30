# TBR Whisperer – Mood‑Based Reading Assistant

TBR Whisperer is a small, end‑to‑end project that helps readers pick a single book from their unread shelf based on their current mood. It combines:

- A conversational, chat‑style UI built in Framer.  
- A Flask API deployed on Render that serves mood‑filtered book recommendations from a CSV.  
- A simple, ADHD‑friendly interaction pattern: pick a vibe → get one clear suggestion.

Live prototype: `https://tbrwhisperer.framer.website/`  

***

## 1. Problem & Goals

### 1.1 Problem

Readers with large “To Be Read” (TBR) piles often experience:

- Decision fatigue when choosing the next book.  
- Guilt or overwhelm when scrolling through long lists.  
- Difficulty matching a book’s energy to their current mental state.

Traditional recommendation UIs (carousels, long lists) make this worse. The user problem:  

> “I want someone to just tell me one book that fits how my brain feels right now.”

### 1.2 Project Goals

- **Reduce decision fatigue** by offering only one book at a time.  
- **Anchor selection to mood/energy**, not genre or rating.  
- **Ship a real, working prototype** that connects a custom backend to a designed UI.  
- **Keep the flow ADHD‑friendly**: low cognitive load, minimal options, no complex onboarding.

***

## 2. System Overview

The system has two main parts:

1. **Backend API (Flask on Render)**  
   - Loads a CSV of books with metadata.  
   - Exposes two HTTP endpoints:
     - `/random` – one random book from the full set.  
     - `/mood?tag=XYZ` – one random book filtered by `mood_tag=XYZ`.

2. **Frontend UI (Framer)**  
   - A chat‑style layout based on a Textfolio template.  
   - Mood choices presented as “chips” in the conversation (“Soft & Slow”, “Deep‑dive grind”, “Chaos & fun”, “Big thinky brain”).  
   - A “RecBubble” component that fetches data from the API and renders:
     - Book title  
     - Author  
     - Short notes describing the vibe

The current v1 prototype wires the **Soft & Slow** mood to a live API call and shows **static examples** for the other moods.

***

## 3. Data Model

The project uses a `books.csv` file as a lightweight database. Expected columns:

- `title` – book title (string)  
- `author` – author name (string)  
- `genre` – broad genre label (string)  
- `mood_tag` – one of: `soft_slow`, `deep_dive`, `chaos_fun`, `thinky`  
- `energy` – qualitative energy level (e.g., “low”, “medium”, “high”)  
- `notes` – short free‑text description focusing on vibe / why it fits that mood

The backend normalizes column names to lowercase and validates that all required columns exist.  

***

## 4. Backend – Flask API

### 4.1 Dependencies

Defined in `requirements.txt`:

- `Flask` – web framework  
- `flask-cors` – to allow Framer / browser access from another origin  
- `pandas` – CSV loading and random sampling  
- `gunicorn` – production WSGI server  
- Supporting libs: `numpy`, `Werkzeug`, etc.

### 4.2 Application Structure

Single‑file app (`app.py`) for simplicity:

```python
from flask import Flask, jsonify, request
import pandas as pd
from flask_cors import CORS

CSV_PATH = "books.csv"

app = Flask(__name__)
CORS(app)  # enable cross-origin requests for the frontend

def load_books():
    df = pd.read_csv(CSV_PATH)
    df.columns = [c.strip().lower() for c in df.columns]  # normalize
    required_cols = {"title", "author", "genre", "mood_tag", "energy", "notes"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")
    return df

BOOKS_DF = load_books()
```

Utility functions:

- `pick_random(df)` – returns one random row or `None` if empty.  
- `pick_by_mood(df, mood_tag)` – filters by `mood_tag`, returns one random row or `None`.

### 4.3 Endpoints

#### 4.3.1 Health Check

- **Route:** `/`  
- **Method:** `GET`  
- **Purpose:** simple status check.

**Response example:**

```json
{ "status": "ok" }
```

#### 4.3.2 `/random`

- **Route:** `/random`  
- **Method:** `GET`  
- **Description:** returns one random book from the entire dataset.

**Success (200) response:**

```json
{
  "title": "...",
  "author": "...",
  "genre": "...",
  "mood": "...",
  "energy": "...",
  "notes": "..."
}
```

**Error (404):**

```json
{ "error": "no_books" }
```

#### 4.3.3 `/mood`

- **Route:** `/mood`  
- **Method:** `GET`  
- **Query param:** `tag` – mood tag string, e.g., `soft_slow`, `deep_dive`, `chaos_fun`, `thinky`.  
- **Description:** filters the DataFrame by `mood_tag` and returns one random book.

**Success (200):**

```json
{
  "title": "...",
  "author": "...",
  "genre": "...",
  "mood": "soft_slow",
  "energy": "...",
  "notes": "..."
}
```

**Error (400):** no tag provided

```json
{ "error": "missing_tag_param" }
```

**Error (404):** no books for that mood

```json
{ "error": "no_books_for_mood" }
```

### 4.4 Deployment (Render)

- Connected the GitHub repo containing `app.py`, `books.csv`, and `requirements.txt` to a **Render Web Service**.  
- `gunicorn` is used as the start command, for example:

  ```bash
  gunicorn app:app
  ```

- Render builds the environment from `requirements.txt`.  
- `flask-cors` fixed browser “Failed to fetch” / CORS errors between Framer and the API.

***

## 5. Frontend – Framer Prototype

### 5.1 Layout

The prototype is built on top of a Textfolio‑style messaging layout:

- **Header:**  
  - TBR Whisperer identity card (avatar + “ADHD‑friendly reading assistant”).  
  - Location (“Mumbai”).  
  - Time label (e.g., “Today · 20:35”).

- **Conversation flow:**  
  - Intro message explaining what TBR Whisperer does.  
  - User bubble: “Okay, cool. How do we do this?”  
  - Bot explains: “Tell me the vibe and I’ll pull one book from your unread stack.”  
  - Mood options as stacked grey “chips”:
    - 😴 Soft & Slow  
    - ⚡ Deep‑dive grind  
    - 😂 Chaos & fun  
    - 💭 Big thinky brain

- **Recommendation section:**  
  - A “Soft & Slow pick for you today →” label.  
  - A RecBubble showing title, author, and notes for one **soft_slow** book (live from the API).  
  - Optional static RecBubbles further down showing example picks for other moods.

### 5.2 RecBubble Component

RecBubble is a reusable card with three text layers:

- `Book title`  
- `Author name`  
- `Short, cozy, low‑energy read` (or other notes text)

Inside Framer:

1. The card is turned into a Component (`RecBubble`).  
2. A text variable `moodTag` was initially used; for v1 the main live instance is hard‑coded to `soft_slow` for reliability.  
3. Each text uses **Fetch**:

   - URL:

     `https://tbr-whisperer-api.onrender.com/mood?tag=soft_slow`

   - `Book title` – Path `title`  
   - `Author name` – Path `author`  
   - Notes line – Path `notes`

Framer’s Fetch automatically binds the JSON fields to the text, so every page load shows a real book from the backend rather than dummy copy.

### 5.3 Static Examples for Other Moods

To avoid complexity with component variables in the Textfolio template:

- The live `RecBubble_Main` remains connected to the API for `soft_slow`.  
- For other moods:
  - The RecBubble is duplicated and **detached** from the component.  
  - The Fetch URL is temporarily pointed at another tag (e.g., `tag=deep_dive`) to load real data once.  
  - The text is then converted to static copy so the example remains stable.

Each example is labeled, e.g.:

- “If you tap Deep‑dive grind → example result:”  
- “If you tap Chaos & fun → example result:”

This demonstrates the intended behavior without fighting the constraints of the template’s interaction system.

***

## 6. Interaction Model

### 6.1 Current v1

- Mood chips are **visual**, not wired to runtime state in this Textfolio file.  
- The user scrolls through the chat and sees:
  - The question asking for their vibe.  
  - The four moods.  
  - A concrete example of the resulting Soft & Slow recommendation (live).  
  - Additional example states for other moods (static but sourced from real API data at design time).

This is sufficient to communicate:

- The mental model: mood → one book.  
- That the assistant is backed by a working backend, not hard‑coded lorem ipsum.

### 6.2 Planned v2 Interactions

In a next iteration (likely in a dedicated Framer project rather than a template):

- Each mood chip will:
  - Use **Set Property** to update `moodTag` on `RecBubble_Main`.  
  - Use **Scroll To** to bring the recommendation bubble into view.  
- A **“Show another”** button will:
  - Toggle a `refreshKey` variable on the RecBubble instance.  
  - Append `&refresh=:refreshKey` to the Fetch URL so each click re‑fetches a new random book for the same mood.

This would turn the UI into a true, interactive “Tinder for TBR” experience.

***

## 7. Usage & Setup (For Local Development)

### 7.1 Prerequisites

- Python 3.10+  
- `pip`  
- A `books.csv` file matching the schema above.

### 7.2 Setup Steps

1. **Clone the repo**

   ```bash
   git clone <your-repo-url>
   cd <your-repo-folder>
   ```

2. **Create and activate a virtual environment (optional but recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS / Linux
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run locally**

   ```bash
   python app.py
   ```

   - The API will be available at `http://127.0.0.1:5000/`.  
   - Test:

     - `http://127.0.0.1:5000/` → `{"status": "ok"}`  
     - `http://127.0.0.1:5000/random`  
     - `http://127.0.0.1:5000/mood?tag=soft_slow`

5. **Point Framer at local API (optional for dev)**

   - Replace the Fetch URL in Framer with your local URL, e.g.:  
     `http://127.0.0.1:5000/mood?tag=soft_slow`  
   - Switch back to the Render URL when deploying.

***

## 8. Constraints & Trade‑Offs

- **Template limitations:**  
  The Textfolio template nests elements in ways that make Framer’s Interactions and component variables harder to use. That’s why v1 chooses:
  - One fully live RecBubble for Soft & Slow.  
  - Static but accurate examples for other moods.

- **CORS / “Failed to fetch” issues:**  
  Solved by:
  - Adding `flask-cors` to `requirements.txt`.  
  - Calling `CORS(app)` in `app.py`.

- **Simplicity over full feature parity:**  
  Instead of building a complex state machine inside Framer on day one, the project prioritizes:
  - Clear storytelling.  
  - A real backend.  
  - One solid, working end‑to‑end path.

***

## 9. Roadmap / Future Improvements

- **Full mood → RecBubble interaction**  
  Move to a simpler Framer canvas (non‑template) and:
  - Wire mood chips to `moodTag`.  
  - Add scroll + selection states (highlight active mood).

- **Refresh button**  
  Implement the `refreshKey` pattern to allow multiple random picks for the same mood without reloading.

- **Swipe‑style “TBR Tinder” view**  
  Add a second page where:
  - User selects mood once.  
  - Swipes or taps “Next” to cycle through options for that mood.  
  - Optionally marks a book as “Read / Skip / Add to next”.

- **User persistence**  
  Store chosen books in local storage or a lightweight DB so the assistant doesn’t resurface the same recommendation repeatedly.

- **Accessibility & microcopy**  
  - Refine color contrast, focus states, and keyboard navigation.  
  - Polish the ADHD‑friendly microcopy and explainers.

***

## 10. How to Present This Project (PM / Portfolio Angle)

- **User problem:** decision fatigue choosing from an unread shelf.  
- **Insight:** mood and energy level matter more than genre when users are overwhelmed.  
- **Solution:** a mood‑based assistant that gives exactly one suggestion.  
- **Execution:**  
  - Designed conversational copy and mood taxonomy.  
  - Implemented a backend API and wired it into a real UI.  
  - Managed timeboxing: shipped a constrained but working v1, with clear future enhancements.

This README serves both as technical documentation and as a narrative you can translate into a case study, portfolio page, or talking points for interviews.
