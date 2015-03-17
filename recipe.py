from bs4 import BeautifulSoup
import urllib2
import nltk
import sys
import json
import re
import string
import operator
import numpy
from random import randint
import copy


def debugPrompt():
    print " "
    xxx = input('ENTER \'3\' to STOP: ')
    if xxx == 3:
        exit(0)

def JSONlistPrint(JSONfile):
    
    str = ", "
    
    print("\nURL: " + JSONfile["url"])
    print("\nCooking methods: " + str.join(JSONfile["cooking methods"]))
    print("Primary cooking method: " + JSONfile["primary cooking method"])
    print("Cooking tools: " + str.join(JSONfile["cooking tools"]))
    print("\nIngredients:")

    ingredients = JSONfile["ingredients"]

    for ingredient in ingredients:
        print("\nName: " + str.join(ingredient["name"]))
        print("Preparation: " + str.join(ingredient["preparation"]))
        print("Descriptor: " + str.join(ingredient["descriptor"]))
        print("Measurement: " + str.join(ingredient["measurement"]))
        print("Prep description: " + str.join(ingredient["prep-description"]))
        print("Quantity: " + str.join(ingredient["quantity"]))
        
    print("\nDone")

def JSONtablePrint(JSONfile):

    str = ", "

    print("\nURL: " + JSONfile["url"])
    print("\nCooking methods: " + str.join(JSONfile["cooking methods"]))
    print("Primary cooking method: " + JSONfile["primary cooking method"])
    print("Cooking tools: " + str.join(JSONfile["cooking tools"]))
    print("\nIngredients:")

    ingredients = JSONfile["ingredients"]

    print('{:^30}'.format('Name:') + '{:^30}'.format('Preparation:') + '{:^30}'.format('Descriptor:') +
          '{:^10}'.format('Measurement:') + '{:^30}'.format('Prep description:') + '{:^10}'.format('Quantity:'))

    for ingredient in ingredients:
        print('{:^30}'.format(str.join(ingredient["name"])) + '{:^30}'.format(str.join(ingredient["preparation"])) +
              '{:^30}'.format(str.join(ingredient["descriptor"])) + '{:^10}'.format(ingredient["measurement"]) +
              '{:^30}'.format(str.join(ingredient["prep-description"])) + '{:^10}'.format(ingredient["quantity"]))

    print("\nDone")

def getRecipe(url):
    content = urllib2.urlopen(url).read()
    soup = BeautifulSoup(content)
    amountRaw = soup.find_all('span', attrs={'class':'ingredient-amount'})
    ingredientRaw = soup.find_all('span', attrs={'class':'ingredient-name'})
    directionsRaw = soup.find_all('span', attrs={'class':'plaincharacterwrap break'})

    amounts = []
    ingredients = []
    directions = []
    
    for element in amountRaw:
        amounts.append(element.decode_contents(formatter="html"))
    for element in ingredientRaw:
        ingredients.append(element.decode_contents(formatter="html"))
    for element in directionsRaw:
        directions.append(element.decode_contents(formatter="html"))
        
    for i in range(len(ingredients)):
        print(amounts[i] + " " + ingredients[i] )

    for i in range(len(directions)):
        print(str(i+1)+ ". " + directions[i])

##def getIngredients(url):
##    content = urllib2.urlopen(url).read()
##    soup = BeautifulSoup(content)
##    amountRaw = soup.find_all('span', attrs={'class':'ingredient-amount'})
##    ingredientRaw = soup.find_all('span', attrs={'class':'ingredient-name'})
##
##    returnDict = {}
##    
##    for i in range(len(ingredientRaw)):
##        returnDict[ingredientRaw[i].decode_contents(formatter="html")] = amountRaw[i].decode_contents(formatter="html")
##
##    return returnDict    

