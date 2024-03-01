from PyQt5.QtWidgets import *
from PyQt5 import uic, QtWidgets, QtGui
import sys
import module.function as fct
import config.config as cfg
import uuid

class Simulator(QMainWindow):
    
    def __init__(self, parent=None):
        
        super(Simulator, self).__init__(parent)                
        self.ui = uic.loadUi('simulator.ui', self) 
        self.ui.setWindowTitle('Tradingaly')
        self.ui.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        header = self.ui.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        self.ui.lineEdit_amount.setValidator(QtGui.QIntValidator(1,2147483647, self))
        self.ui.lineEdit_price.setValidator(QtGui.QIntValidator(1,2147483647, self))
        
        ''' View model for market'''
        self.ui.market = fct.load_data(input_file_name)    
        self.ui.update_market_view()
        
        ''' View model for account'''
        self.ui.account = {'balance' : 200, 'shares' : [{'name' : 'ShareX', 'amount' : 200}]}        

        self.ui.transaction_id = ''
        ''' Set events on buttons'''
        self.ui.pushButton_buy.clicked.connect(lambda: self.process_order( 'ShareX', self.ui.lineEdit_amount.text(), self.ui.comboBox_type.currentText(), cfg.buy, self.ui.lineEdit_price.text()))
        self.ui.pushButton_sell.clicked.connect(lambda: self.process_order('ShareX', self.ui.lineEdit_amount.text(), self.ui.comboBox_type.currentText(), cfg.sell,self.ui.lineEdit_price.text()))
        
        self.ui.update_account_view()
        self.show()
                
    def update_context(self) -> None:
        ''' Update gui'''        
        self.update_market_view()
        self.update_account_view()
    
    def set_info_message(self, transacId: str, message: str, color: str) -> None:        
        msg = fct.message_date() + ' [' + transacId + ']' + message        
        self.ui.label_info_content.setText(msg)
        self.ui.label_info_content.setStyleSheet('color:%s;' % color)

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
            msg = " Please, enter amount value."
            self.set_info_message("", msg, "yellow")            
        else:
            if orderType == cfg.limit:                
                ''' LIMIT order'''
                if limit == None or limit == '':
                    ''' LIMIT value is empty'''
                    msg = " Please, enter LIMIT value."
                    self.set_info_message("", msg, "yellow")
                else:
                    self.ui.transaction_id = (uuid.uuid4().hex)[0:12]                    
                    if action == cfg.sell:
                        ''' Sell order'''
                        self.ui.process_sell_limit_order(shareName, size, limit)
                        ''' Buy order'''
                    elif action == cfg.buy:
                        self.ui.process_buy_limit_order(shareName, size, limit)
            elif orderType == cfg.market:
                ''' MARKET order'''
                self.ui.transaction_id = (uuid.uuid4().hex)[0:12]
                if action == cfg.sell:
                    ''' Sell order'''
                    self.ui.process_sell_market_order(shareName, size)
                elif action == cfg.buy:
                    self.ui.process_buy_market_order(shareName, size)
            self.ui.transaction_id = ''
		

    def get_share_infos(self, shareName: str) -> int:
      ''' Return info about the share, Quantity, name, and location
					in the list of shares.
      '''
      share_count = len(self.ui.account['shares'])
      found = False
      index = -1
      share_infos = {'share':'', 'index':-1}
      while found != True and index < share_count:
        if self.ui.account['shares'][index]['name'] == shareName:
            found = True
            share_infos['share'] = self.ui.account['shares'][index]
            share_infos['index'] = index+1
        index += 1      
      return share_infos
    
    def process_sell_limit_order(self, share: str, size, limit: float) -> None:
        ''' Execute a sell limit order only if the share price is
            higher than or equal to <limit>.
            If no shares is over the limit, add a new offer to the market.
        '''              
        is_operation_processed = False
        index = fct.get_limit_max_ask_index(share, limit, self.ui.market)
        share_balance = 0
        idx = -1
        if index != -1:          
            ''' Get the account share balance'''
            share_balance = self.get_share_infos(share)['share']['amount']
            if fct.is_sellable(share_balance, size):
                ''' Execute order'''
                ''' 1. Remove the amount from the share balance account'''
                new_account_share_balance = share_balance - int(size)
                print(new_account_share_balance)
                self.ui.account['shares'][idx]['amount'] = new_account_share_balance
                ''' 2. Remove the associated ASK offer from the market'''
                new_market_size = int(self.market[index]['size']) - int(size)
                self.market[index]['size'] = new_market_size
                ''' 3. Update the currency balance of the account'''
                current_account_currency_balance = float(self.ui.account['balance'])
                market_share_price = float(self.ui.market[index]['price'])
                new_account_currency_balance = current_account_currency_balance + market_share_price * int(size)
                self.ui.account['balance'] = round(new_account_currency_balance, 2)
                ''' 4. Completely remove the offer from market amount 
                		if the remining amount equal to 0 after operation.
                '''            
                if int(self.market[index]['size']) == 0:                
                    self.ui.market.remove(self.ui.market[index])
                is_operation_processed = True
            else:
                msg = " Unsufficient share balance. Order not executed."
                self.set_info_message(self.ui.transaction_id, msg, "yellow")
        else:
            ''' If no offer at the limit was found then
                add a new offer on the market
            '''
            self.ui.market.append({'shareName': 'ShareX', 'offer': 'BID', 'price': limit, 'size': size})
            msg = " No matching offer found. Your offer is added to market."
            self.set_info_message(self.ui.transaction_id, msg, "yellow")
            ''' Remove the amount from the share balance account'''
            share_balance = self.get_share_infos(share)['share']['amount']
            new_account_share_balance = share_balance - int(size)
            print(new_account_share_balance)
            self.ui.account['shares'][idx]['amount'] = new_account_share_balance
        self.ui.update_context()
        return is_operation_processed
    
    def process_sell_market_order(self, share: str, size: int) -> int:
        is_operation_processed = False
        index = fct.get_max_ask_index(share, self.ui.market)
        share_balance = 0
        found = False
        share_count = len(self.ui.account['shares'])
        idx = -1
        print("is salable")
        while found != True and idx < share_count:
            if self.ui.account['shares'][idx]['name'] == share:
                share_balance = int(self.ui.account['shares'][idx]['amount'])
                found = True
            idx += 1
        if fct.is_sellable(share_balance, size):
            ''' Execute the order'''
            ''' 1. Remove the amount from the share balance account'''
            
            new_account_share_balance = share_balance - int(size)
            self.ui.account['shares'][idx]['amount'] = new_account_share_balance
            print(new_account_share_balance)        
            ''' 2. Remove the associated offer from the market'''
            new_market_size = int(self.market[index]['size']) - int(size)
            self.market[index]['size'] = new_market_size
            ''' 3. Update the currency balance of the account'''
            current_account_currency_balance = float(self.ui.account['balance'])
            market_share_price = self.ui.market[index]['price']
            new_account_currency_balance = current_account_currency_balance + market_share_price * int(size)
            self.ui.account['balance'] = round(new_account_currency_balance, 2)
            ''' 4. Completely remove the offer from market amount 
                if the remining amount equal to 0 after operation.'''            
            if int(self.market[index]['size']) == 0:                
                self.ui.market.remove(self.ui.market[index])
            msg = " Order executed successfully."
            self.set_info_message(self.ui.transaction_id, msg, "yellow")
            is_operation_processed = True            
        else:   
            msg = " Order not executed. Unsufficient balance."
            self.set_info_message(self.ui.transaction_id, msg, "yellow")        
        self.ui.update_context()    
        return is_operation_processed
 
    def process_buy_market_order(self, share: str, size: int) -> int:
        ''' buy shares on the market by executing a market buy order.
        '''
        is_operation_processed = False
        index = fct.get_min_bid_index(share, self.ui.market)
        price = float(self.ui.market[index]['price'])        
        sizeprice = float(size) * price
        account_balance = float(self.ui.account['balance'])
        market_size = self.ui.market[index]['size']
        market_price = self.ui.market[index]['price']
        
        ''' Remove share amount from the market'''
        if fct.is_buyable(sizeprice, account_balance, market_size, market_price):
            current_market_size = market_size
            current_market_size -= float(size)
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
                    self.ui.account['shares'][idx]['amount'] += float(size)
                    found = True
                    is_operation_processed = True
                idx += 1
        else:
           is_operation_processed = False
           msg = " Unsufficient balance."
           self.set_info_message(self.ui.transaction_id, msg, "yellow")
        ''' Displays confirmation message'''
        if is_operation_processed:
            msg = " Order executed successfully."
            self.set_info_message(self.ui.transaction_id, msg, "yellow")                    
        else:
            msg = " Order not executed."
            self.set_info_message(self.ui.transaction_id, msg, "yellow")   
        self.ui.update_context()
        return is_operation_processed
        
    def process_buy_limit_order(self, share: str, size: int, limit: float) -> None:
        ''' Execute a buy limit order only if the share price is 
            lower than or equal to <limit>.
            If no shares is under the limit, add a new offer to the market.
        '''
        is_opreation_processed = False
        index = fct.get_limit_min_bid_index('ShareX', limit, self.ui.market)        
        if index != -1:
            ''' If an offer at the limit was found, then execute the order'''
            price = float(self.ui.market[index]['price'])
            sizeprice = float(size) * price
            account_balance = float(self.ui.account['balance'])
            market_size = self.ui.market[index]['size']
            market_price = self.ui.market[index]['price']
            ''' Remove share amount from market'''
            if fct.is_buyable(sizeprice, account_balance, market_size, market_price):                
                market_size -= float(size)
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
                        self.ui.account['shares'][idx]['amount'] += float(size)
                        found = True
                        is_opreation_processed = True
                        msg = " Order executed successfully."
                        self.set_info_message(self.ui.transaction_id, msg, "yellow")
                    idx += 1
            else:
                msg = " Unsufficient balance. Order not executed."
                self.set_info_message(self.ui.transaction_id, msg, "yellow")
        else:
            ''' If not offer at the limit was found then
                add a new offer on the market
            '''
            self.ui.market.append({'shareName': 'ShareX', 'offer': 'ASK', 'price': limit, 'size': size})
            msg = " No matching offer found. Your offer is added to market."
            self.set_info_message(self.ui.transaction_id, msg, "yellow")
        self.ui.update_context()
        return is_opreation_processed

if __name__ == '__main__':
    app = QApplication(sys.argv)
    input_file_name = "input/data.csv"
    ex = Simulator()
    sys.exit(app.exec_())