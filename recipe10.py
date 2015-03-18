###########################################################################################################
# 
# EECS 337-0
# Recipe Project
# March 18, 2015
#
# GROUP 10:   David Demeter
#             Rahul Matta
#             Sachin Lai
#             Michael Kushnir
#
# File:       recipe11.py
#
###########################################################################################################

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
import pprint

###########################################################################################################
#
# debugPrompt(): paused execution and provides the user with an opportunity to exit
#
###########################################################################################################

def debugPrompt():
    print " "
    xxx = input('ENTER \'3\' to STOP: ')
    if xxx == 3:
        exit(0)

###########################################################################################################
#
# jsonRecipePrint(): prints a quasi-english version of a parsed or transformed recips
#
###########################################################################################################

def jsonRecipePrint(JSONfile):

    sep = ", "

    print("\n\n\n\n\n")

    print("\nURL: " + JSONfile["url"] + "\n")
    print("Cooking methods: " + sep.join(JSONfile["cooking methods"]))
    print("Primary cooking method: " + JSONfile["primary cooking method"])
    print("Cooking tools: " + sep.join(JSONfile["cooking tools"]))
    print("\n===== INGREDIENTS: =====")

    ingredients = JSONfile["ingredients"]
    for ingredient in ingredients:

        # convert numbers in quantity field to strings
        for i in range(len(ingredient["quantity"])):
            ingredient["quantity"][i] = str(ingredient["quantity"][i])

        # construct a list separately instead of outputting anything in case of empty fields
        # empty fields are not added to the list
        outList = []
        if len(ingredient["name"]) > 0:
            outList.append("/".join(ingredient["name"]))
        if len(ingredient["preparation"]) > 0:
            outList.append(" or ".join(ingredient["preparation"]))
        if len(ingredient["descriptor"]) > 0:
            outList.append(" or ".join(ingredient["descriptor"]))
        if len(ingredient["prep-description"]) > 0:
            outList.append("/".join(ingredient["prep-description"]))
        if len(ingredient["quantity"]) > 0:
            outList.append(" or ".join(ingredient["quantity"]) + " " + "/".join(ingredient["measurement"]))
        
        print(sep.join(outList))
        
    print("\n===== DIRECTIONS: =====")

    para = ""
    directions = JSONfile["directions"]
    for d in directions:
        para = para + d + '  '
    print(para)

    print("\nDone")

#########################################################################################################
#
#   getRecipe(): prints an inputted recipe in the form of a url from allrecipes.com in
#                in a human-readable format
#
#########################################################################################################

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

#########################################################################################################
#
#   getIngredients(): returns the ingredients associated with the URL provided
#                    
#########################################################################################################

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


#########################################################################################################
#
#   getDirections(): returns the directions associated with the URL provided
#                    
#########################################################################################################

def getDirections(url):
    content = urllib2.urlopen(url).read()
    soup = BeautifulSoup(content)
    directions = []
    directionsRaw = soup.find_all('span', attrs={'class':'plaincharacterwrap break'})
    for element in directionsRaw:
        directions.append(nltk.sent_tokenize(element.decode_contents(formatter="html")))
    return directions


###########################################################################################################
#
#   getServingSize(): returns the serving size of an inputted recipe in the form of a url from allrecipes.com
#                   
###########################################################################################################


def getServingSize(url):
    content = urllib2.urlopen(url).read()
    soup = BeautifulSoup(content)
    serving = soup.find('span', attrs={'itemprop':'recipeYield'}).decode_contents(formatter="html")
    return serving


###########################################################################################################
#
#   getTime(): returns the total prep + cook time of an inputted recipe in the form of a url from allrecipes.com                    
#
###########################################################################################################

def getTime(url):
    content = urllib2.urlopen(url).read()
    soup = BeautifulSoup(content)
    prep = soup.find('time', attrs={'id':'timeTotal'})['datetime']
    prep = prep[2:]
    count = 0
    count += int(prep[0:prep.index("H")])*60 + int(prep[prep.index("H")+1:prep.index("M")])
    return count