##def getIngredients(url):
##    content = urllib2.urlopen(url).read()
##    soup = BeautifulSoup(content)
##    amountRaw = soup.find_all('span', attrs={'class':'ingredient-amount'})
##    ingredientRaw = soup.find_all('span', attrs={'class':'ingredient-name'})
##
##    returnList = []
##    returnList.append([])
##    returnList.append([])
##
##    if len(ingredientRaw) > 2:
##        for i in range(len(amountRaw)-1):
###            if i < len(amountRaw):
##            returnList[0].append(amountRaw[i].decode_contents(formatter="html"))
##            returnList[1].append(ingredientRaw[i].decode_contents(formatter="html"))
##
##    return returnList



def getDirections(url):
    content = urllib2.urlopen(url).read()
    soup = BeautifulSoup(content)
    directions = []
    directionsRaw = soup.find_all('span', attrs={'class':'plaincharacterwrap break'})
    for element in directionsRaw:
        directions.append(nltk.sent_tokenize(element.decode_contents(formatter="html")))
    return directions


def getServingSize(url):
    content = urllib2.urlopen(url).read()
    soup = BeautifulSoup(content)
    serving = soup.find('span', attrs={'itemprop':'recipeYield'}).decode_contents(formatter="html")
    return serving


def getTime(url):
    content = urllib2.urlopen(url).read()
    soup = BeautifulSoup(content)
    prep = soup.find('time', attrs={'id':'timeTotal'})['datetime']
    prep = prep[2:]
    count = 0
    count += int(prep[0:prep.index("H")])*60 + int(prep[prep.index("H")+1:prep.index("M")])
    return count


def getNutritionalData(ingredient):
    returnList = []
    url = "https://api.nutritionix.com/v1_1/search/"+  ingredient.replace(" ","%20") +"?fields=item_name%2Citem_id%2Cbrand_name%2Cnf_calories%2Cnf_sodium%2Cnf_serving_size_unit%2Cnf_total_fat&appId=76cb91ea&appKey=06fffb14b509b9547fbe293350329289"
    response = urllib2.urlopen(url);
    data = json.loads(response.read())
    try:
        calories = data['hits'][0]['fields']['nf_calories']
        fat = data['hits'][0]['fields']['nf_total_fat']
        sodium = data['hits'][0]['fields']['nf_sodium']
        name = data['hits'][0]['fields']['item_name']
        
        nameList = name.split("-")
        nameListLength = len(nameList)
        returnList.append(calories)
        returnList.append(fat)
        returnList.append(sodium)
        if (nameListLength > 1):
            unit = nameList[nameListLength-1]
            returnList.append(unit)
        return returnList
    except IndexError:
        return []


def getFatRatio(ingredient):
    data = getNutritionalData(ingredient)
    try:
        if (numpy.sum([data[0],data[1]]) == 0):
            return 0
    except IndexError:
        return 0
    try:
        ret = data[1]/data[0]
        return ret
    except ZeroDivisionError:
        print(ingredient)
        return 0


def getSodiumRatio(ingredient):
    data = getNutritionalData(ingredient)
    try:
        if (numpy.sum([data[0],data[2]]) == 0):
            return 0
    except IndexError:
        return 0
    try:
        ret = data[2]/data[0]
        return ret
    except ZeroDivisionError:
        return 9999

def getRelatedRecipes(url):
    if (len(urls) < 1000):
        content = urllib2.urlopen(url).read()
        soup = BeautifulSoup(content)
        recipes = soup.find('div', attrs={'class':'detail-section more-recipes'}).find_all('a')
        links = []
        for i in range(len(recipes)):
            link = "http://allrecipes.com" + recipes[i]['href']
            if (link not in urls and i !=0 ):
                urls.append(link)
                print(link)
                getRelatedRecipes(link)

