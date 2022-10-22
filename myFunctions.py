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
        jsonString = response.content.decode()
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
    jsonString = response.content.decode()
    jsonList = json.loads(jsonString)

    # Extract just the list of items from the json file
    itemList = [i for i in jsonList['payload']['items']]

    # Add Additional information like tags to each item
    itemList = addAdditionalInfoToItems(itemList)

    # Save extracted data for later loading
    pickleSave(itemList, 'transformedItemList', './data')

def loadMarketItemList():
    # Designate Path
    path = Path('./data/transformedItemList.pkl')

    # If it doesn't exist, set it up
    if not path.exists():
        updateMarketItemList()
    
    # Load and return itemList from file
    return pickleLoad('transformedItemList', './data')

def allQueriesInKey(queries, key, item):
    # For every query
    for q in queries:
        # Check if it doesn't match item
        if q not in item[key]:
            return False # If there's a query that doesn't match key, return False
    return True # Else return True

def findItemsInList(*queries, itemList, key='item_name'):
    # Build list with every item matching query/ies
    return [x for x in itemList if allQueriesInKey(queries, key, x)]

def queryPricesOf(*queries, itemList, key='item_name'):
    # Pre-set variables
    query = []

    if key == 'item_name':
        # Creates an "or" search that grabs all matching items for each query
        rawQuery = list(np.array([findItemsInList(i, itemList, key) for i in queries]).flatten())

        # Filters the rawQuery by removing any duplicates
        for item in rawQuery:
            if item not in query:
                query.append(item)
    else:
        # Creates an "and" search that grabs all items that match all the query terms
        query = findItemsInList(queries, itemList=itemList, key=key)

    # Gets the current average price for each item and adds it as a key in each item
    for item in query:
        orders = getWarframeMarketOrders(item['url_name'])
        price = getItemAveragePrice(orders)
        item['price'] = price

    return query

def getItemData(itemUrl=str):

    # Defines path
    path = Path(f'./data/itemInfo/{itemUrl}.json')

    # If the path exists, get itemData from that file
    if path.exists():
        with open(path, 'r') as file:
            itemData = json.loads(file.read())
    else: # Else request it from the API
        # 1 second delay before each call so i can't spam API
        sleep(1)

        # Request item info from API
        response = requests.get(f'https://api.warframe.market/v1/items/{itemUrl}')
        # Raise exception if status code doesn't indicate successful
        if response.status_code != 200:
            raise Exception('Status Code: ', response.status_code)

        # Save item info to file
        with open(path, 'w') as outfile:
            outfile.write(response.content.decode())
        # Load to python dictionary to return
        itemData = json.loads(response.content.decode())

    return itemData

def addAdditionalInfoToItems(itemList):
    # Initialise pre-set variables
    listIndex = 0

    for item in itemList:
        
        # Get item info i'm after which is in ['items_in_set']
        itemInfo = getItemData(item['url_name'])['payload']['item']['items_in_set']

        # If there is more than 1 item in "items_in_set", use the one that matches what i searched 
        if len(itemInfo) > 1:
            for e, item in enumerate(itemInfo):
                if item['url_name'] == item['url_name']:
                    listIndex = e
                    break

        # Attempt to add each type of info to item, if it doesn't exist, just skip
        item['tags'] = itemInfo[listIndex]['tags']
        try:
            item['subtypes'] = itemInfo[listIndex]['subtypes']
        except:
            pass
        try:
            item['set_root'] = itemInfo[listIndex]['set_root']
        except:
            pass
        try:
            item['rarity'] = itemInfo[listIndex]['rarity']
        except:
            pass
    return itemList