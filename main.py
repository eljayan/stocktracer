import re
from sqlite3 import connect
from selenium import webdriver
from datetime import datetime

url = "https://www.bolsadevaloresguayaquil.com/acciones/bvg.asp"
driver = webdriver.Chrome()
db = connect("D:/myScripts/stockstracer/db.db")

def main():
    if weekend():
        quit()

    #download stock prices
    download()

    #calculate returns
    for c in ["favorita", "holcim"]:
        setReturn(c)

    db.commit()
    db.close()

def weekend():
    # do not run on weekends
    day = datetime.today().strftime("%A")
    return day in ["Saturday", "Sunday"]


def download():
    page_text = get_page_data()
    stocks_list = format_data(page_text)
    for s in stocks_list:
        print s

    insert_database(stocks_list)

    driver.close()
    driver.quit()

def get_page_data():

    driver.get(url)

    table = driver.find_element_by_tag_name("table")

    page_text = table.text
    return page_text


def format_data(page_text):
    today = datetime.today().strftime("%Y-%m-%d")
    stocks_list= []

    stock_blocks = page_text.split("\n")[4:-3]

    #define the regexps
    companyreg = re.compile(r'\D*')
    stockreg = re.compile(r'\$\d+[\.\,]?\d+[\.\,]?\d*')

    for s in stock_blocks:
        find_company = companyreg.search(s)
        find_price = stockreg.search(s)

        if find_company and find_price:
            company = find_company.group()
            price = find_price.group()[1:]
            price = price.replace(",", "")
        else:
            continue

        if company and price:
            stocks_list.append({
                "date": today,
                "company": company,
                "price": float(price)
            })

    return stocks_list

def insert_database(data):

    for d in data:
        db.execute("insert into stocks (date, company, price) values (?,?,?)", (d["date"], d["company"], d["price"]))



def setReturn(companyName):
    cursor = db.execute(
        'select rowid, date, company, price, value  from stocks where company like "%' + companyName + '%"')
    for c in cursor:
        rid = c[0]
        date = c[1]
        year = int(date[:4])
        price = float(c[3])
        dividendQuery = db.execute(
            'select dividend from expected_dividends where company like "%' + companyName + '%"' + 'and year = ?',
            (year,))
        expected_dividend = dividendQuery.fetchone()
        if expected_dividend:
            print expected_dividend[0], price
            expected_return = expected_dividend[0] / price
            db.execute("update stocks set value = ? where rowid = ?", (expected_return, rid))


if __name__ == "__main__":
    main()