def getCat(ingredient):
    url = "http://en.wikipedia.org/w/api.php?action=query&prop=extracts|info&exintro&titles="+ ingredient.replace(" ","%20")+"&format=json&explaintext&redirects&inprop=url&indexpageids"
    response = urllib2.urlopen(url)
    data = json.loads(response.read())
    pageId = data['query']['pageids'][0]
    try:
        extract = data['query']['pages'][pageId]['extract']
        meat = extract.count('meat')
        vegetable = extract.count('vegetable')
        fruit = extract.count('fruit')
        dairy = extract.count('dairy') + extract.count('cheese')
        starch = extract.count('starch') + extract.count('wheat') + extract.count('grain') + extract.count('flour')
        spice = extract.count('spice')
        bean = extract.count('bean')
        sauce = extract.count('sauce')
        fish = extract.count('fish')

        results = []
        results.append(meat)
        results.append(vegetable)
        results.append(fruit)
        results.append(dairy)
        results.append(starch)
        results.append(spice)
        results.append(bean)
        results.append(sauce)
        results.append(fish)

        maxR = max(results)
        
        categories = ['Meat','Vegetable','Fruit','Dairy','Starch','Spice','Bean', 'Sauce','Fish']
        if (numpy.sum(results) == 0):
            return 'Other'
    except KeyError:
        return 'Unparsed'
    return categories[results.index(maxR)]

def transformVeg(data):
    returnData = copy.deepcopy(data)
    for i in range(len(data['ingredients'])):
        name = (data['ingredients'][i]['name'][0])
        print(name)
        prepList = data['ingredients'][i]['preparation']
        if (getCat(name) == 'Meat'):
            if ('ground' in prepList or 'ground' in name):
                returnData['ingredients'][i]['name'] = ['tofu']
                if ('ground' in prepList):
                    returnData['ingredients'][i]['preparation'][prepList.index('ground')] = ['crumbled']
                else:
                    prepList.append('crumbled')
            elif ('sliced' in prepList):
                returnData['ingredients'][i]['name'] = ['tofurkey']
            elif ('chopped' in prepList or 'shredded' in prepList or 'cubed' in prepList or 'cube' in prepList):
                returnData['ingredients'][i]['name'] = ['tofu']
            else:
                returnData['ingredients'][i]['name'] = ['veggie burger']
        elif (getCat(name) == 'Fish'):
                returnData['ingredients'][i]['name'] = ['veggie burger']

    return(returnData)


def transformFromVeg(data):
    returnData = copy.deepcopy(data)
    for i in range(len(data['ingredients'])):
        name = (data['ingredients'][i]['name'][0])
        print(name)
        prepList = data['ingredients'][i]['preparation']
        if ('tofu' in name and 'crumbled' in prepList):
                returnData['ingredients'][i]['name'] = 'chicken'
                returnData['ingredients'][i]['preparation'][prepList.index('crumbled')] = ['ground']
        elif ('chopped' in prepList or 'shredded' in prepList or 'cubed' in prepList or 'cube' in prepList and 'tofu' in name):
                returnData['ingredients'][i]['name'] = ['pork']
        else:
            returnData['ingredients'].append({'name':['chicken'],'quantity':[8],'measurement':['ounces'],'descriptor':[],'preparation':[],'prep-description':[]})
    return(returnData)

def transformDairy(data):
    returnData = copy.deepcopy(data)
    cheeses = ['Asiago', 'Carmody', 'Cheddar', 'Colby', 'Cotija', 'Edam', 'Enchilado', 'Fontina', 'Gouda', 'Havarti', 'Longhorn', 'Port Salut' , 'St. George', 'Syrian']
    for i in range(len(data['ingredients'])):
        name = (data['ingredients'][i]['name'][0])
        print(name)
        prepList = data['ingredients'][i]['preparation']
        if (getCat(name) == 'Dairy'):
            if ('cheese' in name):
                returnData['ingredients'][i]['name'] = [cheeses[randint(0,len(cheeses)-1)]]
            if ('milk' in name):
                returnData['ingredients'][i]['name'] = ['soy milk']
            if ('cream' in name):
                returnData['ingredients'][i]['name'] = ['soy cream']
            if ('half' in name):
                returnData['ingredients'][i]['name'] = ['soy cream']
            if ('yogurt' in name):
                returnData['ingredients'][i]['name'] = ['greek yogurt']
            if ('butter' in name):
                returnData['ingredients'][i]['name'] = ['margarine']
            if ('ice cream' in name):
                returnData['ingredients'][i]['name'] = ['soy ice cream']
                
    return(returnData)

