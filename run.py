from PyQt5.QtWidgets import *
from PyQt5 import uic, QtWidgets, QtGui
import sys
import module.function as fct
import config.config as cfg

class Simulator(QMainWindow):
    
    def __init__(self, parent=None):
        
        super(Simulator, self).__init__(parent)                
        self.ui = uic.loadUi('simulator.ui', self) 
        self.ui.setWindowTitle('Tradingaly')
        self.ui.lineEdit_amount.setValidator(QtGui.QIntValidator(1,2147483647, self))
        self.ui.lineEdit_price.setValidator(QtGui.QIntValidator(1,2147483647, self))
        
        ''' View model for market'''
        self.ui.market = fct.load_data(input_file_name)    
        self.ui.update_market_view()
        
        ''' View model for account'''
        self.ui.account = {'balance' : 200, 'shares' : [{'name' : 'ShareX', 'amount' : 200}]}        

        ''' Set events on buttons'''
        self.ui.pushButton_buy.clicked.connect(lambda: self.process_order( 'ShareX', self.ui.lineEdit_amount.text(), self.ui.comboBox_type.currentText(), cfg.buy, self.ui.lineEdit_price.text()))
        self.ui.pushButton_sell.clicked.connect(lambda: self.process_order('ShareX', self.ui.lineEdit_amount.text(), self.ui.comboBox_type.currentText(), cfg.sell,self.ui.lineEdit_price.text()))
        
        self.ui.update_account_view()
        self.show()
                
    def update_context(self) -> None:
        ''' Update gui'''        
        self.update_market_view()
        self.update_account_view()
    
    def set_info_message(self, message: str, color: str) -> None:
        msg = fct.message_date() + message
        self.label_info_content.setText(msg)
        self.label_info_content.setStyleSheet('color:%s;' % color)

    def update_market_view(self) -> None:
        ''' Update market table with ui.data content'''
        rowindex = 0
        self.tableWidget.setRowCount(len(self.ui.market))
        for row in self.ui.market:                                
            if row['offer'] == cfg.bid:
                self.ui.tableWidget.setItem(rowindex,0,QtWidgets.QTableWidgetItem(str(row['size'])))
                self.ui.tableWidget.setItem(rowindex,1,QtWidgets.QTableWidgetItem(str(row['price'])))
            else:                
                self.ui.tableWidget.setItem(rowindex,1,QtWidgets.QTableWidgetItem(str(row['price'])))
                self.ui.tableWidget.setItem(rowindex,2,QtWidgets.QTableWidgetItem(str(row['size']))) 
            rowindex += 1

    def update_account_view(self) -> None:
        self.ui.label_currency_account_balance.setText(str(self.ui.account['balance']))
        self.ui.label_share_account_balance.setText(str(self.ui.account['shares'][0]['amount']))

    def process_order(self, shareName: str, size: int, orderType: str, action: str, limit: int=None) -> None:        
        if size == '':
            ''' Amount is empty'''
            self.set_info_message("Please, enter an amount.", "yellow")            
        else:
            if orderType == cfg.limit:                
                ''' LIMIT order'''
                if limit == None or limit == '':
                    ''' LIMIT value is empty'''
                    self.set_info_message("Please, enter a LIMIT value.", "yellow")
                else:
                    if action == cfg.sell:
                        ''' Sell order'''
                        self.ui.process_buy_limit_order(shareName, size, limit)
                        ''' Buy order'''
                    elif action == cfg.buy:
                        self.ui.process_buy_market_order(shareName, size)
            elif orderType == cfg.market:
                ''' MARKET order'''
                if action == cfg.sell:
                    ''' Sell order'''
                    self.ui.process_sell_market_order(shareName, size)
                elif action == cfg.buy:
                    self.ui.process_buy_market_order(shareName, size)
   
    def process_sell_limit_order(self, share: str, size) -> None:
        ''' Execute a sell limit order.
        '''
        is_operation_processed = False
        return is_operation_processed
    
    def process_sell_market_order(self, share: str, size: int) -> int:
        is_operation_processed = False
        index = fct.get_max_ask_index('ShareX', self.ui.market)
        share_balance = 0
        found = False
        share_count = len(self.ui.account['shares'])
        idx = -1
        while found != True and idx < share_count:
            if self.ui.account['shares'][idx]['name'] == share:
                share_balance = int(self.ui.account['shares'][idx]['amount'])
                found = True
            idx += 1
        if fct.is_sellable(share_balance, size):
            ''' Execute the order'''
            ''' 1. Remove the amount from the share balance account'''
            new_account_share_balance = share_balance - size
            self.ui.account['shares'][idx]['amount'] = new_account_share_balance            
            ''' 2. Remove the associated offer from the market'''
            new_market_size = int(self.market[index]['size']) - size
            self.market[index]['size'] = new_market_size
            ''' 3. Update the currency balance of the account'''
            current_account_currency_balance = float(self.ui.account['balance'])
            market_share_price = self.ui.market[index]['price']
            new_account_currency_balance = current_account_currency_balance + market_share_price * size
            self.ui.account['balance'] = round(new_account_currency_balance, 2)
            ''' 4. Completely remove the offer from market amount 
                if the remining amount equal to 0 after operation.'''            
            if int(self.market[index]['size']) == 0:                
                self.ui.market.remove(self.ui.market[index])
            is_operation_processed = True
        ''' Displays confirmation message'''
        if is_operation_processed:
            self.set_info_message(" Order executed successfully.", "green")            
        else:
            self.set_info_message(" Order not executed.", "red")
        self.ui.update_context()    
        return is_operation_processed
 
    def process_buy_market_order(self, share: str, size: int) -> int:
        ''' buy shares on the market by executing a market buy order.
        '''
        is_operation_processed = False
        index = fct.get_min_bid_index('ShareX', self.ui.market)
        price = float(self.ui.market[index]['price'])
        sizeprice = size * price
        account_balance = float(self.ui.account['balance'])
        market_size = self.ui.market[index]['size']
        market_price = self.ui.market[index]['price']
        ''' Remove share amount rom the market'''
        if fct.is_buyable(sizeprice, account_balance, market_size, market_price):
            current_market_size = market_size
            current_market_size -= size            
            if current_market_size > 0:
                self.ui.market[index]['size'] = current_market_size
                self.ui.account['balance'] = round(self.ui.account['balance'] - sizeprice, 2)
            else:
                ''' Remove share completely from the market'''
                self.ui.market.remove(self.ui.market[index])
            ''' Add new share to the account shares balance'''
            idx = 0
            size_share = len(self.ui.account['shares'])
            found = False        
            while idx <= size_share - 1 and not found:            
                if self.ui.account['shares'][idx]['name'] == share:            
                    self.ui.account['shares'][idx]['amount'] += size
                    found = True
                    is_operation_processed = True
                idx += 1
        ''' Displays confirmation message'''
        if is_operation_processed:
            self.set_info_message(" Order executed successfully.", "green")            
        else:
            self.set_info_message(" Order not executed.", "red")
        self.ui.update_context()
        return is_operation_processed
        
    def process_buy_limit_order(self, share: str, size: int, limit: float) -> None:
        ''' Execute a buy limit order only if the share price is lower than <limit>.
            If no shares is under the limit, add a new offer to the market.
        '''
        is_opreation_processed = False
        index = fct.get_limit_min_bid_index('ShareX', limit, self.ui.market)
        if index != -1:
            ''' If an offer at the limit was found, then execute the order'''
            price = float(self.ui.market[index]['price'])
            sizeprice = size * price
            account_balance = float(self.ui.account['balance'])
            market_size = self.ui.market[index]['size']
            market_price = self.ui.market[index]['price']
            ''' Remove share amount from market'''
            if fct.is_buyable(sizeprice, account_balance, market_size, market_price):                
                market_size -= size            
                if market_size > 0:
                    self.ui.market[index]['size'] = market_size
                    self.ui.account['balance'] = round(self.ui.account['balance'] - sizeprice, 2)
                else:
                    ''' Remove share completely from the market'''
                    self.ui.market.remove(self.ui.market[index])
                ''' Add new share to the account shares balance'''
                idx = 0
                size_share = len(self.ui.account['shares'])
                found = False        
                while idx <= size_share - 1 and not found:            
                    if self.ui.account['shares'][idx]['name'] == share:            
                        self.ui.account['shares'][idx]['amount'] += size
                        found = True
                        is_operation_processed = True
                    idx += 1
            ''' Displays confirmation message'''
            if is_operation_processed:
                self.set_info_message(" Order executed successfully.", "green")            
            else:
                self.set_info_message(" Order not executed.", "red")
        else:
            ''' If not offer at the limit was found then
                add a new offer on the market
            '''
            self.ui.market.append({'shareName': 'ShareX', 'offer': 'ASK', 'price': limit, 'size': size})
        self.ui.update_context()
        return is_opreation_processed

if __name__ == '__main__':
    app = QApplication(sys.argv)
    input_file_name = "input/data.csv"
    ex = Simulator()
    sys.exit(app.exec_())