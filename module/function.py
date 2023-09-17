import csv, datetime

def get_max_ask_index(share: str, data) -> int:
    max_ask = data[0]['price']
    max_ask_index = 0
    index = -1
    for row in data:
        index += 1
        val = row['price']        
        if row['offer'] == "ASK" and val > max_ask and row['shareName'] == share:
            print('inside')
            print(max_ask_index)
            max_ask = val
            max_ask_index = index
    return max_ask_index

def get_limit_min_bid_index(share: str, limit: float, data) ->int:
    ''' Return the index of the less expansive share <share> of the market
        with a value lower than or equal to <limit> 
    '''
    limit_min_bid = limit
    limit_min_bid_index = -1
    index = -1
    for row in data:
        index += 1
        val = row['price']
        if row['offer'] == "BID" and val <= limit_min_bid:
            limit_min_bid = val
            limit_min_bid_index = index
    return limit_min_bid_index

def get_min_bid_index(share: str, data) -> int:
    ''' Return the index of the less expansive share inside the
        table representing the market.
    '''
    min_bid = data[0]['price']
    min_bid_index = -1
    index = -1
    for row in data:
        index +=1        
        val = row['price']        
        if row['offer'] == "BID" and val < min_bid and row['shareName'] == share:
            min_bid = val
            min_bid_index = index
    return min_bid_index

def is_buyable(cost: float, balance: float, availableSize: int, marketPrice: float) -> bool:
    ''' Return true if the account balance is sufficient
    to buy the amount and if the market can provide this amount.
    Return false otherwise
    '''
    return balance - cost > 0 and availableSize * marketPrice > cost

def is_sellable(balance: int, amount: int) -> bool:
    ''' Return true if the account share balance greater
     than the amount to sell '''
    return amount <= balance

def load_data(filename) -> None:
    ''' Loading data from csv file '''
    data = []
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        rows = csv.DictReader(f)
        for row in rows:                
            data.append({'shareName': 'ShareX', 'offer': row['offer'], 'price': float(row['price']), 'size': int(row['size'])})
    return data

def message_date() -> str:
    ''' Formatting date to add in front of log and information messages
    '''
    d = datetime.datetime.now()
    formated_date = d.strftime("%d/%m/%y %H:%M:%S")
    message = formated_date
    return message