def tranformFromDairy(data):
    returnData = copy.deepcopy(data)
    cheeses = ['Asiago', 'Carmody', 'Cheddar', 'Colby', 'Cotija', 'Edam', 'Enchilado', 'Fontina', 'Gouda', 'Havarti', 'Longhorn', 'Port Salut' , 'St. George', 'Syrian']
    for i in range(len(data['ingredients'])):
        name = (data['ingredients'][i]['name'][0])
        print(name)
        prepList = data['ingredients'][i]['preparation']
        if (getCat(name) == 'Dairy'):
            if ('soy milk' in name):
                returnData['ingredients'][i]['name'] = ['milk']
            if ('soy cream' in name):
                returnData['ingredients'][i]['name'] = ['cream']
            if ('greek yogurt' in name):
                returnData['ingredients'][i]['name'] = ['yogurt']
            if ('margarine' in name):
                returnData['ingredients'][i]['name'] = ['butter']
            if ('soy ice cream' in name):
                returnData['ingredients'][i]['name'] = ['ice cream']
                
    return(returnData)


def transformKid(data):
    returnData = copy.deepcopy(data)
    vegList = ['tomatoes', 'onion', 'carrots', 'peas', 'corn', 'lettuce']
    for i in range(len(data['ingredients'])):
        name = (data['ingredients'][i]['name'][0])
        print(name)
        prepList = data['ingredients'][i]['preparation']
        if (getCat(name) == 'Spice' and 'salt' not in name and 'black pepper' not in name):
            del returnData['ingredients'][i]
        if (getCat(name) == 'Vegetable' and name not in vegList):
            del returnData['ingredients'][i]
        if (getCat(name) == 'Fish'):
            returnData['ingredients'][i]['name'] = ['chicken breast']
            returnData['ingredients'][i]['preparation'] = []

    return(returnData)


def transformPizza(data):
    returnData = copy.deepcopy(data)

    deleteIndices = []
    for i in range(len(data['ingredients'])):
        name = (data['ingredients'][i]['name'][0])
        if (getCat(name) != 'Meat' and getCat(name) != 'Spice' and getCat(name) != 'Vegetable' and getCat(name) != 'Fish' ):
            deleteIndices.append(i)

    for i in sorted(deleteIndices,reverse=True):
        del returnData['ingredients'][i]
    
    returnData['ingredients'].append({'name':['bread flour'],'quantity':['4'],'measurement':['cups'],'descriptor':[],'preparation':[],'prep-description':[]})
    returnData['ingredients'].append({'name':['sugar'],'quantity':['1'],'measurement':['teaspoons'],'descriptor':[],'preparation':[],'prep-description':[]})
    returnData['ingredients'].append({'name':['yeast'],'quantity':['1'],'measurement':['envelope'],'descriptor':['instant','dry'],'preparation':[],'prep-description':[]})
    returnData['ingredients'].append({'name':['salt'],'quantity':['2'],'measurement':['teaspoons'],'descriptor':['kosher'],'preparation':[],'prep-description':[]})
    returnData['ingredients'].append({'name':['water'],'quantity':['1.5'],'measurement':['cups'],'descriptor':[''],'preparation':['110'],'prep-description':['degrees F']})
    returnData['ingredients'].append({'name':['olive oil'],'quantity':['2'],'measurement':['tablespoons'],'descriptor':[],'preparation':[],'prep-description':[]})
    returnData['ingredients'].append({'name':['olive oil'],'quantity':['2'],'measurement':['teaspoons'],'descriptor':[],'preparation':[],'prep-description':[]})
    returnData['ingredients'].append({'name':['garlic'],'quantity':['1'],'measurement':['clove'],'descriptor':[],'preparation':['crushed'],'prep-description':[]})
    returnData['ingredients'].append({'name':['tomato puree'],'quantity':['1'],'measurement':['can (28 ounces)'],'descriptor':[],'preparation':[],'prep-description':[]})
    returnData['ingredients'].append({'name':['marjoram'],'quantity':['1'],'measurement':['teaspoon'],'descriptor':[],'preparation':['dried'],'prep-description':[]})
    returnData['ingredients'].append({'name':['basil'],'quantity':['1'],'measurement':['teaspoon'],'descriptor':[],'preparation':['dried'],'prep-description':[]})
    returnData['ingredients'].append({'name':['salt'],'quantity':['1'],'measurement':['teaspoon'],'descriptor':['to taste'],'preparation':[],'prep-description':[]})  
    returnData['ingredients'].append({'name':['black pepper'],'quantity':['1'],'measurement':['teaspoon'],'descriptor':['to taste'],'preparation':[],'prep-description':[]})
    returnData['ingredients'].append({'name':['mozzarella cheese'],'quantity':['8'],'measurement':['ounces'],'descriptor':[''],'preparation':[],'prep-description':[]})

    return(returnData)