###########################################################################################################
#
#   getNutritionalData(): returns nutrition facts including sodium, fat, and calories of an inputted ingredient 
#                         making use of the nutritionix api
#
###########################################################################################################

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


###########################################################################################################
#
#   getFatRatio(): returns the fat per calorie ratio of an inputted ingredient 
#                    
###########################################################################################################

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
        return 0


###########################################################################################################
#
#   getSodiumRatio(): returns the sodium per calorie ratio of an inputted ingredient 
#                    
#
###################################################################################### 

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

###########################################################################################################
#
#   getRelatedRecipes(): recursively crawls through source code of an inputted allrecipes.com recipe 
#                        to print an arbitrary amount of related recipe urls
#
###########################################################################################################

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


###########################################################################################################
#
#   getCat(): uses the first paragraph of a wikipedia article to determine if the input ingredient
#             is a meat, vegetable, fruit, dairy, starch, spice, bean, sauce, or fish
#             by counting the occurrances
#
###################################################################################### 

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

###########################################################################################################
#
#   transformVeg(): made use of the preparation words preceding meats to determine which 
#                   vegetarian ingredients to which a meat could be transformed
#
###########################################################################################################

def transformVeg(data):
    transformedIngreds=[]
    returnData = copy.deepcopy(data)
    for i in range(len(data['ingredients'])):
        ingredTuple=[]
        name = (data['ingredients'][i]['name'][0])
        print("."),
        prepList = data['ingredients'][i]['preparation']
        if (getCat(name) == 'Meat'):
            if ('ground' in prepList or 'ground' in name):
                ingredTuple.append(name)
                ingredTuple.append('tofu')
                transformedIngreds.append(ingredTuple)
                returnData['ingredients'][i]['name'] = ['tofu']
                if ('ground' in prepList):
                    returnData['ingredients'][i]['preparation'][prepList.index('ground')] = ['crumbled']
                else:
                    prepList.append('crumbled')
            elif ('sliced' in prepList):
                ingredTuple.append(name)
                ingredTuple.append('tofurkey')
                transformedIngreds.append(ingredTuple)
                returnData['ingredients'][i]['name'] = ['tofurkey']
            elif ('chopped' in prepList or 'shredded' in prepList or 'cubed' in prepList or 'cube' in prepList):
                ingredTuple.append(name)
                ingredTuple.append('tofu')
                transformedIngreds.append(ingredTuple)
                returnData['ingredients'][i]['name'] = ['tofu']
            else:
                ingredTuple.append(name)
                ingredTuple.append('veggie burger')
                transformedIngreds.append(ingredTuple)
                returnData['ingredients'][i]['name'] = ['veggie burger']
        elif (getCat(name) == 'Fish'):
                ingredTuple.append(name)
                ingredTuple.append('veggie burger')
                transformedIngreds.append(ingredTuple)
                returnData['ingredients'][i]['name'] = ['veggie burger']


    return(transformDirections(returnData,transformedIngreds,0))



###########################################################################################################
#
#   transformFromVeg(): logical reversed function of tranformVeg
#
###########################################################################################################

def transformFromVeg(data):
    returnData = copy.deepcopy(data)
    transformedIngreds=[]
    for i in range(len(data['ingredients'])):
        ingredTuple=[]
        name = (data['ingredients'][i]['name'][0])
        print("."),
        prepList = data['ingredients'][i]['preparation']
        if ('tofu' in name and 'crumbled' in prepList):
                ingredTuple.append(name)
                ingredTuple.append('chicken')
                transformedIngreds.append(ingredTuple)
                returnData['ingredients'][i]['name'] = 'chicken'
                returnData['ingredients'][i]['preparation'][prepList.index('crumbled')] = ['ground']
        elif ('chopped' in prepList or 'shredded' in prepList or 'cubed' in prepList or 'cube' in prepList and 'tofu' in name):
                ingredTuple.append(name)
                ingredTuple.append('pork')
                transformedIngreds.append(ingredTuple)
                returnData['ingredients'][i]['name'] = ['pork']
        else:
            returnData['ingredients'].append({'name':['chicken'],'quantity':[8],'measurement':['ounces'],'descriptor':[],'preparation':[],'prep-description':[]})
            ingredTuple.append(name)
            ingredTuple.append('chicken')
            transformedIngreds.append(ingredTuple)

    return(transformDirections(returnData,transformedIngreds,0))


