import pathlib
import re
import sqlite3

section_title_re = re.compile("([0-9]+).\[T]")
joke_title_re = re.compile("([0-9]+).\[I]")

sql_create_jokes_table = """ CREATE TABLE IF NOT EXISTS joke 
                        (id integer PRIMARY KEY, title TEXT NOT NULL, 
                        category TEXT, content TEXT ); """

sql_insert_joke_query = """INSERT INTO joke (title, category, content) VALUES (?, ?, ?);"""

db_file_path = pathlib.Path("jokes.db")
db_file_path.unlink(missing_ok=True)

with open("jokes.txt") as jokes_f:
    joke = ""
    title = ""
    category = ""
    old_category = ""
    jokes = []
    for line in jokes_f:
        if not line.strip():
            continue

        if section_title_re.match(line):
            section_tmp = section_title_re.sub("", line).strip()
            if not section_tmp:
                continue
            new_category = section_tmp.replace("…", " ").strip()
            new_category = " / ".join([c.strip() for c in new_category.split("/")])
            if not joke:
                category = new_category
        elif joke_title_re.match(line):
            if joke:
                title = title.replace("…", "").replace(":", "").replace("..", "").replace(".", "").replace("...", "")
                category = category[0].upper() + category[1:]
                jokes.append((title.strip(), category, joke.strip()))
                category = new_category
            joke = ""
            title = joke_title_re.sub("", line).strip()
        else:
            joke += line

with sqlite3.connect(db_file_path) as con:
    cur = con.cursor()
    cur.execute(sql_create_jokes_table)
    cur.executemany(sql_insert_joke_query, jokes)


