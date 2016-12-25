#PRBS polynomial logic node

#this module contains helper functions that help generate a PRBS sequence according to polynomial logic 

# stage 1 polyParser
# stage 2 polyTreater
# stage 3 divider 
# stage 4 multiplier
# stage 5 lBitWala
# stage 6 prbsGetter



import re

#stage 1 polyParser
#takes a polynomial expression where the degree of a term is
#denoted by writing it after x. Eg: 3x2 is a second degree term
#returns a list containing individual opearators and operands of the expression
def polyParser(expression):
    container = []
    OPERATORS = {'+', '-', '*', '/'}
    operators = re.escape(''.join(OPERATORS))
    pattern = r"\w+|[{}]".format(operators)
    for match in re.finditer(pattern, expression):
        element = match.group(0)
        container.append(element)
    return (container)
#end of polyParser
    
#stage 2 polyTreater
#assuming degree and coefficients are in single digits
#takes a list containing individual opearators and operands of an expression
#returns a dictionary that represents a polynomial; keys represent degree and values represent coefficients
def polyTreater(listOld):
    lenlistOld = len (listOld)
    #print (lenlistOld)
    dictNew = {}
    #print (len (dictNew))

#dict keys store degree values   
    for i in listOld:
        if i == '+' or i == '-':
            pass
        else:
            #if the term has x
            if 'x' in i:
                k = i.find('x')            
                #setting degree:
                #if no degree specified
                if len (i) == k+1:
                    deg = 1
                #if degree specified
                else:
                    deg = i [k+1]  
                #setting coeff:
                #if no coeff specified
                if k == 0:
                    coeff = 1
                #if coeff specified
                else:
                    coeff = i[0]
                    
            #if the term has no x    
            else:
                deg = 0
                coeff = i

        dictNew[int(deg)] = int(coeff)
        
    #this part fills in zero coefficients for the degree terms that are not present
    z = max(dictNew.keys())
    for i in range (1,z):
        if i in dictNew.keys():
            pass
        else:  
            dictNew [i] = 0

    return (dictNew)
#end of polyTreater              


#stage 3 divider
#division of numerator and denominator:
#takes 2 dictionaries (in the order dict1, dict2) which represent polynomials whose:
#degree terms are in ascending sequence
#returns a dicionary which represents a polnomial that is the remainder of dict1 by dict2
def divider (dict1, dict2):
    #if the top order of denominator is present in numerator
    remainder = {}
    flag = 0
    keys1 = dict1.keys()
    keys2 = dict2.keys()
    if max(keys1) == max(keys2):
        for key1, value1 in dict1.items():
            for key2, value2 in dict2.items():
                if key1 == key2 and value1 == value2:
                    flag = 1
                    break
            if flag == 1:
                flag = 0
                pass
            else:
                #if coefficient is zero, do not include the item pair
                if value1 == 0:
                    pass
                else:
                    remainder [key1] = value1

        #print ("remainder is", remainder) #TEST to check interim values
        for key2, value2 in dict2.items():
            for key1, value1 in dict1.items():
                if key1 == key2 and value1 == value2:
                    flag = 1
                    break
            if flag == 1:
                flag = 0
                pass
            else:
                if value2 == 0:
                    pass
                else:
                    remainder [key2] = value2

    #if top order term of numerator less than top order term of denominator
    else:
        for key1, value1 in dict1.items():
            if value1 == 0:
                pass
            else:
                remainder [key1] = value1

    return (remainder)
#end of divider 


#stage 4 multiplier
#takes a dictionary dict1 which represents a polynomials 
#returns a dicionary which represents a polnomial that is the product of dict1 by x
def multiplier (dict1):
    #this dictionary will contain the result
    product = {}
    
    for key1, value1 in dict1.items():
        if value1 == 1:
            product [key1+1] = 1
            
    return (product)
#end of multiplier 


#stage 5 lBitWala:
#takes a dictionary polyDict which represents a polynomial 
#returns an integer which is the coefficient of the zeroth degree term of poynomial polyDict
def lastBitWala(polyDict):
    minKey = min (polyDict.keys())
    if minKey == 0: #we have a zero deg term
        lBit = polyDict [minKey]
    else:
        lBit = 0
    return (lBit)
#end of lBitWala 
    

#stage 6 prbsGetter:
#take three parameters:  (i) an integer (ii) a dictionary (char polynomial) (iii) a dictionary (SeedOrRemainder)  is fed to the function
#returns one bit which is a part of the PRBS sequence
def prbsGetter(flagInt, polyDictDenom, SeedOrRemainder ):
    
    global SeedOrRemainderLocal
    if (flagInt == 0):
        SeedOrRemainderLocal = SeedOrRemainder
        output = lastBitWala(SeedOrRemainderLocal)
        return output 

    polyDictNum = multiplier(SeedOrRemainderLocal)
    #print (polyDictNum)
    SeedOrRemainderLocal = divider(polyDictNum, polyDictDenom)
    #print (SeedOrRemainderLocal)
    output = lastBitWala(SeedOrRemainderLocal)
    return output
#end of prbsGetter 




