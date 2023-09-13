from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, uic, QtWidgets
import csv
import platform
import sys
import pdb
import datetime

filename = 'input/editeddata.csv'
bid = 'BID'
ask = 'ASK'
buy = 'BUY'
sell= 'SELL'
limit = 'LIMIT'
market = 'MARKET'

fieldnames = ['bidask','price','size']
account_initial_currency_balance = 199
account_initial_share_balance = 200

class OrderBook(QMainWindow):
    def __init__(self, parent=None):
        super(OrderBook, self).__init__(parent)        
        self.ui = uic.loadUi('orderbook.ui', self) 
        self.ui.setWindowTitle('Tradingaly')       
        self.updateContext()
        self.ui.pushButton_go.clicked.connect(self.executeOrder)        
        self.account_currency_balance = account_initial_currency_balance
        self.account_share_balance = account_initial_share_balance
        self.ui.label_currency_account_balance.setText(str(self.account_currency_balance))
        self.ui.label_share_account_balance.setText(str(self.account_share_balance))
        self.show()

    def updateContext(self):
        ''' Load data from source and updating GUI table content'''
        self.loadData()
        self.updateTable()
    
    def updateTable(self) -> None:
        ''' Update GUI table content'''
        rowindex = 0
        self.tableWidget.setRowCount(len(self.ui.data))
        for row in self.ui.data:                    
            if row['bidask'] == 'BID':
                self.ui.tableWidget.setItem(rowindex,0,QtWidgets.QTableWidgetItem(row['size']))
                self.ui.tableWidget.setItem(rowindex,1,QtWidgets.QTableWidgetItem(row['price']))
            else:                
                self.ui.tableWidget.setItem(rowindex,1,QtWidgets.QTableWidgetItem(row['price']))
                self.ui.tableWidget.setItem(rowindex,2,QtWidgets.QTableWidgetItem(row['size']))
            rowindex += 1
        self.tableWidget.sortItems(1, QtCore.Qt.AscendingOrder)
    
    def loadData(self) -> None:
        ''' Loading data from source to Orderbook object'''
        self.ui.data = []
        with open(filename, 'r', newline='', encoding='utf-8') as f:
            rows = csv.DictReader(f)
            for row in rows:
                self.ui.data.append(row)        
    
    def addOrder(self, bidask: str, price: str, amount: str)-> None:
        ''' Add order(bid or ask) into data'''
        index = -1
        i = 0
        while (index == -1 and i < len(self.ui.data)):             
            if self.ui.data[i]['bidask'] == bidask and self.ui.data[i]['price'] == price:                
                self.ui.data[i]['size'] = str(float(self.ui.data[i]['size']) + float(amount))
                index = i
            i += 1        
        if (index != -1):
            ''' The same order was found'''
            with open(filename, 'w', newline='') as f:
                w=csv.DictWriter(f,fieldnames=fieldnames)
                w.writeheader()
                w.writerows(self.ui.data)        
        else:
            ''' No pre existing order was found'''
            with open(filename, 'a', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow([bidask,price,amount])

        ''' reloading data in viewmodel'''
        self.loadData()
        self.updateTable()
    
    def isOrderSubmitable(self):
        '''Checking if the form fields are properly filled.'''
        bidask = self.ui.combobox_buysell.currentText()
        amount = self.ui.lineEdit_amount.text()
        price = self.ui.lineEdit_price.text()
        typeOrder = self.ui.comboBox_type.currentText()
        isSubmitable = False

        if bidask == buy:
            if typeOrder == limit:
                isSubmitable = True if amount != '' and price != '' else False 
            # if typeOrder == market
            else:
                isSubmitable = True if amount != '' else False
        # bidask == sell
        else:
            if typeOrder == limit:
                isSubmitable = True if amount != '' and price != '' else False
            else:
                isSubmitable = True if amount != '' else False
        return isSubmitable
    
    def isBalanceSufficient(self):
        ''' Check if the account balance is sufficient to buy or sell shares.'''
        bidask = self.ui.combobox_buysell.currentText()
        price = self.ui.lineEdit_price.text()
        amount = self.ui.lineEdit_amount.text()
        sufficientBalance = False
        
        if bidask == sell:
            sufficientBalance = True if int(self.account_share_balance) > float(amount) else False
        # bidask == bid
        else:
            sufficientBalance = True if float(amount) * float(price) > float(self.account_currency_balance) else False        
        return sufficientBalance
    
    def isOrderSatisfiable(self, bidask: str, price: str, amount: str) -> bool:        
        ''' Determine wether the total amount of Asks or Bid satisfies respectivement the bid or the ask'''
        amountAvailable = 0
        for row in self.ui.data:
            if price != '':
                if (bidask == bid and row['bidask'] == ask and float(row['price']) <= float(price)):
                    amountAvailable += float(row['size'])
                if (bidask == ask and row['bidask'] == bid and float(row['price']) >= float(price)):
                    amountAvailable += float(row['size'])
            else:
                if (bidask == bid and row['bidask'] == ask):
                    amountAvailable += float(row['size'])
                if (bidask == ask and row['bidask'] == bid):
                    amountAvailable += float(row['size'])

        return amountAvailable >= int(amount)
    
    def getBidAskIndexes(self, bidask: str, price: str) -> list:
        ''' Getting all ask/bid offers row indexes from the source file
            TODO: fix indentation
        '''
        bidaskIndexes = []
        i = 0

        # We are looking for buying at the market lowest available price
        if bidask == bid:
            pass#or row in self.ui.data:
                #if row['bidask'] == bidask and float(row['price']) <= float(price):
		         #  	bidaskIndexes.append(i)
		          # 	i += 1

        # We are looking for selling at the market highest available price
		#elif bidask == ask:
		    #pass#for row in self.ui.data:
		     #  	if row['bidask'] == bidask and float(row['price']) >= float(price):
		      #     	bidaskIndexes.append(i)
		       #    	i += 1
        return bidaskIndexes
    
    def processLimitedOrder(self, bidask: str, price: str, amount: str)-> None:
        ''' Remov' the amount of order corresponding to amount parameter
        and updates account balance.
        '''
        reliquat = int(amount)
        account_balance = self.account_currency_balance
        mirrorOrder = bid if bidask == ask else ask

        if bidask == bid:

            ''' TODO: sort from the lower to the higher price'''
            bidaskIndexes = self.getBidAskIndexes(mirrorOrder, price)
            print(bidaskIndexes)
            i = 0
            while i <= len(bidaskIndexes) and reliquat > 0:                
                reliquat = reliquat - float(self.ui.data[bidaskIndexes[i]]['size'])

                if reliquat < 0:
                    ''' if there is more offer in the order book than the mirror order'''
                    print('reliquat is inferior to 0')
                    newAmount = float(self.ui.data[bidaskIndexes[i]]['size']) - reliquat
                    if bidask == bid:
                        account_balance -= float(amount) * float(self.ui.data[bidaskIndexes[i]]['price'])
                    else:
                        account_balance += float(amount) * float(self.ui.data[bidaskIndexes[i]]['price'])
                    self.ui.data[bidaskIndexes[i]]['size'] = newAmount                
                elif reliquat == 0:
                    ''' remove the row into data (all sells are consumed)'''
                    print('reliquat is equal to 0')
                    if bidask == bid:
                        account_balance -= float(amount) * float(self.ui.data[bidaskIndexes[i]]['price'])
                        del(self.ui.data[bidaskIndexes[i]])
                    else:
                        account_balance += float(amount) * float(self.ui.data[bidaskIndexes[i]]['price'])
                        del(self.ui.data[bidaskIndexes[i]])                
                else:
                    ''' if there is not enough asks to absorb all buys'''
                    print('reliquat is superior to 0')
                    if bidask == bid:
                        account_balance -= float(self.ui.data[bidaskIndexes[i]]['size']) * float(self.ui.data[bidaskIndexes[i]]['price'])
                        del(self.ui.data[bidaskIndexes[i]])
                    else:
                        account_balance += float(self.ui.data[bidaskIndexes[i]]['size']) * float(self.ui.data[bidaskIndexes[i]]['price'])
                        del(self.ui.data[bidaskIndexes[i]])
                i += 1

        ''' TODO : Complete this sections with a similar business as the previous section'''
        if bidask == ask:
            print("Limited selling order.")
    
    def getBidAskIndexes(self, bidask: str) -> list:
        ''' Get all ask/bid offers row indexes from the source file'''
        bidaskIndexes = []
        i = 0
        for row in self.ui.data:
            if row['bidask'] == bidask:
                bidaskIndexes.append(i)
                i += 1
        return bidaskIndexes

    def processMarketOrder(self, bidask: str, amount: str) -> None:
        pass
    
    def executeOrder(self) -> None:
        ''' Sells or buy shares if possible. Otherwise adds the new order to the book.'''
        bidask =  self.ui.combobox_buysell.currentText()
        bidask = ask if bidask == sell else bid
        price = self.ui.lineEdit_price.text()
        amount = self.ui.lineEdit_amount.text()       

        if self.isOrderSubmitable():
            d = datetime.datetime.now()
            frmtd = d.strftime("%d/%m/%y %H:%M:%S")
            msg = frmtd
            if self.isBalanceSufficient():
                if self.isOrderSatisfiable(bidask, price, amount):
                    self.processLimitedOrder(bidask, price, amount)
                    msg = msg + " Order executed successfully."
                    self.label_info_content.setText(msg)
                    self.label_info_content.setStyleSheet('color:green;')
                else:
                    self.addOrder(bidask, price, amoun)
                    msg = msg + " New order placed successfully."
                    self.label_info_content.setText(msg)
                    self.label_info_content.setStyleSheet('color:green;')
            else:
                msg = msg + " Insufficient balance."
                self.label_info_content.setStyleSheet('color:red;')
                self.label_info_content.setText(msg)
        else:
            self.label_info_content.setStyleSheet('color:yellow;')
            self.label_info_content.setText("Please, complete amount or Limit.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = OrderBook()
    sys.exit(app.exec_())
