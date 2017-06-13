from sqlite3 import connect
from datetime import datetime

def main():
    db = connect("db.db")
    cursor = db.execute("select rowid, date from stocks")
    for d in cursor:
        rowid = d[0]
        newdate = datetime.strptime(d[1], "%d-%m-%y")
        newdate = datetime.strftime(newdate, "%Y-%m-%d")
        db.execute("update stocks set date=? where rowid=?", (newdate, rowid))
    db.commit()

if __name__ == "__main__":
    main()