###########################################################################################################
#
#   transformDairy(): created substitution tables for ingredients containing greater than
#                     5 percent lactose
#
###########################################################################################################

def transformDairy(data):
    returnData = copy.deepcopy(data)
    transformedIngreds=[]
    # learned that hard cheeses are effectively lactose free
    cheeses = ['Asiago', 'Carmody', 'Cheddar', 'Colby', 'Cotija', 'Edam', 'Enchilado', 'Fontina', 'Gouda', 'Havarti', 'Longhorn', 'Port Salut' , 'St. George', 'Syrian']
    for i in range(len(data['ingredients'])):
        ingredTuple=[]
        name = (data['ingredients'][i]['name'][0])
        print("."),
        prepList = data['ingredients'][i]['preparation']
        if (getCat(name) == 'Dairy'):
            if ('cheese' in name):
                ingredTuple.append(name)
                ingredTuple.append(cheeses[randint(0,len(cheeses)-1)])
                transformedIngreds.append(ingredTuple)
                returnData['ingredients'][i]['name'] = [cheeses[randint(0,len(cheeses)-1)]]
            if ('milk' in name):
                ingredTuple.append(name)
                ingredTuple.append('soy milk')
                transformedIngreds.append(ingredTuple)
                returnData['ingredients'][i]['name'] = ['soy milk']
            if ('cream' in name):
                ingredTuple.append(name)
                ingredTuple.append('soy cream')
                transformedIngreds.append(ingredTuple)
                returnData['ingredients'][i]['name'] = ['soy cream']
            if ('half' in name):
                ingredTuple.append(name)
                ingredTuple.append('soy cream')
                transformedIngreds.append(ingredTuple)
                returnData['ingredients'][i]['name'] = ['soy cream']
            if ('yogurt' in name):
                ingredTuple.append(name)
                ingredTuple.append('greek yogurt')
                transformedIngreds.append(ingredTuple)
                #greek yogurt effectively lactose-free
                returnData['ingredients'][i]['name'] = ['greek yogurt']
            if ('butter' in name):
                ingredTuple.append(name)
                ingredTuple.append('margarine')
                transformedIngreds.append(ingredTuple)
                returnData['ingredients'][i]['name'] = ['margarine']
            if ('ice cream' in name):
                ingredTuple.append(name)
                ingredTuple.append('soy ice cream')
                transformedIngreds.append(ingredTuple)
                returnData['ingredients'][i]['name'] = ['soy ice cream']
                
    return(transformDirections(returnData,transformedIngreds,0))


###########################################################################################################
#
#   transformFromDairy(): logical reversed function of transformDairy
#
###########################################################################################################