def transformLowFat(data):
    returnData = copy.deepcopy(data)
    ratioList = {}
    for i in range(len(data['ingredients'])):
        if (getFatRatio(data['ingredients'][i]['name'][0]) > .06):
            quantity = data['ingredients'][i]['quantity'][0]
            quantity = float(quantity) / 2            

    for key,value in ratioList.iteritems():
        print(key, " ", value)
    
    return(returnData)


def transformLowSalt(data):
    returnData = copy.deepcopy(data)
    ratioList = {}
    for i in range(len(data['ingredients'])):
        if (getSodiumRatio(data['ingredients'][i]['name'][0]) > 3.5):
            quantity = data['ingredients'][i]['quantity'][0]
            quantity = str(float(quantity) / 2)

    for key,value in ratioList.iteritems():
        print(key, " ", value)
    
    return(returnData)

# main function - takes entire list (ex, all of quantities.txt)

def listQuantityParse(inputList):
    
    length = len(inputList)
    outputList = inputList

    for i in range(0, length):
        outputList[i] = stringQuantityParse(inputList[i])

    return outputList

# helper functions

# takes a string - each string formatted like one line of quantities.txt
def stringQuantityParse(inputString):

    splitInputString = inputString.split()

    # assume first word is a number
    splitInputString[0] = fractionStringToFloat(splitInputString[0])
    
    # check if second word is fraction (second part of mixed number)
    if len(inputString) == 1:
        return str(inputString[0]) + ' count'
    elif numberCheck(splitInputString[1]):
        number = splitInputString[0]
        fraction = splitInputString[1]
        quantity = number + fractionStringToFloat(fraction)
        unit = splitInputString[2]
    else:
        quantity = splitInputString[0]
        unit = splitInputString[1]

    outputArray = measurementParse(quantity, unit)
    stringNumber = str(outputArray[0])

    if len(stringNumber) > 5:
        stringNumber = stringNumber[0:5]
        
    result = stringNumber + " " + outputArray[1]
    return result

def fractionStringToFloat(inputFraction):

    splitFraction = None

    if "/" in inputFraction:
        splitFraction = inputFraction.split("/", 1)
        numerator = float(splitFraction[0])
        denominator = float(splitFraction[1])
        outputDouble = numerator/denominator
    else:
        outputDouble = float(inputFraction)

    return outputDouble

def mixedFractionToFloat(inputMixedFraction):

    number = inputMixedFraction[0]
    fraction = inputMixedFraction[1]

    outputFloat = float(number) + fractionStringToFloat(fraction)
    return outputFloat

def numberCheck(inputWord):

    if re.match('\d', inputWord) == None:
        return False
    else:
        return True

        
