import requests
from pathlib import Path
import json
from time import sleep

def getWarframeMarketOrders(itemUrlName):
    # Define my file path
    myPath = Path(f'./orders/{itemUrlName}.json')

    # Check if order data is already saved, if not, request it and download it
    if myPath.is_file():
        # Open saved file
        with open(f'./orders/{itemUrlName}.json', 'r') as myFile:
            jsonDict = json.loads(myFile.read())
        
    else:
        # Avoid spamming API by sleeping 1 second once every time the API is called
        sleep(1)

        # Request API for order list, raise exception if unsuccessful status code
        response = requests.get(f"https://api.warframe.market/v1/items/{itemUrlName}/orders")
        if response.status_code != 200:
            raise Exception('Status Code: ', response.status_code)

        # Create variables to use from the response content
        jsonString = str(response.content)[2:-1]
        jsonDict = json.loads(jsonString)
        
        # Save response to orders file
        with open(f'./orders/{itemUrlName}.json', 'w') as outfile:
            outfile.write(jsonString)

    # Extract list of orders
    orderList = [d for d in jsonDict['payload']['orders']]
    
    # Return Orders
    return orderList

def getItemAveragePrice(orderList):
    # Pre-define variables
    totalPrice = 0
    totalQuantity = 0

    # Extract item price and quantity in each order
    itemSellPriceAndQuantity = [{"price": d["platinum"],
                                 "quantity": d["quantity"]} for d in orderList]

    # Calculate average item price
    for d in itemSellPriceAndQuantity:    
        totalPrice += d['price'] * d['quantity']
        totalQuantity += d['quantity']
    avgPrice = totalPrice / totalQuantity

    # Return average price
    return avgPrice

def updateMarketItemList():
    sleep(1)

    # Request API for item list, raise exception if unsuccessful status code
    response = requests.get(f"https://api.warframe.market/v1/items/")
    if response.status_code != 200:
        raise Exception('Status Code: ', response.status_code)



    with open('.data/warframeMarketItemList.json', 'r') as myFile:
        file_data = json.loads(myFile.read())
    payload = [i for i in file_data['myitems']]

    with open('./data/transformedItemList', 'w') as outFile:
        outFile.write(str(payload))
    pass