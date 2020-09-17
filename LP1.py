from gurobipy import *
from collections import OrderedDict
from itertools import *


class Data:
    def __init__(self):
        self.products = [1, 2, 3, 4, 5, 6, 7];
        self.machines = ["grinder","vdrill","hdrill","borer","planer"]
        self.months = ["january","february","march","april","may","june"]
        
        self.profits = [10, 6, 8, 4, 11, 9, 3]
        
        tmp = {
        'grinder'     :[0.5,    0.7,    0,      0,      0.3,    0.2,   0.5],  
        'vdrill'      :[0.1 ,   0.2 ,   0   ,   0.3 ,   0   ,   0.6,   0],    
        'hdrill'      :[0.2 ,   0   ,   0.8 ,   0   ,   0   ,   0  ,   0.6],  
        'borer'      :[0.05,   0.03,   0   ,   0.07,   0.1 ,   0  ,   0.08],
        'planer'    :[0   ,   0   ,   0.01,   0   ,   0.05,   0  ,   0.05]
        }
        self.coeff=OrderedDict()
        for m in self.machines:
            for (j,p) in enumerate(self.products):
                self.coeff[m,p] = tmp[m][j] 
        

        capacity = {"grinder": 4,"vdrill": 2,"hdrill": 3, "boring": 1, "planning": 1}#wrong names, uses my own modified.
        
        tmp = {
        "grinder": [("january", 2), ("february", 1), ("march", 1), ("april", 1), ("may", 2), ("june", 1)],
        "hdrill": [("january", 1), ("february", 3), ("march", 1), ("april", 1), ("may", 1), ("june", 2)], 
        "borer":  [("january", 1), ("february", 1), ("march", 2), ("april", 1), ("may", 1), ("june", 1)],
        "vdrill": [("january", 1), ("february", 1), ("march", 1), ("april", 2), ("may", 2), ("june", 1)],
        "planer": [("january", 1), ("february", 1), ("march", 1), ("april", 1), ("may", 1), ("june", 2)] 
        }

        
        self.maintainance = OrderedDict()
        for m in self.machines:
            for t in self.months:
                self.maintainance[m,t] = 0
            if m in tmp:
                for s in tmp[m]:
                    self.maintainance[m,s[0]]=s[1]
        
        tmp = {
        "january":    [500   ,1000   ,300   ,300   ,800    ,200   ,100],
        "february":   [600   ,500    ,200   ,0     ,400    ,300   ,150],
        "march":      [300   ,600    ,0     ,0     ,500    ,400   ,100],
        "april":      [200   ,300    ,400   ,500   ,200    ,0     ,100],   
        "may":        [0     ,100    ,500   ,100   ,1000   ,300   ,0  ],
        "june":       [500   ,500    ,100   ,300   ,1100   ,500   ,60 ]
        }
        
        self.market_limits = OrderedDict()
        for m in self.months:
            for (j,p) in enumerate(self.products):
                self.market_limits[m,p] = tmp[m][j] 
    
    def printData(self):
        print "Months:", self.months
        print "Products:", self.products
        print "Machines:", self.machines
        print "Coefficients: ",self.coeff
        print "Market_limits:", self.market_limits
        print "Maitainance:", self.maintainance

def solve(data):
    m = Model("fpmm")
    m.setParam(GRB.param.Method, 0)
    
    ######### BEGIN: Write here your models
    
#variables:
    # capacity dictonary lookups renamed to match data.machines
    capacity = {"grinder": 5,"vdrill": 3,"hdrill": 4, "borer": 2, "planer": 2}
    Wmonths = ["december","january","february","march","april","may","june"] #december for the warehouse
    monthsdict = {"december": 0,"january": 1,"february": 2,"march": 3,"april": 4,"may": 5,"june": 6}

    #selling, whats in the warehouse and production as variable, upper bound just in case.
    production = m.addVars(data.products, data.months, ub=10000, vtype=GRB.INTEGER, name="production")
    sold = m.addVars(data.products, data.months, ub=10000, vtype=GRB.INTEGER, name="sold")
    warehouse = m.addVars(data.products, Wmonths, lb=0, ub=100, vtype=GRB.INTEGER, name="warehouse")

    #objective is selling of products times profits associated with said product.
    m.setObjective(quicksum(sold[i] * data.profits[i[0]-1] - warehouse[i] * 0.5 for i in product(data.products,data.months)), GRB.MAXIMIZE)
    
#constraints:
    #warehouse constants, december = 0 and june = 50
    for i in data.products:
        m.addConstr( (warehouse[i,"december"] == 0))

    for i in data.products:
        m.addConstr( (warehouse[i,"june"] == 50))

    #market limits on selling
    for i in product(data.products,data.months):
        m.addConstr( (sold[i] <= data.market_limits[i[1],i[0]]))

    #limits on production hours
    for n in product(data.machines,data.months):
        m.addConstr( 
              quicksum( production[i,n[1]] * data.coeff[n[0],i] for i in data.products) 
              <= 16 * 24 * ( capacity[n[0]] - data.maintainance[n] )    
        )

    #max selling is production this month + warehouse from last month - warehouse this month
    for i in product(data.products,data.months):
        m.addConstr( (sold[i] == production[i] + warehouse[i[0],Wmonths[monthsdict[i[1]]-1]] - warehouse[i]))


    ######### END
     
    # check the model
    m.write("model.lp")
    def printSolution():
         ## implement this function
         for v in m.getVars():
             print(v.varName, v.x)
         print('Profit:', m.objVal)
         pass
    m.optimize()
    printSolution()
    return m.objVal

instance = Data()
    instance.printData()
    solve(instance)
