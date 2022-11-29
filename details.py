import streamlit as st
import pandas as pd
from datetime import datetime

from router import router, args
from utils import query_db, exec_db
from login import login_required

def return_book(event_id, lid, location, isbn):
    user = st.session_state["logined_user"]
    print(f"Return Book: User={user} EventID={event_id}")

    time = datetime.now().strftime("%Y-%m-%d")
    exec_db(f"UPDATE booking_records SET ret_date = '{time}' WHERE event_id = '{event_id}'")

    exec_db(f"UPDATE racks SET num_books = num_books + 1 WHERE lid = '{lid}' AND location = '{location}' AND isbn = '{isbn}';")

    st.success("🎉 Return success!")

def borrow_book(lid, location, isbn):
    user = st.session_state["logined_user"]
    print(f"Borrow Book: User={user} Library={lid} Location={location} ISBN={isbn}")

    exec_db(f"UPDATE racks SET num_books = num_books - 1 WHERE lid = '{lid}' AND location = '{location}' AND isbn = '{isbn}';")

    time = datetime.now().strftime("%Y-%m-%d")
    exec_db(f"INSERT INTO booking_records (lid, location, isbn, ssn, event_date) VALUES ('{lid}', '{location}', '{isbn}', '{user}', '{time}');")

    st.success("🎉 Book borrowed!")

@router(path="/details")
@login_required
def render():
    isbn = args("isbn")
    user = st.session_state["logined_user"]
    st.markdown("# 📖 ISBN"+isbn)

    isbn = st.session_state["args"]["isbn"]
    book = query_db(f"SELECT * FROM books WHERE isbn = '{isbn}';")
    
    if book.empty:
        st.error("😕 The book you searched is not found, please try again:")
    else:
        categories_query = query_db(f"SELECT category_name FROM books_categories_rel WHERE isbn = '{isbn}';")
        categories = []
        for _, row in categories_query.iterrows():
            categories.append(row['category_name'])
        categories = ",".join(categories)

        book = book.loc[0].to_dict()
        st.markdown(f"**Book Name:** _{book['title']}_")
        st.markdown(f"**Publisher:** _{book['publisher_name']}_")
        st.markdown(f"**Category:** _{categories}_")

        st.markdown("### ✒️ Authors")
        authors = query_db(f"SELECT first_name, last_name, dob FROM books_authors_rel b LEFT JOIN authors a ON b.aid = a.aid WHERE isbn = '{isbn}';")
        st.table(authors)
        
        st.markdown("### 📚 Stock Infomation")
        racks = query_db(f"SELECT l.lid, l.name, l.address, r.location, r.num_books FROM racks r LEFT JOIN libraries l ON r.lid = l.lid WHERE r.isbn = '{isbn}';")

        if racks.empty:
            st.error("😕 The book you searched is currently out of stock.")
        else:
            racks = racks.rename(columns={"lid": "ID", "name": "Library", "address": "Address", "location": "Location", "num_books": "Stock Left"})
            st.table(racks)

            # check if the user has a borrow record in database, if exists, show return button
            records = query_db(f"SELECT r.event_id, l.lid, l.name, r.location, r.event_date FROM booking_records r LEFT JOIN libraries l ON l.lid = r.lid WHERE isbn = '{isbn}' AND ssn = '{user}' AND ret_date is NULL;")
            if not records.empty:
                st.markdown("### ⬅️ Return the book")
                records = records.rename(columns={"event_id": "Event ID", "lid": "Library ID", "name": "Library Name", "location": "Location", "event_date": "Start Date"})
                st.table(records)
                st.button('Return the book', type="primary", on_click=lambda: return_book(records.loc[0]['Event ID'], records.loc[0]['Library ID'], records.loc[0]['Location'], isbn))
            else:
                st.markdown("### 🎉 Borrow it online")
                libraries = set()
                for _, row in racks.iterrows():
                    if row["Stock Left"] > 0:
                        libraries.add((row["ID"], row["Library"], row["Location"]))
                
                option = st.selectbox('Which library do you want to borrow the book from?', list(libraries), format_func=lambda x: f"{x[1]} - {x[2]}")
                st.button(f"Borrow from {option[0]}", type="primary", disabled=(not option), on_click=lambda: borrow_book(option[0], option[2], isbn))
