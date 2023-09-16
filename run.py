from PyQt5.QtWidgets import *
from PyQt5 import uic, QtWidgets
import sys
import module.function as fct
import config.config as cfg

class Simulator(QMainWindow):
    
    def __init__(self, parent=None):
        
        super(Simulator, self).__init__(parent)                
        self.ui = uic.loadUi('simulator.ui', self) 
        self.ui.setWindowTitle('Tradingaly')
        
        ''' View model for market'''
        self.ui.market = fct.load_data(input_file_name)    
        self.ui.update_market_view()
        
        ''' View model for account'''
        self.ui.account = {'balance' : 200, 'shares' : [{'name' : 'ShareX', 'amount' : 200}]}        

        ''' Set events on buttons'''
        self.ui.pushButton_buy.clicked.connect(lambda: self.process_buy_order('ShareX', self.ui.comboBox_type.currentText(), int(self.ui.lineEdit_amount.text())))
        self.ui.pushButton_sell.clicked.connect(lambda: self.process_sell_order('ShareX', self.ui.comboBox_type.currentText(), int(self.ui.lineEdit_amount.text())))
        
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

    def process_buy_order(self, share: str, type: str, size:int) -> None:
        ''' Execute a buy (MARKET or LIMIT) order
        '''
        if type == cfg.market:
            self.process_buy_market_order(share, size)
        if type == cfg.limit:
            self.process_buy_limit_order(share, size)

    def process_buy_limit_order(self, share: str, size) -> None:
        ''' Execute a buy limit order.
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
        market_size= self.ui.market[index]['size']
        market_price = self.ui.market[index]['price']
        ''' Remove share from the market'''
        if fct.is_buyable(sizeprice, account_balance, market_size, market_price):
            current_market_size = market_size
            current_market_size -= size            
            if current_market_size > 0:
                self.ui.market[index]['size'] = current_market_size
                self.ui.account['balance'] = round(self.ui.account['balance'] - sizeprice,2)
            else:
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

    def process_sell_order(self, share: str, type: str, size: int) -> None:
        ''' Execute a sell order (LIMIT or MARKET)'''
        if type == cfg.limit:
            print('LIMIT order')
        else:
            self.ui.process_sell_market_order(share, size)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    input_file_name = "input/data.csv"
    ex = Simulator()
    sys.exit(app.exec_())