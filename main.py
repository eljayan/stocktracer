import re
from sqlite3 import connect
from selenium import webdriver
from datetime import datetime

class App:
    def __init__(self):
        self.url = "https://www.bolsadevaloresguayaquil.com/acciones/bvg.asp"
        self.testWeekend()
        self.connectToDb()

    def testWeekend(self):
        date = datetime.today()
        day = datetime.strftime(date, "%A")
        if day in ["Sunday"]:
            quit()

    def connectToDb(self):
        self.db = connect("D:/myScripts/stockstracer/db.db")

    def createDriver(self):
        driver = webdriver.Chrome()
        self.driver = driver

    def download(self):
        return #IMPLEMENT USING REQUESTS

    def downloadWithDriver(self):
        # dowloads the pade
        self.driver.get(self.url)
        table = self.driver.find_element_by_tag_name("table")
        self.page_text = table.text


    def format_data(self):
        # takes the page and returns a list of dictionaries with stock info
        today = datetime.today().strftime("%Y-%m-%d")
        stocks_list = []

        stock_blocks = self.page_text.split("\n")[4:-3]

        # define the regexps
        companyreg = re.compile(r'\D*')
        stockreg = re.compile(r'\$\d+[\.\,]?\d+[\.\,]?\d*')

        for s in stock_blocks:
            find_company = companyreg.search(s)
            find_price = stockreg.search(s)

            if find_company and find_price:
                company = find_company.group().strip()
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

        self.stocks_list = stocks_list

    def insert_database(self):
        for d in self.stocks_list:
            self.db.execute("insert into stocks (date, company, price) values (?,?,?)",
                       (d["date"], d["company"], d["price"]))



    def setReturn(self, companyName):
        # calculates the expected return of a stock at current price
        cursor = self.db.execute(
            'select rowid, date, company, price, return  from stocks where company like "%' + companyName + '%"')
        for c in cursor:
            rid = c[0]
            date = c[1]
            year = int(date[:4])
            price = c[3]
            dividendQuery = self.db.execute(
                'select dividend from expected_dividends where company like "%' + companyName + '%"' + 'and year = ?',
                (year,))
            expected_dividend = dividendQuery.fetchone()
            if expected_dividend:
                print expected_dividend[0], price
                expected_return = expected_dividend[0] / price
                self.db.execute("update stocks set return = ? where rowid = ?", (expected_return, rid))

    def setYield(self, companyName):
        cursor = self.db.execute(
            'select rowid, date, company, price, earnings_yield  from stocks where company like "%' + companyName + '%"')
        for c in cursor:
            rid = c[0]
            date = c[1]
            year = int(date[:4])
            price = c[3]
            earningsQuery = self.db.execute(
                'select earnings_per_share from earnings where company like "%' + companyName + '%"' + 'and year = ?',
                (year,))
            earnings = earningsQuery.fetchone()
            if earnings:
                print earnings[0], price
                earnings_yield = earnings[0] / price
                self.db.execute("update stocks set earnings_yield = ? where rowid = ?", (earnings_yield, rid))

    def calculateReturs(self):
        for c in ["favorita", "holcim", "banco guayaquil", "banco pichincha", "cerveceria nacional",
                  "continental tire", "produbanco", "homeforest", "alicosta", "cerro verde", "brikapital",
                  "banco bolivariano", "unacem", "pathforest", "el tecal", "tonicorp", "inversancarlos"]:
            self.setReturn(c)
            self.setYield(c)


if __name__ == "__main__":
    app = App()
    app.downloadWithDriver()
    app.format_data()
    app.insert_database()
    app.db.commit()
    app.db.close()