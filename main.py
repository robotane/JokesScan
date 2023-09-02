import pathlib
import re
import sqlite3


# Regex to match a section title. It's in the format 123.[T] Section title
section_title_re = re.compile("([0-9]+).\[T]")

# Regex to match a joke title. It's in the format 123.[I] Joke title
joke_title_re = re.compile("([0-9]+).\[I]")

# Create jokes table
sql_create_jokes_table = """ CREATE TABLE IF NOT EXISTS joke 
                        (id integer PRIMARY KEY, title TEXT NOT NULL, 
                        category TEXT, content TEXT ); """

# Insert jokes to the database
sql_insert_joke_query = """INSERT INTO joke (title, category, content) VALUES (?, ?, ?);"""

# Path of the database file
db_file_path = pathlib.Path("jokes.db")
# Remove the database file if it was already been created (overwrite it)
db_file_path.unlink(missing_ok=True)

# Process the jokes.txt file
with open("jokes.txt") as jokes_f:
    # Initialise variables
    joke = ""
    title = ""
    category = ""
    old_title = ""
    jokes = [] # We will save tuple of (title, category, content) jokes here
    can_save = False
    # Retrieving all the lines of the file
    lines = jokes_f.readlines()
    N = len(lines)-1
    skiped_section = 0
    skiped_title = 0
    last_category = "Contrepétries"
    for index, line in enumerate(lines):
        # Skip empty lines
        if not line.strip():
            continue

        # Checking the content of the line
        if section_title_re.match(line): # Check if the line is a section title
            # Here we use a temp variable to not overwrite a section title with an empty string
            section_tmp = section_title_re.sub("", line).strip()
            
            if not section_tmp:
                skiped_section += 1
                continue
            # Strip the line before
            new_category = section_tmp.replace("…", "...").strip()
            new_category = " / ".join([c.strip() for c in new_category.split("/")])
            
            # The last category case
            if new_category == last_category:
                can_save = True
            
            # While the joke is being filled, we don't change the category
            # So, we change the category title only if the joke content is empty
            if not joke:
                category = new_category
        elif joke_title_re.match(line): # Check if the line is a joke title
            # Skip empty titles
            if not joke_title_re.sub("", line).strip():
                skiped_title += 1
                continue
            # Backup the old title, and save the new one
            old_title = title
            title = joke_title_re.sub("", line).strip()
            
            # If we have got a new joke title and the current joke content is not empty, 
            # then we can save this content with the old_title title
            can_save = bool(joke)
        else: # If the line is not a section title or a joke title, then it's a joke content
            joke += line

        # When we are the end of the file, we can automatically save the joke
        # As the last category doesn't have a title, we use its category as title
        if index == N:
            old_title = category
            can_save = True

        # Saving the joke
        if can_save:
            # Striping and refactoring the joke content and category
            old_title = old_title.replace("…", "...")#.replace(":", "").replace("..", "").replace(".", "")
            category = category[0].upper() + category[1:]
            
            # We save the tuple (title, category, joke) in the list
            jokes.append((old_title.strip(), category, joke.strip()))
            
            # We then update the category and title because saving is triggered by getting
            # new category or new title
            category = new_category
            old_title = title
            
            # Resetting can_save and joke content variables
            can_save = False
            joke = ""


# Saving data to the database
with sqlite3.connect(db_file_path) as con:
    cur = con.cursor()
    # Creating the table
    cur.execute(sql_create_jokes_table)

    # Inserting the datas to the database using the list of tuple
    cur.executemany(sql_insert_joke_query, jokes)

