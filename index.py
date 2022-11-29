import streamlit as st

from router import router, navigate
from utils import query_db, exec_db
from login import login_required

@router(path="/")
@login_required
def render():
    role = st.session_state["logined_user_role"]
    if role == 0:
        col1, col2, col3 = st.columns(3)
        col1.button("📈 Statistics Page", on_click=navigate(path="/stats"))
        col2.button("👥 Profile Page", on_click=navigate(path="/user"))
        col3.button("🔑 Management Page", on_click=navigate(path="/admin"))
    else:
        col1, col2 = st.columns(2)
        col1.button("📈 Statistics Page", on_click=navigate(path="/stats"))
        col2.button("👥 Profile Page", on_click=navigate(path="/user"))

    st.markdown("# Welcome to library system")

    isbn_list = []
    searchBy = st.selectbox("Search By", ["Book Title", "Author Name", "ISBN"])

    if searchBy == "Book Title":
        "## Search by title tables"
        st.markdown("### 📖 Search by title")

        books = query_db(f"SELECT * FROM books;")
        try:
            all_book_titles = books["title"].tolist()
            title_selected = st.selectbox("Enter the title", all_book_titles)
        except:
            st.write("Sorry! Something went wrong with your query, please try again.")

        if title_selected:
            f"Display the table"
            try:
                books_selected = query_db(f"SELECT * FROM books WHERE title = '{title_selected}';")
                df = books_selected
                isbn_list.extend(books_selected.to_dict('records'))
                # st.dataframe(df)
            except:
                st.write(
                    "Sorry! Something went wrong with your query, please try again."
                )

    if searchBy == "Author Name":
        "## Search by title tables"
        st.markdown("### ✒️ Search by Authors")

        authors = query_db(f"SELECT * FROM authors;")
        try:
            all_author_first_names = authors["first_name"].tolist()
            all_author_last_names = authors["last_name"].tolist()
            all_author_names = []
            for i in range(len(all_author_first_names)):
                all_author_names.append(all_author_first_names[i] + " · " + all_author_last_names[i])
            author_selected = st.selectbox("Enter the author name", all_author_names)
        except:
            st.write("Sorry! Something went wrong with your query, please try again.")

        if author_selected:
            f"Display the table"
            try:
                first_name_selected = author_selected.split(" · ")[0]
                last_name_selected = author_selected.split(" · ")[1]
                all_books_selected = query_db(f"SELECT k.* FROM books_authors_rel b LEFT JOIN authors a ON b.aid = a.aid LEFT JOIN books k ON b.isbn = k.isbn WHERE a.first_name = '{first_name_selected}' AND a.last_name = '{last_name_selected}';")
                isbn_list.extend(all_books_selected.to_dict('records'))
                df = all_books_selected
                # st.dataframe(df)
            except:
                st.write(
                    "Sorry! Something went wrong with your query, please try again."
                )

    if searchBy == "ISBN":
        "## Search by isbn"
        st.markdown("### 🔍️ Search by isbn")
        isbn_entered = st.text_input(
            "Enter book isbn 👇",
            placeholder="enter isbn of the book",
        )

        if isbn_entered:
            all_books_selected = query_db(f"SELECT * FROM books WHERE isbn = '{isbn_entered}';")
            isbn_list.extend(all_books_selected.to_dict('records'))
            df = all_books_selected
            # st.dataframe(df)

    st.markdown("""<style>button[kind="primary"] {
        float: right;
    }</style>""", unsafe_allow_html=True)
    for book in isbn_list:
        st.markdown("<hr />", unsafe_allow_html=True)
        isbn = book['isbn']
        title = (book['title'] + ' ' + book['subtitle']).strip()
        desc = book['description'].replace('\n', ' ')
        publisher = book['publisher_name']


        st.markdown(f"##### *{title}*")
        st.markdown(f"""
            - **ISBN:** `{isbn}`
            - **Publisher:** `{publisher}`
            - **Description:** {desc}
        """)
        st.button(f"Borrow {isbn}", type="primary", on_click=navigate(path="/details", args={ "isbn": isbn }))