def tranformFromDairy(data):
    returnData = copy.deepcopy(data)
    transformedIngreds=[]
    cheeses = ['Asiago', 'Carmody', 'Cheddar', 'Colby', 'Cotija', 'Edam', 'Enchilado', 'Fontina', 'Gouda', 'Havarti', 'Longhorn', 'Port Salut' , 'St. George', 'Syrian']
    for i in range(len(data['ingredients'])):
        ingredTuple=[]
        name = (data['ingredients'][i]['name'][0])
        print("."),
        prepList = data['ingredients'][i]['preparation']
        if (getCat(name) == 'Dairy'):
            if ('soy milk' in name):
                ingredTuple.append(name)
                ingredTuple.append('milk')
                transformedIngreds.append(ingredTuple)
                returnData['ingredients'][i]['name'] = ['milk']
            if ('soy cream' in name):
                ingredTuple.append(name)
                ingredTuple.append('cream')
                transformedIngreds.append(ingredTuple)
                returnData['ingredients'][i]['name'] = ['cream']
            if ('greek yogurt' in name):
                ingredTuple.append(name)
                ingredTuple.append('yogurt')
                transformedIngreds.append(ingredTuple)
                returnData['ingredients'][i]['name'] = ['yogurt']
            if ('margarine' in name):
                ingredTuple.append(name)
                ingredTuple.append('butter')
                transformedIngreds.append(ingredTuple)
                returnData['ingredients'][i]['name'] = ['butter']
            if ('soy ice cream' in name):
                ingredTuple.append(name)
                ingredTuple.append('ice cream')
                transformedIngreds.append(ingredTuple)
                returnData['ingredients'][i]['name'] = ['ice cream']
                
    return(transformDirections(returnData,transformedIngreds,0))

###########################################################################################################
#
#   transformKid(): using a list of accpeted kid-friendly vegetables, meats, and spices, 
#                   returns a kid-friendly recipe
#
###########################################################################################################

def transformKid(data):
    returnData = copy.deepcopy(data)
    transformedIngreds=[]
    vegList = ['tomatoes', 'onion', 'carrots', 'peas', 'corn', 'lettuce']
    for i in range(len(data['ingredients'])):
        ingredTuple=[]
        name = (data['ingredients'][i]['name'][0])
        print("."),
        prepList = data['ingredients'][i]['preparation']
        if (getCat(name) == 'Spice' and 'salt' not in name and 'black pepper' not in name):
            del returnData['ingredients'][i]
        if (getCat(name) == 'Vegetable' and name not in vegList):
            del returnData['ingredients'][i]
        if (getCat(name) == 'Fish'):
            returnData['ingredients'][i]['name'] = ['chicken breast']
            returnData['ingredients'][i]['preparation'] = []
    t = transformDirections(returnData,transformedIngreds,2)
    return(t)


###########################################################################################################
#
#   transformPizza(): isolates meats, vegetables, and spices, and makes use of a typical
#                     pizza recipe to transform any recipe into a pizza
#
###########################################################################################################

def transformPizza(data):
    returnData = copy.deepcopy(data)
    transformedIngreds=[]

    deleteIndices = []
    for i in range(len(data['ingredients'])):
        print("."),
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


    return(transformDirections(returnData,transformedIngreds,1))

###########################################################################################################
#
#   transformLowFat(): used knowledge of ingredient fat ratio to decrease the amount of an ingredient with high fat ratio
#
###################################################################################### 

def transformLowFat(data):
    returnData = copy.deepcopy(data)
    transformedIngreds=[]
    ratioList = {}
    for i in range(len(data['ingredients'])):
        print("."),
        if (getFatRatio(data['ingredients'][i]['name'][0]) > .06):
            quantity = data['ingredients'][i]['quantity'][0]
            quantity = float(quantity) / 2            
            returnData['ingredients'][i]['quantity'] = [str(quantity)]
         
    return(transformDirections(returnData,transformedIngreds,2))



###########################################################################################################
#
#   transformLowSalt(): used knowledge of ingredient sodium ratio to decrease the amount of an ingredient with high sodium ratio
#
###########################################################################################################

def transformLowSalt(data):
    returnData = copy.deepcopy(data)
    transformedIngreds=[]
    ratioList = {}
    for i in range(len(data['ingredients'])):
        print("."),
        if (getSodiumRatio(data['ingredients'][i]['name'][0]) > 3.5):
            quantity = data['ingredients'][i]['quantity'][0]
            quantity = str(float(quantity) / 2)
            returnData['ingredients'][i]['quantity'] = [str(quantity)]

    return(transformDirections(returnData,transformedIngreds,2))

