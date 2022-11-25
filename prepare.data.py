import httpx
import re
import json
import os

bookReg = "/works/([0-9A-Za-z]+)"
allBooks = set()

D = {
    "books": {},
    "authors": {},
    "publishers": {},
    "subjects": {}
}

if os.path.exists("./database.json"):
    with open("./database.json", "r") as f:
        D = json.loads(f.read())
        if "allBooks" in D:
            allBooks = set(D["allBooks"])

def getBooks(page=1):
    url = f"https://openlibrary.org/trending/forever?page={page}"
    data = httpx.get(url, timeout=30.0).text
    allIds = re.findall(bookReg, data)
    ids = []
    for i in allIds:
        if i not in allBooks:
            allBooks.add(i)
            ids.append(i)
    
    for i in ids:
        try:
            url = f"https://openlibrary.org/works/{i}.json"
            work = httpx.get(url).json()
            url = f"https://openlibrary.org/works/{i}/editions.json"
            editions = httpx.get(url).json()
            for data in editions["entries"]:
                try:
                    if "isbn_13" not in data:
                        continue
                    isbn = data["isbn_13"].pop()
                    if not isbn or isbn in D["books"]:
                        continue
                    if data["languages"][0]["key"] != "/languages/eng":
                        continue
                    data["work"] = work
                    D["books"][isbn] = data
                    for publisher in data["publishers"]:
                        D["publishers"][publisher] = publisher
                    for author in data["authors"]:
                        if author["key"] not in D["authors"]:
                            url = "https://openlibrary.org" + author["key"] + ".json"
                            adata = httpx.get(url).json()
                            D["authors"][author["key"]] = adata
                    for subject in work["subjects"]:
                        D["subjects"][subject] = subject
                    s = len(work["subjects"])
                    p = len(data["publishers"])
                    a = len(data["authors"])
                    # print(f"Downloaded {i}:{isbn}, publishers={p} authors={a} subjects={s}")
                except Exception:
                    pass
        except Exception as e:
            print(f"Downloaded {i} with error: {e}")

    return ids

for i in range(14, 101):
    print(f"Page {i}:", getBooks(i))
    with open("./database.json", "w") as f:
        D["allBooks"] = list(allBooks)
        f.write(json.dumps(D))
