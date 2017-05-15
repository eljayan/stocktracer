import re
from sqlite3 import connect
from selenium import webdriver
from datetime import datetime

def weekend():
    #do not run on weekends
    day = datetime.today().strftime("%A")
    return day in ["Saturday", "Sunday"]


if weekend():
    quit()

#globals
url = "https://www.bolsadevaloresguayaquil.com/acciones/bvg.asp"
driver = webdriver.Chrome()
db = connect("db.db")

def main():
    
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
    today = datetime.today().strftime("%d-%m-%Y")
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
        else:
            continue

        if company and price:
            stocks_list.append({
                "date": today,
                "company": company,
                "price": price
            })

    return stocks_list

def insert_database(data):
    db.execute('''create table if not exists stocks(
    date text,
    company text,
    price number)''')

    for d in data:
        db.execute("insert into stocks (date, company, price) values (?,?,?)", (d["date"], d["company"], d["price"]))

    db.commit()

if __name__ == '__main__':
    main()
