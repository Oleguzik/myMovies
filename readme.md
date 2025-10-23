# 🎬 myMovies

The **myMovies** is a Python-based tool that allows you to explore and render a visual movie catalog by pulling movie data from a local SQLite database and generating an HTML movie gallery. 

---

## 📌 Project Description

This app lets you load movies from a local database and visually present them in a styled HTML file. Movie information such as title, release year, IMDb rating, and poster URL is displayed in a responsive grid layout using a template system.

---

## 🧩 Features

- Query or load movie data from a local database (`movies.db`)
- HTML movie grid generation triggered by menu option 11
- Custom HTML template with placeholders
- Built-in CSS styling for visual layout
- Modular code structure for data access and external API

---

## 🚀 How to Use

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Dependencies

Create a `.env` file in the root directory and add your API key:

```env
API_KEY='your_api_key_here'
```

### 3. Run the App

From the root of the project:

```bash
python movies.py
```

You will be presented with a menu. Select option `8` to generate the HTML movie gallery.

### 4. View the Output

Open the generated `index.html` in your browser to view the movie showcase.

---

## 🗂️ Project Structure

```
Movies_Project/
├── .env                       # Your api key
├── movies.py                  # Main script with menu and logic
├── index.html                 # Generated HTML (output)
│
├── data/
│   ├── movie_storage_sql.py   # Handles database operations
│   └── movies.db              # SQLite database with movie data
│
├── static/
│   ├── index_template.html    # HTML template with placeholders
│   └── style.css              # CSS styling
│
├── requirements.txt
├── README.md
└── LICENSE
```

---

## 🛠️ Technologies Used

| Purpose              | Library             |
|----------------------|---------------------|
| Database ORM         | `SQLAlchemy`        |
| API Requests         | `requests`          |
| Fuzzy Search Matching| `fuzzywuzzy`        |
| HTML Generation      | Template injection  |


---

## 📄 License

Licensed under the MIT License (./LICENSE)