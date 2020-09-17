from tsputil import *
from gurobipy import *
from collections import OrderedDict
from itertools import chain, combinations, product

%run tsputil.py 
%matplotlib inline

ran_points = Cities(n=20,seed=1488)
plot_situation(ran_points)

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

subtours = list(powerset(range(len(ran_points))))
# The first element of the list is the empty set and the last element is the full set, hence we remove them.
subtours = subtours[1:(len(subtours)-1)]

def solve_tsp_origional(points, subtours=[]):
    points=list(points) #list of city points (tuples)
    V = range(len(points)) #list of cities (numbered)
    E = [(i,j) for i in V for j in V if i<j]
    E = tuplelist(E) #Gurobi Tuplelist of different edges, starting from 0 going to n-1, with duplicate edges removed
    
    m = Model("TSP0")
    m.setParam(GRB.param.Presolve, 0)
    m.setParam(GRB.param.Method, 0)
    m.setParam(GRB.param.MIPGap,1e-7)
    
    ######### BEGIN: Write here your model for Task 1

    #variables:
    x = m.addVars(E, vtype=GRB.BINARY, name="x") #edge used or not

    #objective: 
    m.setObjective(quicksum(distance(points[i[0]], points[i[1]]) * x[i] for i in E), GRB.MINIMIZE)
    
    #constraints:
    
    #edge in and out of city
    for i in V:
        m.addConstr(
            quicksum( x[i] for i in E.select(i,'*')) 
            + quicksum( x[i] for i in E.select('*',i))
            == 2
        )
    
    #subset elimination
    #list(itertools.combinations(subtours[t], 2)) gets all (i,j) possible pairs from a tour
    for t in subtours:
        m.addConstr(
            quicksum( x[i] for i in itertools.combinations(t, 2)) 
            <= len(t) -1
        )
        
        
    #from task 4:
    #for i,j in E if (i != 0 and j != 0):
    #    for i in V for j in V if i<j
    #    m.addConstr(
    #        quicksum( x[i] for i in itertools.combinations(t, 2)) 
    #        <= len(t) -1
    #    )
    
    ######### END
    
    m.optimize()
    m.write("tsplp.lp")
    
    if m.status == GRB.status.OPTIMAL:
        print('The optimal objective is %g' % m.objVal)
        m.write("tsplp.sol") # write the solution    
        return {(i,j) : x[i,j].x for i,j in x}
    else:
        print "Something wrong in solve_tsplp"
        exit(0)
        
def solve_tsp(points, subtours=[]):
    points=list(points) #list of city points (tuples)
    V = range(len(points)) #list of cities (numbered)
    E = [(i,j) for i in V for j in V if i<j]
    E = tuplelist(E) #Gurobi Tuplelist of different edges, starting from 0 going to n-1, with duplicate edges removed
    
    m = Model("TSP0")
    m.setParam(GRB.param.Presolve, 0)
    m.setParam(GRB.param.Method, 0)
    m.setParam(GRB.param.MIPGap,1e-7)
    
    ######### BEGIN: Write here your model for Task 1

    #variables:
    x = m.addVars(E, vtype=GRB.CONTINUOUS, name="x")

    #objective: 
    m.setObjective(quicksum(distance(points[i[0]], points[i[1]]) * x[i] for i in E), GRB.MINIMIZE)
    
    #constraints:
    
    #edge in and out of city, note that this also means that x wont go below 0
    for i in V:
        m.addConstr(
            quicksum( x[i] for i in E.select(i,'*')) 
            + quicksum( x[i] for i in E.select('*',i))
            == 2
        )
    
    #x limit
    for i in E:
        m.addConstr(
            x[i] <= 1
        )
    
    #subtour elimination, given from input
    for t in subtours:
        m.addConstr(
            quicksum( x[i] for i in itertools.combinations(t, 2)) 
            <= len(t) -1
        )
    
    ######### END
    
    m.optimize()
    m.write("tsplp.lp")
    
    if m.status == GRB.status.OPTIMAL:
        print('The optimal objective is %g' % m.objVal)
        m.write("tsplp.sol") # write the solution    
        return {(i,j) : x[i,j].x for i,j in x}
    else:
        print "Something wrong in solve_tsplp"
        exit(0)

#task 3
tsplp1_task3 = solve_tsp(ran_points,[[2,3,4,8,9,10,12,13,14,15,16,19],[0,7,11],[1,5,6,17,18]])
#giving all: (2,3,4,8,9,10,12,13,14,15,16,19),(0,7,11),(1,5,6,17,18) gets final solution?
plot_situation(ran_points,tsplp1_task3)