###########################################################################################################
#
#   transformDirections(): used tuples of original ingredients and their respective transformed
#                       ingredients to replace the occurrances of an original ingredient.
#                       Special case: pizza.
#
###########################################################################################################

def transformDirections(data, transformedIngreds, special):
    returnData = copy.deepcopy(data)        
    directions = returnData['directions']
    originalIngredients = []
    transformedIngredients = []
    tupleList = transformedIngreds
    for ing in returnData['ingredients']:
        originalIngredients.append(ing['name'][0])
        
    for ing in returnData['ingredients']:
        transformedIngredients.append(ing['name'][0])
        
    if (special == 1):
        returnDirections = []
        for sentence in directions:
            hasPizzaIngredient = False
            for ing in transformedIngredients:
                if ing in transformedIngredients:
                    hasPizzaIngredient = True
            if (hasPizzaIngredient == True):
                returnDirections.append(sentence)
        returnDirections.append('Combine the bread flour, sugar, yeast and kosher salt in the bowl of a stand mixer and combine.' +
                                'While the mixer is running, add the water and 2 tablespoons of the oil and beat until the dough forms into a ball.'+
                                'If the dough is sticky, add additional flour, 1 tablespoon at a time, until the dough comes together in a solid ball.'+
                                'If the dough is too dry, add additional water, 1 tablespoon at a time. Scrape the dough onto a lightly floured surface and gently knead into a smooth,'+
                                'firm ball.Grease a large bowl with the remaining 2 teaspoons olive oil, add the dough, cover the bowl with plastic wrap and put it in a warm area to let'+
                                'it double in size, about 1 hour. Turn the dough out onto a lightly floured surface and divide it into 2 equal pieces. Cover each with a clean kitchen towel'+
                                'or plastic wrap and let them rest for 10 minutes. In a small bowl, combine tomato paste, water, Parmesan cheese, garlic, honey, anchovy paste, onion powder,'+
                                'oregano, marjoram, basil, ground black pepper, cayenne pepper, red pepper flakes and salt; mix together, breaking up any clumps of cheese. Top with Mozzarella cheese and all other ingredients. Bake for 14 minutes.')

        returnData['directions'] = returnDirections
    elif (special == 2):
        returnData['directions'] = directions
    else:
        returnDirections = []
        for sentence in directions:
            for tup in tupleList:
                for word in tup[0].split():
                    if word in sentence:
                        returnDirections.append(sentence.replace(word,tup[1]))


        returnData['directions'] = returnDirections

    return returnData


###########################################################################################################
#
#   Quantity Parse Functions:  converts all measures and units to conforming metrics
#
#   listQuantityParse(): iterates over a list of amounts and units and produces standardized output
#   stringQuantityParse(): breaks the amount-units string into two standardized quantities
#   fractionStringToFloat(): converts and fraction strings to decimal values
#   mixedFractionToFloat(): convert a mixed whole number and fraction string to decimal
#   numberCheck(): checks a string for numbers
#   measurementParse(): converts any unit abbreviations to a standard unit
#
###########################################################################################################

def listQuantityParse(inputList):
    
    length = len(inputList)
    outputList = inputList

    for i in range(0, length):
        outputList[i] = stringQuantityParse(inputList[i])

    return outputList

# helper functions

# takes a string - ex: "3 lbs chicken"
# returns a list of length 2: [quantity, measurement] ex: [3, "pounds"]
def stringQuantityParse(inputString):

    inputString = inputString.lower()
    splitInputString = inputString.split()

    # first word is either number or n/a
    if splitInputString[0] == "n/a":
        return [0,' ']
    else:
        splitInputString[0] = fractionStringToFloat(splitInputString[0])
    
    # check if second word is fraction (second part of mixed number)
    if len(splitInputString) == 1:
        return str(splitInputString[0]) + ' count'
    elif numberCheck(splitInputString[1]):
        number = splitInputString[0]
        fraction = splitInputString[1]
        quantity = number + fractionStringToFloat(fraction)
        unit = splitInputString[2]
    else:
        quantity = splitInputString[0]
        unit = splitInputString[1]

    [outQuantity, outUnit] = measurementParse(quantity, unit)

    # converts non-decimal numbers back to int, just to look nice
    # 3.0 -> 3
    if outQuantity == int(outQuantity):
        outQuantity = int(outQuantity)

    return [outQuantity, outUnit]


