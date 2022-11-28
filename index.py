import streamlit as st

from router import router, navigate
from utils import query_db, exec_db
from login import login_required

@router(path="/")
def render():
    # only for demo purpose
    import demo
    st.button("Go to Demo Page", on_click=navigate(path="/demo", args={ "id": "A-Demo-ID" }))
    st.button("Go to Statstics Page", on_click=navigate(path="/stats"))

    st.markdown("# This is the book searching page.")

    isbn_list = []

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
            books_selected = query_db(f"SELECT title, isbn, publisher_name, description FROM books WHERE title = '{title_selected}';")
            df = books_selected
            isbn_list.extend(books_selected["isbn"].tolist())
            st.dataframe(df)
        except:
            st.write(
                "Sorry! Something went wrong with your query, please try again."
            )

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
            all_books_selected = query_db(f"SELECT k.title, b.isbn, k.publisher_name, k.description FROM books_authors_rel b LEFT JOIN authors a ON b.aid = a.aid LEFT JOIN books k ON b.isbn = k.isbn WHERE a.first_name = '{first_name_selected}' AND a.last_name = '{last_name_selected}';")
            isbn_list.extend(all_books_selected["isbn"].tolist())
            df = all_books_selected
            st.dataframe(df)
        except:
            st.write(
                "Sorry! Something went wrong with your query, please try again."
            )

    "## Select book"
    st.markdown("### 🔍️ Select book by isbn")
    if author_selected or title_selected:
        isbn_list = list(set(isbn_list))
        isbn_selected = st.selectbox("Choose the isbn listed", isbn_list)

    if isbn_selected:
        book_name = query_db(f"SELECT title FROM books WHERE isbn = '{isbn_selected}';")
        button_name = f"Read More About Book: " + book_name["title"].tolist()[0]
        st.button(button_name, on_click=navigate(path="/details", args={"isbn": isbn_selected}))
    else:
        st.button(f"Read More About Book: Test Book 1", on_click=navigate(path="/details", args={ "isbn": "9781612681122" }))

if __name__ == "__main__":
    render()
