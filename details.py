import streamlit as st
import pandas as pd
from datetime import datetime

from router import router, args
from utils import query_db, exec_db
from login import login_required

def return_book(event_id, library, location, isbn):
    user = st.session_state["logined_user"]
    print(f"Return Book: User={user} EventID={event_id}")

    time = datetime.now().strftime("%Y-%m-%d")
    exec_db(f"UPDATE booking_records SET ret_date = '{time}' WHERE event_id = '{event_id}'")

    exec_db(f"UPDATE racks SET num_books = num_books + 1 WHERE library_name = '{library}' AND location = '{location}' AND isbn = '{isbn}';")

    st.success("🎉 Return success!")

def borrow_book(library, location, isbn):
    user = st.session_state["logined_user"]
    print(f"Borrow Book: User={user} Library={library} Location={location} ISBN={isbn}")

    exec_db(f"UPDATE racks SET num_books = num_books - 1 WHERE library_name = '{library}' AND location = '{location}' AND isbn = '{isbn}';")

    time = datetime.now().strftime("%Y-%m-%d")
    exec_db(f"INSERT INTO booking_records (library_name, location, isbn, people_ssn, event_date) VALUES ('{library}', '{location}', '{isbn}', '{user}', '{time}');")

    st.success("🎉 Book borrowed!")

@router(path="/details")
@login_required
def render():
    isbn = args("isbn")
    user = st.session_state["logined_user"]
    st.markdown("# 📖 ISBN"+isbn)

    isbn = st.session_state["args"]["isbn"]
    book = query_db(f"SELECT b.*, a.* FROM books b LEFT JOIN authors a on b.author_id = a.id WHERE b.isbn = '{isbn}';")
    
    if book.empty:
        st.error("😕 The book you searched is not found, please try again:")
    else:
        book = book.loc[0].to_dict()
        st.markdown(f"**Book Name:** _{book['name']}_")
        st.markdown(f"**Category:** _{book['category_name']}_")
        st.markdown(f"**Author:** _{book['last_name']} {book['first_name']}_")
        st.markdown(f"**Publisher:** _{book['publisher_name']}_")
        
        st.markdown("### 📚 Stock Infomation")
        racks = query_db(f"SELECT l.name, l.address, r.location, r.num_books FROM racks r LEFT JOIN libraries l ON r.library_name = l.name WHERE r.isbn = '{isbn}';")

        if racks.empty:
            st.error("😕 The book you searched is currently out of stock.")
        else:
            racks = racks.rename(columns={"name": "Library", "address": "Address", "location": "Location", "num_books": "Stock Left"})
            st.table(racks)

            # check if the user has a borrow record in database, if exists, show return button
            records = query_db(f"SELECT event_id, library_name, location, event_date FROM booking_records WHERE isbn = '{isbn}' AND people_ssn = '{user}' AND ret_date is NULL;")
            if not records.empty:
                st.markdown("### ⬅️ Return the book")
                records = records.rename(columns={"event_id": "Event ID", "library_name": "Library", "location": "Location", "event_date": "Start Date"})
                st.table(records)
                st.button('Return the book', type="primary", on_click=lambda: return_book(records.loc[0]['Event ID'], records.loc[0]['Library'], records.loc[0]['Location'], isbn))
            else:
                st.markdown("### 🎉 Borrow it online")
                libraries = set()
                for _, row in racks.iterrows():
                    if row["Stock Left"] > 0:
                        libraries.add((row["Library"], row["Location"]))
                
                option = st.selectbox('Which library do you want to borrow the book from?', list(libraries), format_func=lambda x: f"{x[0]} - {x[1]}")
                st.button(f"Borrow from {option[0]}", type="primary", disabled=(not option), on_click=lambda: borrow_book(option[0], option[1], isbn))


if __name__ == "__main__":
    render()