def measurementParse(inputQuantity, inputUnit):

    # neither - unit quantity
    outputUnit = 'count'
    #outputQuantity = inputQuantity

    # volume - to cubic cm
    if re.match('tablespoon[s]?|tbsp' , inputUnit) != None:
        outputUnit = 'tablespoon(s)'
        #outputQuantity = inputQuantity * 14.7867648
        
    if re.match('teaspoon[s]?|tsp' , inputUnit) != None:
        outputUnit = 'teaspoon(s)'
        #outputQuantity = inputQuantity * 4.92892159
        
    if re.match('cup[s]?' , inputUnit) != None:
        outputUnit = 'cup(s)'
        #outputQuantity = inputQuantity * 236.588236

    if re.match('mL[s]?|ml[s]?|milliliter[s]?' , inputUnit) != None:    
        outputUnit = 'milliliter(s)'
        #outputQuantity = inputQuantity

    if re.match('l[s]?|L[s]?|liter[s]?' , inputUnit) != None:    
        outputUnit = 'liter(s)'
        #outputQuantity = inputQuantity * 1000
        

    # mass/weight - to grams
    if re.match('pound[s]?|lb[s]?' , inputUnit) != None:
        outputUnit = 'pound(s)'
        #outputQuantity = inputQuantity * 453.592

    if re.match('ounce[s]?|oz[s]?' , inputUnit) != None:  
        outputUnit = 'ounce(s)'
        #outputQuantity = inputQuantity * 28.3495
        
    if re.match('kilogram[s]?|kg[s]?' , inputUnit) != None:
        outputUnit = 'kilogram(s)'
        #outputQuantity = inputQuantity * 1000

    if re.match('gram[s]?|g[s]?' , inputUnit) != None:
        outputUnit = 'gram(s)'
        #outputQuantity = inputQuantity
          
    return [inputQuantity, outputUnit] 

def LoadKnowledge(filename,lst):
    with open(filename) as f:
        line = f.readlines()
    for lin in line:
        lin = lin.rstrip('\r\n')
        lst.append(lin)

def stripPunctuation(inText):
  outText = inText
  for c in string.punctuation:
      outText = outText.replace(c,"")
  return outText

def validMatch(phrase,s):
    bOn = False
    for i in range(0,s.start(0)):
        if phrase[i] == '[':
            bOn = True
        if phrase[i] == ']':
            bOn = False
    return not bOn

def wrapRemaining(phrase):
    temp = ""
    if phrase[0] != '[':
        temp = '['
    bOn = False
    for i in range(0,len(phrase)-1):
        if phrase[i] == '[':
            bOn = True
        if phrase[i] == ']':
            bOn = False
        if not bOn and phrase[i] == ' ':
            if phrase[i-1] != ']':
                temp = temp + ']'
            temp = temp + ' '
            if phrase[i+1] != '[':
                 temp = temp + '['
        if phrase[i] != ' ' or bOn:
            temp = temp + phrase[i]
    return temp
            

def parseIngredients(phrase):
    listFood = list()
    listDesc = list()
    listPrep = list()
    listPrepDesc = list()
    listIgnore = list()

    LoadKnowledge('c:\\dwd\\recipes\\foods.txt',listFood)
    LoadKnowledge('c:\\dwd\\recipes\\desc.txt',listDesc)
    LoadKnowledge('c:\\dwd\\recipes\\preps.txt',listPrep)
    LoadKnowledge('c:\\dwd\\recipes\\prepdesc.txt',listPrepDesc)
    LoadKnowledge('c:\\dwd\\recipes\\ignores.txt',listIgnore)

    listFood.sort(lambda x,y: cmp(len(y), len(x)))
    listDesc.sort(lambda x,y: cmp(len(y), len(x)))
    listPrep.sort(lambda x,y: cmp(len(y), len(x)))
    listPrepDesc.sort(lambda x,y: cmp(len(y), len(x)))
    listIgnore.sort(lambda x,y: cmp(len(y), len(x)))

    listBig = list()
    for elem in listFood:
        listBig.append(elem)
    for elem in listDesc:
        listBig.append(elem)
    for elem in listPrep:
        listBig.append(elem)
    for elem in listPrepDesc:
        listBig.append(elem)
    for elem in listIgnore:
        listBig.append(elem)
    listBig.sort(lambda x,y: cmp(len(y), len(x)))

    phrase = stripPunctuation(phrase)
    phrase = phrase.lower()
    phrase = phrase + "  "

    for elem in listBig:
        elem1 = elem + ' '
        s = re.search(elem1,phrase)
        if s:
            if validMatch(phrase,s):
                old = elem
                new = '[' + elem + ']'
                phrase = phrase.replace(old,new)
    phrase = wrapRemaining(phrase)

    food = list()
    desc = list()
    prep = list()
    pdsc = list()
    
    tokens = phrase.split("]")
    for t in tokens:
        if len(t) > 1:
            s = t.replace(" [","")
            s = s.replace("[","")
            if s in set(listFood):
                print '          food: ',s
                food.append(s)
            if s in set(listDesc):
                print '          desc: ',s
                desc.append(s)
            if s in set(listPrep):
                print '          prep: ',s
                prep.append(s)
            if s in set(listPrepDesc):
                print '          pdsc: ',s
                pdsc.append(s)
                
    return [food,desc,prep,pdsc]