# takes a tuple of strings representing a mixed fraction
# ex., ["1", "1/2"]
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
    outputUnit = 'unit'
    #outputQuantity = inputQuantity

    # volume - to cubic cm
    if re.match('tablespoon[s]?|tbsp' , inputUnit) != None:
        outputUnit = 'tablespoon'
        #outputQuantity = inputQuantity * 14.7867648
        
    if re.match('teaspoon[s]?|tsp' , inputUnit) != None:
        outputUnit = 'teaspoon'
        #outputQuantity = inputQuantity * 4.92892159
        
    if re.match('cup[s]?' , inputUnit) != None:
        outputUnit = 'cup'
        #outputQuantity = inputQuantity * 236.588236

    if re.match('mL[s]?|ml[s]?|milliliter[s]?' , inputUnit) != None:    
        outputUnit = 'milliliter'
        #outputQuantity = inputQuantity

    if re.match('l[s]?|L[s]?|liter[s]?' , inputUnit) != None:    
        outputUnit = 'liter'
        #outputQuantity = inputQuantity * 1000
        

    # mass/weight - to grams
    if re.match('pound[s]?|lb[s]?' , inputUnit) != None:
        outputUnit = 'pound'
        #outputQuantity = inputQuantity * 453.592

    if re.match('ounce[s]?|oz[s]?' , inputUnit) != None:
        outputUnit = 'ounce'
        #outputQuantity = inputQuantity * 28.3495
        
    if re.match('kilogram[s]?|kg[s]?' , inputUnit) != None:
        outputUnit = 'kilogram'
        #outputQuantity = inputQuantity * 1000

    if re.match('gram[s]?|g[s]?' , inputUnit) != None:
        outputUnit = 'gram'
        #outputQuantity = inputQuantity

    if inputUnit == 1:
        outputUnit += "s"
          
    return [inputQuantity, outputUnit]

###########################################################################################################
#
#   LoadKnowledge(): reads specified knowledge text file into the specified list
#
###########################################################################################################

def LoadKnowledge(filename,lst):
    with open(filename) as f:
        line = f.readlines()
    for lin in line:
        lin = lin.rstrip('\r\n')
        lst.append(lin)

###########################################################################################################
#
#   stripPunctuation(): used to strip punctuation from ingredient and direction strings
#
###########################################################################################################

def stripPunctuation(inText):
  outText = inText
  for c in string.punctuation:
      outText = outText.replace(c,"")
  return outText

###########################################################################################################
#
#   validMatch(): used to determine if a prospective word match is within a longer match previously made
#
###########################################################################################################

def validMatch(phrase,s):
    bOn = False
    for i in range(0,s.start(0)):
        if phrase[i] == '[':
            bOn = True
        if phrase[i] == ']':
            bOn = False
    return not bOn

###########################################################################################################
#
#   wrapRemaining(): places brackets [around] any unwrapped word.  this aids in identifying multi-word
#                    tokens contained int he knowledgebase
#
###########################################################################################################

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

###########################################################################################################
#
#   parseIngredients(): parses an ingredient phrase and returns a separate list for all food, description
#                       preparation and preparations descriptions found in phrase.  function reads tokens
#                       from appropriate knowledge bases and store in lists specified.  all tokens are
#                       aggregated into a single big list and sorted in descending order of length.  this
#                       faciliates the match of longer tokens before shorted tokens (note: prospective
#                       matches inside a longer token are rejected -- see above).  once all tokens in a phrase
#                       are wrapped with brackets, these are compared to individual kb lists to determine
#                       how to clossify them, if at all.
#
###########################################################################################################

