from sqlite3 import connect

def setReturn(companyName):
    db = connect ("db.db")
    cursor = db.execute('select rowid, date, company, price, value  from stocks where company like "%' + companyName + '%"')
    for c in cursor:
        rid = c[0]
        date = c[1]
        year = int(date[:4])
        company = c[2]
        price = float(c[3])
        dividendQuery = db.execute('select dividend from expected_dividends where company like "%' + companyName + '%"' + 'and year = ?', (year,))
        expected_dividend = dividendQuery.fetchone()
        if expected_dividend:
            print expected_dividend[0], price
            expected_return = expected_dividend[0]/price 
            db.execute("update stocks set value = ? where rowid = ?", (expected_return, rid))
    
    db.commit()
    db.close()

if __name__ == '__main__':

    setReturn("favorita")

