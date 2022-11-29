import json
import hashlib
import psycopg2
import random
from random import randint
from configparser import ConfigParser

COMMIT_LOGS = []

CREATE_BASE = """
drop table if exists booking_records;
drop table if exists racks;
drop table if exists books_authors_rel;
drop table if exists books_categories_rel;

drop table if exists books;
drop table if exists people;
drop table if exists publishers;
drop table if exists libraries;
drop table if exists authors;
drop table if exists categories;

create table if not exists people
(
    ssn        varchar(16)  primary key,
    username   varchar(128) unique,
    password   varchar(128),
    first_name varchar(128),
    last_name  varchar(128),
    address    varchar(128),
    role       integer
);

create table if not exists libraries
(
    lid varchar(128) primary key,
    name varchar(128) not null,
    address varchar(128),
    zipcode varchar(128)
);

create table if not exists publishers
(
    publisher_name varchar(128) primary key,
    created varchar(4)
);

create table if not exists authors
(
    aid varchar(128) primary key,
    first_name varchar(128),
    last_name varchar(128),
    dob date
);

create table if not exists categories
(
    category_name varchar(128) not null,
    primary key (category_name)
);

create table if not exists books
(
    isbn varchar(128) not null,
    title varchar(128),
    subtitle varchar(128),
    description text,
    publisher_name varchar(128),
    primary key (isbn),
    foreign key (publisher_name) references publishers
);

create table if not exists books_authors_rel
(
    isbn varchar(128) not null,
    aid varchar(128) not null,
    primary key (isbn, aid),
    foreign key (aid) references authors
);

create table if not exists books_categories_rel
(
    isbn varchar(128) not null,
    category_name varchar(128) not null,
    primary key (isbn, category_name),
    foreign key (category_name) references categories on delete cascade
);

create table if not exists racks
(
    lid varchar(128) not null,
    isbn varchar(128) not null,
    location varchar(128) not null,
    num_books integer,
    primary key (lid, isbn, location),
    foreign key (lid) references libraries on delete cascade,
    foreign key (isbn) references books on delete cascade
);

create table if not exists booking_records
(
    event_id     integer generated always as identity,
    lid          varchar(128),
    isbn         varchar(128),
    ssn          varchar(16),
    event_date   date,
    ret_date     date,
    location     varchar(64),
    primary key (event_id),
    foreign key (lid) references libraries,
    foreign key (isbn) references books,
    foreign key (ssn) references people
);
"""

def get(fn, default=None):
    try:
        return fn()
    except Exception:
        pass
    return default

def get_config(filename="local.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}

def run(sql):
    db_info = get_config()
    conn = psycopg2.connect(**db_info)

    cur = conn.cursor()
    cur.execute(sql)
    COMMIT_LOGS.append(sql)

    conn.commit()
    cur.close()
    conn.close()

def irun(table, cols, extra=""):
    COMMIT_LOGS.append("")
    COMMIT_LOGS.append("")

    db_info = get_config()
    conn = psycopg2.connect(**db_info)

    cur = conn.cursor()
    i = 0
    for entry in cols:
        if len(cols) >= 1000 and i % 1000 == 0:
            print(f"Migrating {table}: {i}/{len(cols)} ...")
        keys = []
        values = []
        for k in entry:
            keys.append(k)
            values.append("'" + f"{entry[k]}".replace("'", "") + "'")
        keys = ",".join(keys)
        values = ",".join(values)
        sql = f"INSERT INTO {table} ({keys}) VALUES ({values}) " + extra
        cur.execute(sql)
        COMMIT_LOGS.append(sql.strip()+";")
        i += 1

    print(f"Committing {table}: {len(cols)} ...")
    conn.commit()
    cur.close()
    conn.close()

AB = 'QWERTYUIOPASDFGHJKLZXCVBNM'
def randlocation():
    return AB[randint(0, 25)] + AB[randint(0, 25)] + f"{randint(0, 9)}" + f"{randint(0, 9)}"

# create tables
run(CREATE_BASE)

# create initial records
irun("people", [{
    "ssn": 4820394710,
    "username": "demo",
    "password": hashlib.md5("demo".encode()).hexdigest(),
    "first_name": "demo",
    "last_name": "demo",
    "role": 0,
}, {
    "ssn": 5819283842,
    "username": "bob",
    "password": hashlib.md5("bob".encode()).hexdigest(),
    "first_name": "bob",
    "last_name": "bob",
    "role": 1,
}])

irun("libraries", [{
    "lid": "L1",
    "name": "NYU Bobst",
    "address": "714 Broadway, 10003, NY",
    "zipcode": "10003",
}, {
    "lid": "L2",
    "name": "NYU Tandon Library",
    "address": "5 MetroTech, 11201, NY",
    "zipcode": "11201",
}])
ALL_LIBS = ["L1", "L2"]

# build data
D = {}
with open('./database.json') as f:
    D = json.loads(f.read())

publishers = set()
categories = set()
authors = set()
books = []
books_authors_rel = []
books_categories_rel = []
racks = []
for isbn in D['books']:
    b = D['books'][isbn]
    if ('publishers' not in b) or (len(b['publishers']) == 0) or ('work' not in b) or ('authors' not in b['work']) or ('subjects' not in b['work']):
        continue
    
    # publishers
    publisher = b['publishers'][0].replace("'", "")
    publishers.add(publisher)

    # authors, books_authors_rel
    for au in b['work']['authors']:
        aid = get(lambda: au['author']['key'], "").replace('/authors/', '')
        if ('/authors/'+aid) in D['authors']:
            authors.add(aid)
            books_authors_rel.append({
                'isbn': isbn,
                'aid': aid,
            })
    
    # categories
    for ca in b['work']['subjects']:
        categories.add(ca)
        books_categories_rel.append({
            'isbn': isbn,
            'category_name': ca,
        })

    books.append({
        'isbn': isbn,
        'title': b['title'],
        'subtitle': get(lambda: b['subtitle'], ""),
        'publisher_name': b['publishers'][0],
        'description': get(lambda: b['work']['description']['value'], ""),
    })

    for i in range(randint(1, 3)):
        lid = ALL_LIBS[randint(0, 1)]
        racks.append({
            'lid': lid,
            'isbn': isbn,
            'location': randlocation(),
            'num_books': randint(0, 32),
        })
    
    # limit
    if len(books) > 100:
        break

print(f"Wait to commit: publishers={len(publishers)} categories={len(categories)} authors={len(authors)} books={len(books)} " + 
    f"books_authors_rel={len(books_authors_rel)} books_categories_rel={len(books_categories_rel)} racks={len(racks)}")

publishers_ = []
for p in publishers:
    publishers_.append({ 'publisher_name': p, 'created': randint(1990, 2014) })
irun('publishers', publishers_, 'ON CONFLICT (publisher_name) DO NOTHING')

categories_ = []
for p in categories:
    categories_.append({ 'category_name': p })
irun('categories', categories_, 'ON CONFLICT (category_name) DO NOTHING')

authors_ = []
for aid in authors:
    au = D['authors']['/authors/'+aid]
    name = au['name'].split(' ')
    lastname = name.pop()
    firstname = ' '.join(name)
    authors_.append({ 'aid': aid, 'first_name': firstname, 'last_name': lastname })
irun('authors', authors_, 'ON CONFLICT (aid) DO NOTHING')

irun('books', books, 'ON CONFLICT (isbn) DO NOTHING')
irun('books_authors_rel', books_authors_rel)
irun('books_categories_rel', books_categories_rel)
irun('racks', racks)

with open("database.sql", "w") as f:
    f.write("\n".join(COMMIT_LOGS))

