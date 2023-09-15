import csv

def get_min_bid_index(share: str, data) -> int:
    ''' Return the index of the less expansive share inside the
        table representing the market.
    '''
    min_bid = data[0]['price']
    index = -1
    for row in data:
        index +=1        
        val = row['price']        
        if row['offer'] == "BID" and val < min_bid and row['shareName'] == share:
            min_bid = val        
    return index

def is_buyable(cost: float, balance: float, availableSize: int, marketPrice: float) -> bool:
    ''' Return true if the account balance is sufficient
    to buy the amount and if the market can provide this amount.
    Return false otherwise
    '''
    return balance - cost > 0 and availableSize * marketPrice > cost

def is_sellable(size: int) -> bool:
    ''' Return true if the account balance has enough
        shares to sell the amount specified. Return false
        otherwise.
    '''
    return size > 0 

def load_data(filename) -> None:
    ''' Loading data from csv file '''
    data = []
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        rows = csv.DictReader(f)
        for row in rows:                
            data.append({'shareName': 'ShareX', 'offer': row['offer'], 'price': float(row['price']), 'size': int(row['size'])})
    return data