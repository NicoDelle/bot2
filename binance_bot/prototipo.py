from db_creator import db_from_csv

symbol = 'BTCUSDT'
interval = '15m'
limit = 1000

db = db_from_csv(symbol, interval, limit)

print(db.head())
print('*'*25)
print(db.tail())