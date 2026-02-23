import yfrlt

def on_price_update(data):
    print(data.day_volume, data.timestamp, data.price, data.day_low, data.day_high)

client = yfrlt.Client()
client.subscribe(['ULKER.IS'], on_price_update)
client.start()
# client.stop()





