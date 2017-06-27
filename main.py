import requests
from bs4 import BeautifulSoup
from sqlite3 import connect
from selenium import webdriver
from datetime import datetime

class App:
    def __init__(self):
        self.url = "https://www.bolsadevaloresguayaquil.com/acciones/bvg.asp"
        self.setProxies()
        self.testWeekend()
        self.connectToDb()

    def setProxies(self):
        proxies = {
            "http":"http://r00715649:Huawei%3F8@proxyuk2.huawei.com:8080",
            "https":"http://r00715649:Huawei%3F8@proxyuk2.huawei.com:8080"
        }
        self.proxies = proxies

    def testWeekend(self):
        date = datetime.today()
        day = datetime.strftime(date, "%A")
        if day in ["Saturday", "Sunday"]:
            quit()

    def connectToDb(self):
        self.db = connect("D:/myScripts/stockstracer/db.db")

    def createDriver(self):
        driver = webdriver.Chrome()
        self.driver = driver

    def download(self, useproxy = False):
        if useproxy:
            self.page_text = requests.get(self.url, proxies=self.proxies).text
        else:
            self.page_text = requests.get(self.url).text
        return

    def downloadWithDriver(self):
        # dowloads the pade
        driver = webdriver.Chrome()
        driver.get(self.url)
        # table = driver.find_element_by_tag_name("table")
        self.page_text = driver.page_source
        driver.close()

    def formatPrice(self, price):
        price = price.replace("$", "")
        price = price.replace(",", "")
        price = price.replace("*", "0")
        price = float(price)
        return price

    def format_data(self):
        '''returns a list of tuples'''
        stocks_list = []
        today = datetime.today().strftime("%Y-%m-%d")
        soup = BeautifulSoup(self.page_text, 'html.parser')
        table = soup.find_all("table")[2]
        rows = table.find_all("tr")
        for r in rows[1:-1]:
            cells = r.find_all("td")
            company = cells[0].text.strip()
            price = self.formatPrice(cells[3].text.strip())
            stocks_list.append((today, company, price))

        self.stocks_list = stocks_list

    def insert_database(self):
        for data in self.stocks_list:
            self.db.execute("insert into stocks (date, company, price) values (?,?,?)",
                       (data))

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
            #SELECT LAST YEARS EARNINGS (year - 1)
            earningsQuery = self.db.execute(
                'select earnings_per_share from earnings where company like "%' + companyName + '%"' + 'and year = ?',
                (year-1,))
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
    # app.downloadWithDriver()
    app.download(useproxy=True)
    app.format_data()
    app.insert_database()
    app.calculateReturs()
    app.db.commit()
    app.db.close()