def main():
    lines = [line.strip() for line in open('c:\\python27\\recipe\\urls.txt')]
    for i in range(0,3):
        url = lines[i]

        print "Getting recipe for: ",url
##        listI = getIngredients(url)
        dictI = getIngredients(url)
        listD = getDirections(url)

        print ' '

        jsonObj = {"url":url,
                   "ingredients": [],
                   "primary cooking method": "",
                   "cooking methods": [],
                   "cooking tools": [],
                   "directions": []}

        for phrase in dictI.keys():
            qty = dictI[phrase]
            print qty
            meas = stringQuantityParse(qty)
            tokens = meas.split(' ');
            amt = ['unknown']
            units = ['unknown']
            if len(tokens) == 1:
                amt = [tokens[0]]
                units = ['pieces']
            if len(tokens) == 2:
                amt = [tokens[0]]
                units = [tokens[1]]
            print 'phrase = ',phrase
            [food,desc,prep,pdsc] = parseIngredients(phrase)
            jsonObj["ingredients"].append({"name":food, "quantity":amt, "measurement":units, "descriptor":desc, "preparation":prep, "prep-description":pdsc})

        for i in range(0,len(listD)):
            step = listD[i]
            print ' '
            print 'Step',i,':'
            for j in range(0,len(step)):
                direction = step[j]
                print 'direction = ',direction
                jsonObj["directions"].append(direction)

        JSONlistPrint(jsonObj)

        with open('c:\\dwd\\recipes\\recipe.json', 'w') as outfile:
            json.dump(jsonObj, outfile)
        outfile.close()

        debugPrompt()
        
    bContinue = True
    while bContinue:
        jsonTrans = jsonObj
        option = input('enter option number: ')
        if option == 1:
            jsonTrans = transformVeg(jsonObj)
        elif option == 2:
            jsonTrans = transformVeg(jsonObj)
        elif option == 3:
            jsonTrans = transformDairy(jsonObj)
        elif option == 4:
            jsonTrans = tranformFromDairy(jsonObj)
        elif option == 5:
            jsonTrans = transformKid(jsonObj)
        elif option == 6:
            jsonTrans = transformPizza(jsonObj)
        elif option == 7:
            jsonTrans = transformLowFat(jsonObj)
        elif option == 8:
            jsonTrans = transformLowSalt(jsonObj)
        else:
            bContinue = False
        JSONlistPrint(jsonTrans)

        print ' '
        print 'oroginal'
        print ' '
        JSONlistPrint(jsonObj)
                       
        
##    lines = [line.strip() for line in open('c:\\python27\\recipe\\urls.txt')]
##    for i in range(0,500):
##        url = lines[i]
##
##        print "Getting recipe for: ",url
##        listI = getIngredients(url)
##        listD = getDirections(url)

def getIngredients(url):
    content = urllib2.urlopen(url).read()
    soup = BeautifulSoup(content)

    allIngredientElements = soup.findAll('p', attrs={'class':'fl-ing'})

    returnDict = {}
    
    for element in allIngredientElements:
        ingredient = element.find('span', attrs={'class':'ingredient-name'}).decode_contents(formatter="html")
        try:
            amount = element.find('span', attrs={'class':'ingredient-amount'}).decode_contents(formatter="html")
            returnDict[ingredient] = amount

        except:
            returnDict[ingredient] = "N/A"

    return returnDict

if __name__ == "__main__":
    main()
