import requests
from pathlib import Path
import json
from time import sleep
from pickleUtil import pickleSave, pickleLoad
import numpy as np

def getWarframeMarketOrders(itemUrlName=str):
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
        response = requests.get(f'https://api.warframe.market/v1/items/{itemUrlName}/orders')
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
    itemSellPriceAndQuantity = [{'price': d['platinum'],
                                 'quantity': d['quantity']} for d in orderList]

    # Calculate average item price
    for d in itemSellPriceAndQuantity:    
        totalPrice += d['price'] * d['quantity']
        totalQuantity += d['quantity']
    avgPrice = totalPrice / totalQuantity

    # Return average price
    return avgPrice

def updateMarketItemList():
    # Avoid spamming API by sleeping 1 second once every time the API is called
    sleep(1)

    # Request API for item list, raise exception if unsuccessful status code
    response = requests.get('https://api.warframe.market/v1/items')
    if response.status_code != 200:
        raise Exception('Status Code: ', response.status_code)

    # Create variables to use from the response content
    jsonString = str(response.content)[2:-1].replace('\\', '') # Manually remove escaped char since idk what causes them
    jsonList = json.loads(jsonString)

    # Extract just the list of items from the json file
    itemList = [i for i in jsonList['payload']['items']]

    # Save extracted data for later loading
    pickleSave(itemList, 'transformedItemList', './data')

def loadMarketItemList():
    path = Path('./data/transformedItemList.pkl')
    if not path.exists():
        updateMarketItemList()
    
    return pickleLoad('transformedItemList', './data')

def findItemsInList(query, itemList):
    return [{'item_name': x['item_name'],
            'url_name': x['url_name'],
            'id': x['id']} for x in itemList if query in x['item_name']]

def queryPricesOf(*queries):
    query = []
    itemList = loadMarketItemList()

    rawQuery = list(np.array([findItemsInList(i, itemList) for i in queries]).flatten())
    print(rawQuery)

    for item in rawQuery:
        if item not in query:
            query.append(item)


    for item in query:
        orders = getWarframeMarketOrders(item['url_name'])
        price = getItemAveragePrice(orders)
        item['price'] = price

    return query