def parseIngredients(phrase):
    listFood = list()
    listDesc = list()
    listPrep = list()
    listPrepDesc = list()
    listIgnore = list()

    LoadKnowledge('foods.txt',listFood)
    LoadKnowledge('desc.txt',listDesc)
    LoadKnowledge('preps.txt',listPrep)
    LoadKnowledge('prepdesc.txt',listPrepDesc)
    LoadKnowledge('ignores.txt',listIgnore)

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
        bFound = False
        if len(t) > 1:
            s = t.replace(" [","")
            s = s.replace("[","")
            if s in set(listFood):
                bFound = True
                food.append(s)
            if s in set(listDesc):
                bFound = True
                desc.append(s)
            if s in set(listPrep):
                bFound = True
                prep.append(s)
            if s in set(listPrepDesc):
                bFound = True
                pdsc.append(s)
            if not bFound:
                matchObj = re.match(r'(.*)ly',t,re.I)
                if matchObj:
                    bFound = True
                    pdsc.append(s)
            if not bFound:
                matchObj = re.match(r'(.*)ed',t,re.I)
                if matchObj:
                    bFound = True
                    prep.append(s)
                
    return [food,desc,prep,pdsc]

###########################################################################################################
#
#   parseDirections(): peforms same function as parseIngredients() but on direction phrases using idententical
#                      logic -- see above.
#
###########################################################################################################

def parseDirections(direction):
    listTools = list()
    listMethods = list()

    LoadKnowledge('tools.txt',listTools)
    LoadKnowledge('methods.txt',listMethods)

    listTools.sort(lambda x,y: cmp(len(y), len(x)))
    listMethods.sort(lambda x,y: cmp(len(y), len(x)))

    listBig = list()
    for elem in listTools:
        listBig.append(elem)
    for elem in listMethods:
        listBig.append(elem)
    listBig.sort(lambda x,y: cmp(len(y), len(x)))

    direction = stripPunctuation(direction)
    direction = direction.lower()
    direction = direction + "  "

    for elem in listBig:
        elem1 = elem + ' '
        s = re.search(elem1,direction)
        if s:
            if validMatch(direction,s):
                old = elem
                new = '[' + elem + ']'
                direction = direction.replace(old,new)
    direction = wrapRemaining(direction)

    tools = list()
    methods = list()
    
    tokens = direction.split("]")
    for t in tokens:
        if len(t) > 1:
            s = t.replace(" [","")
            s = s.replace("[","")
            if s in set(listTools):
                tools.append(s)
            if s in set(listMethods):
                methods.append(s)
    if re.search('[stir]',direction):
        tools.append('spoon')
        tools.append('bowl')
    if re.search('[mix]',direction):
        tools.append('spoon')
        tools.append('bowl')
    if re.search('[cut]',direction):
        tools.append('knife')

    return [tools, methods]

###########################################################################################################
#
#   main(): accepts a url as input along with the filename for the json file containing the parsed, but
#           untransformed recipe.  The code does the following:
#               1.  Validates the number of command line parameters
#               2.  Gets the indredient (including quantity) and direction lists for the URL
#               3.  Constructs an empty JSON object to store the parsed original recipe
#               4.  Parses the measurements into a standardized format
#               5.  Parses the ingredient list using the knowledge bases
#               6.  Parses the directions for tools and cooking methods
#               7.  Of the cooking methods identifies, selectd the primary cooking method by
#                   walking a manually priorotized list to find the "primary" and the medthods identified
#               8.  Enters the User Interface loop which propmts the user to select a transformation
#                   until "exit" is selected.  Selected transformation are made using the modules
#                   above and displayed in Engligh to the User Interface.
#
###########################################################################################################

def main(args):

    outFileName = 'c:\\dwd\\recipes\\recipe.json'
    url = 'http://allrecipes.com/Recipe/Easy-Garlic-Broiled-Chicken/'
    
