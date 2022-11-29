import streamlit as st

from router import router, args
from utils import query_db, exec_db
from login import login_required

def add_book(isbn, title, subtitle, description, publisher, category, authors, storage):
    if not isbn or not title or not subtitle or not description or not publisher or not category or not authors or not storage:
        st.warning("Missing required fields.")
        return

    exec_db(f"""INSERT INTO books (isbn, title, subtitle, description, publisher_name) 
            VALUES ('{isbn}', '{title}', '{subtitle}', '{description}', '{publisher}') 
            ON CONFLICT (isbn) 
            DO UPDATE SET
            title = EXCLUDED.title, 
            subtitle = EXCLUDED.subtitle, 
            description = EXCLUDED.description, 
            publisher_name = EXCLUDED.publisher_name;""")

    exec_db(f"INSERT INTO books_categories_rel (isbn, category_name) VALUES ('{isbn}', '{category}') ON CONFLICT (isbn, category_name) DO NOTHING;")
    authors_list = [x.strip() for x in authors.split(';')]
    storage_list = [x.strip() for x in storage.split(';')]

    for author in authors_list:
        author_info_list = author.split(',')
        author_name = author_info_list[0].strip()
        author_first_name = author_name.split('·')[0].strip()
        author_last_name = author_name.split('·')[1].strip()
        author_id = author_info_list[1].strip()
        author_dob = author_info_list[2].strip()
        exec_db(f"""INSERT INTO authors (aid, first_name, last_name, dob) 
                    VALUES ('{author_id}', '{author_first_name}', '{author_last_name}', '{author_dob}') 
                    ON CONFLICT (aid) 
                    DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    dob = EXCLUDED.dob;""")
        exec_db(f"INSERT INTO books_authors_rel (isbn, aid) VALUES ('{isbn}', '{author_id}') ON CONFLICT (isbn, aid) DO NOTHING;")

    for record in storage_list:
        storage_info_list = record.split(',')
        lid = storage_info_list[0].strip()
        location = storage_info_list[1].strip()
        num_books = storage_info_list[2].strip()
        exec_db(f"""INSERT INTO racks (lid, isbn, location, num_books) 
                    VALUES ('{lid}', '{isbn}', '{location}', '{num_books}') 
                    ON CONFLICT (lid, isbn, location) 
                    DO UPDATE SET 
                    num_books = EXCLUDED.num_books;""")
    st.success("🎉 Add success!")

@router(path="/admin")
@login_required
def render():
    user_ssn = st.session_state["logined_user"]
    user_first_name = st.session_state["logined_user_username"]
    user_role = st.session_state["logined_user_role"]
    title = "# 🎓 Hello " + str(user_first_name)
    st.markdown(title)

    "## Manager options"
    st.markdown("# 🔧 Manager Options")
    if user_role == 0:
        st.markdown("### ➕ Add book")

        new_book_isbn = st.text_input(
            "Enter book isbn 👇",
            placeholder="isbn of the book",
        )

        new_book_title = st.text_input(
            "Enter book title 👇",
            placeholder = "title of the book",
        )

        new_book_subtitle = st.text_input(
            "Enter book subtitle 👇",
            placeholder="subtitle of the book",
        )

        new_book_description = st.text_input(
            "Enter book description 👇",
            placeholder="description of the book",
        )

        new_book_publisher_name = st.text_input(
            "Enter book publisher 👇",
            placeholder="publisher of the book",
        )

        new_book_category_name = st.text_input(
            "Enter book category 👇",
            placeholder="category of the book",
        )

        new_book_authors = st.text_input(
            "Enter book authors(firstname · lastname, author id, dob) seperated by ';' 👇",
            placeholder="ex: firstname1 · lastname1, OL164002A, 1989-05-31; firstname2 · lastname2, OL356641A, 1778-07-01",
        )

        new_book_storage = st.text_input(
            "Enter book storage(library id, rack id, amount) seperated by ';' 👇",
            placeholder="ex: L2, YA32, 3; L1, ZY47, 1",
        )

        st.button('Add book', type="primary", on_click=lambda: add_book(new_book_isbn, new_book_title, new_book_subtitle, new_book_description, new_book_publisher_name, new_book_category_name, new_book_authors, new_book_storage))

    else:
        st.error("You are not a manager.")
