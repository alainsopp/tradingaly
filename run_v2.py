from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, uic, QtWidgets
import csv
import platform
import sys
import pdb
import datetime
import pdb

filename = 'input/data.csv'
bid = 'BID'
ask = 'ASK'
buy = 'BUY'
sell= 'SELL'
limit = 'LIMIT'
market = 'MARKET'

fieldnames = ['bidask','price','size']

class Simulator(QMainWindow):
    def __init__(self, parent=None):
        super(Simulator, self).__init__(parent)        
        self.ui = uic.loadUi('simulator.ui', self) 
        self.ui.setWindowTitle('Tradingaly')
        self.ui.data = []     
        self.ui.update_context()
        self.ui.pushButton_buy.clicked.connect(lambda: self.process_buy_order('ShareX', self.ui.comboBox_type.currentText, int(self.ui.lineEdit_amount.text())))
        self.ui.pushButton_sell.clicked.connect(lambda: self.process_sell_order('ShareX', self.ui.comboBox_type.currentText, int(self.ui.lineEdit_amount.text())))
        self.ui.account = {'balance':100, 'shares':[{'name':'ShareX', 'amount': 100}]}        
        self.ui.label_currency_account_balance.setText(str(self.account['balance']))
        self.ui.label_share_account_balance.setText(str(self.account['shares'][0]['amount']))
        self.show()

    def load_data(self) -> None:
        ''' Loading data from csv file '''        
        with open(filename, 'r', newline='', encoding='utf-8') as f:
            rows = csv.DictReader(f)
            for row in rows:                
                self.ui.data.append({'shareName': 'ShareX', 'offer': row['offer'], 'price': float(row['price']), 'size': int(row['size'])})
                
    def update_context(self) -> None:
        ''' Update gui'''
        self.load_data()
        self.update_market_table()
    
    def update_market_table(self) -> None:
        ''' Update market table with ui.data content'''
        rowindex = 0
        self.tableWidget.setRowCount(len(self.ui.data))
        for row in self.ui.data:                                
            if row['offer'] == bid:
                self.ui.tableWidget.setItem(rowindex,0,QtWidgets.QTableWidgetItem(str(row['size'])))
                self.ui.tableWidget.setItem(rowindex,1,QtWidgets.QTableWidgetItem(str(row['price'])))
            else:                
                self.ui.tableWidget.setItem(rowindex,1,QtWidgets.QTableWidgetItem(str(row['price'])))
                self.ui.tableWidget.setItem(rowindex,2,QtWidgets.QTableWidgetItem(str(row['size']))) 
            rowindex += 1    

    def process_buy_order(self, share: str, type: str, size: int) -> None:
        ''' buy shares on the market'''
        index = self.ui.get_min_bid_index('ShareX')
        price = float(self.ui.data[index]['price'])
        sp = size * price
        bal = float(self.ui.account['balance'])
        siz = self.ui.data[index]['size']
        pric = self.ui.data[index]['price']
        if self.ui.isBuyable(sp, bal, siz, pric):
            current_market_size = siz
            current_market_size -= size
            if current_market_size > 0:
                self.ui.data[index]['size'] = current_market_size
            else:
                self.ui.data.remove(self.ui.data[index])
        self.ui.update_market_table()

    def process_sell_order(self, share: str, type: str, size: int) -> None:
        ''' Sell shares on the market'''
        pass

    def get_min_bid_index(self, share: str) -> int:
        ''' Return the index of the less expansive share inside the
            table representing the market.
        '''
        min_bid = self.ui.data[0]['price']
        index = 0
        for row in self.ui.data:
            val = row['price']
            if row['offer'] == bid and val < min_bid and row['shareName'] == share:
                min_bid = val
        index +=1
        return index

    def isBuyable(self, cost: float, balance: float, availableSize: int, marketPrice: float) -> bool:
        ''' Return true if the account balance is sufficient
        to buy the amount and if the market can provide this amount.
        Return false otherwise
        '''
        return balance - cost > 0 and availableSize * marketPrice > cost
    
    def isSellable(size: int) -> bool:
        ''' Return true if the account balance has enough
            shares to sell the amount specified. Return false
            otherwise.
        '''
        return size > 0 



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Simulator()
    sys.exit(app.exec_())