##    if len(args) != 3:
##        print " "
##        print "Error:  You need to specifiy 2 command line parameters."
##        print "  usage: <recipe url> <output JSON file name>"
##        debugPrompt()
##        return
##
##    url = args[1]
##    outFileName = args[2]

##    lines = [line.strip() for line in open('c:\\python27\\recipe\\urls.txt')]
##    for i in range(10,100):
##        url = lines[i]

    print " "
    print "Retreiving recipe for specified URL..."
    print " "
    
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
        meas = stringQuantityParse(qty)
        amt = [meas[0]]
        units = [meas[1]]
        [food,desc,prep,pdsc] = parseIngredients(phrase)
        jsonObj["ingredients"].append({"name":food, "quantity":amt, "measurement":units, "descriptor":desc, "preparation":prep, "prep-description":pdsc})

    tools1 = list()
    methods1 = list()
    directions1 = list()
    for i in range(0,len(listD)):
        step = listD[i]
        for j in range(0,len(step)):
            direction = step[j]
            [tools, methods] = parseDirections(direction)
            for t in tools:
                if not (t in tools1):
                    tools1.append(t)
            for m in methods:
                if not (m in methods1):
                    methods1.append(m)
            directions1.append(direction)

    listPrimary = list()
    LoadKnowledge('primary.txt',listPrimary)
    primary = 'prepare'
    for p in listPrimary:
        if p in methods1:
            primary = p
            break
        
    jsonObj["primary cooking method"] = primary
    for m in methods1:
        jsonObj["cooking methods"].append(m)
    for t in tools1:
        jsonObj["cooking tools"].append(t)
    for d in directions1:
        jsonObj["directions"].append(d)

    jsonRecipePrint(jsonObj)

    with open(outFileName, 'w') as outfile:
        json.dump(jsonObj, outfile)
    outfile.close()

    bContinue = True
    while bContinue:

        print(" ")
        print("Please select a transformation option:")
        print(" ")
        print("  1 = To Vegetarian")
        print("  2 = From Vegetarian")
        print("  3 = To Lactose-free")
        print("  4 = From Lactose-free")
        print("  5 = To Kid's Meal")
        print("  6 = To a Pizza")
        print("  7 = To Low Fat")
        print("  8 = TO Low Sodium")
        print("  Anything else = exit")
        print(" ")
        
        option = input("Enter your choice: ")
        print(" ")
        if option == 1:
            print("Transforming recipe ."),
            jsonTrans = transformVeg(jsonObj)
            jsonRecipePrint(jsonTrans)
        elif option == 2:
            print("Transforming recipe ."),
            jsonTrans = transformFromVeg(jsonObj)
            jsonRecipePrint(jsonTrans)
        elif option == 3:
            print("Transforming recipe ."),
            jsonTrans = transformDairy(jsonObj)
            jsonRecipePrint(jsonTrans)
        elif option == 4:
            print("Transforming recipe ."),
            jsonTrans = tranformFromDairy(jsonObj)
            jsonRecipePrint(jsonTrans)
        elif option == 5:
            print("Transforming recipe ."),
            jsonTrans = transformKid(jsonObj)
            jsonRecipePrint(jsonTrans)
        elif option == 6:
            print("Transforming recipe ."),
            jsonTrans = transformPizza(jsonObj)
            jsonRecipePrint(jsonTrans)
        elif option == 7:
            print("Transforming recipe ."),
            jsonTrans = transformLowFat(jsonObj)
            jsonRecipePrint(jsonTrans)
        elif option == 8:
            print("Transforming recipe ."),
            jsonTrans = transformLowSalt(jsonObj)
            jsonRecipePrint(jsonTrans)
        else:
            bContinue = False

    print(" ")
    print(" * * * * * * * T H A N K   Y O U * * * * * * *")

if __name__ == "__main__":
    main(sys.argv)
