#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import math
from gurobipy import *
from bokeh.plotting import figure, show, output_server



Point = namedtuple("Point", ['x', 'y'])
Facility = namedtuple("Facility", ['index', 'setup_cost', 'capacity', 'location'])
Customer = namedtuple("Customer", ['index', 'demand', 'location'])

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def solve_it(input_data):
    # # Modify this code to run your optimization algorithm
    #
    # # parse the input
    # lines = input_data.split('\n')
    #
    # parts = lines[0].split()
    # facility_count = int(parts[0])
    # customer_count = int(parts[1])
    #
    # facilities = []
    # for i in range(1, facility_count+1):
    #     parts = lines[i].split()
    #     facilities.append(Facility(i-1, float(parts[0]), int(parts[1]), Point(float(parts[2]), float(parts[3])) ))
    #
    # customers = []
    # for i in range(facility_count+1, facility_count+1+customer_count):
    #     parts = lines[i].split()
    #     customers.append(Customer(i-1-facility_count, int(parts[0]), Point(float(parts[1]), float(parts[2]))))
    #
    # # build a trivial solution
    # # pack the facilities one by one until all the customers are served
    # solution = [-1]*len(customers)
    # capacity_remaining = [f.capacity for f in facilities]
    #
    # facility_index = 0
    # for customer in customers:
    #     if capacity_remaining[facility_index] >= customer.demand:
    #         solution[customer.index] = facility_index
    #         capacity_remaining[facility_index] -= customer.demand
    #     else:
    #         facility_index += 1
    #         assert capacity_remaining[facility_index] >= customer.demand
    #         solution[customer.index] = facility_index
    #         capacity_remaining[facility_index] -= customer.demand
    #
    # used = [0]*len(facilities)
    # for facility_index in solution:
    #     used[facility_index] = 1
    #
    # # calculate the cost of the solution
    # obj = sum([f.setup_cost*used[f.index] for f in facilities])
    # for customer in customers:
    #     obj += length(customer.location, facilities[solution[customer.index]].location)

    # prepare the solution in the specified output format

    lines = input_data.split('\n')
    parts = lines[0].split()
    facility_count = int(parts[0])
    customer_count = int(parts[1])

    # Facilities = {}
    # Customers = {}
    # for i in range(1, facility_count+1):
    #     parts = lines[i].split()
    #     Facilities['Facility'+str(i)] = {'setup':int(parts[0]), 'capacity':int(parts[1]),\
    #                 'x-cor':float(parts[2]),'y-cor':float(parts[3])}
    #
    # for j in range(facility_count+1, facility_count+customer_count+1):
    #     parts = lines[j].split()
    #     Customers['Customer'+str(j-(facility_count))] = {'demand': int(parts[0]), \
    #                 'x-cor': float(parts[1]), 'y-cor': float(parts[2])}

    facilities = []
    for i in range(1, facility_count + 1):
        parts = lines[i].split()
        facilities.append(Facility(i , float(parts[0]), int(parts[1]), Point(float(parts[2]), float(parts[3]))))

    customers = []
    for i in range(facility_count + 1, facility_count + 1 + customer_count):
        parts = lines[i].split()
        customers.append(Customer(i - facility_count, int(parts[0]), Point(float(parts[1]), float(parts[2]))))

    model = Model('Facility Planning')
    f = {}
    setup = {}
    capacity = {}
    for i in facilities:
        f[i.index] = model.addVar(vtype=GRB.BINARY, name='Facitily %d' %i.index)
        setup[i.index] = i.setup_cost
        capacity[i.index] = i.capacity

    # for k1, v1 in setup.items():
    #     print("setup_cost" + str(k1) + ": " + str(v1))

    demand = {}
    for j in customers:
        demand[j.index] = j.demand

    # for k2, v2 in demand.items():
    #     print("demand" + str(k2) + ": " + str(v2))

    cost = {}
    combo = {}
    for i in customers:
        for j in facilities:
            combo[(i.index, j.index)] = model.addVar(lb=0, vtype=GRB.BINARY, name="Customer, Facility: %g,%g" %(i.index,j.index))
            cost[(i.index, j.index)] = round(length(i.location, j.location), 3)

    model.update()

    # for key,value in cost.items():
    #     print(key,value)

    # Adding Constraints

    for i in customers:
        for j in facilities:
            model.addConstr(combo[(i.index, j.index)] <= f[j.index])

    for i in customers:
        model.addConstr(quicksum(combo[(i.index,j.index)] for j in facilities) == 1)

    for j in facilities:
        model.addConstr(quicksum(demand[i.index]*combo[(i.index, j.index)] for i in customers)<= capacity[j.index] )

    model.setObjective(quicksum(setup[j.index] * f[j.index] +\
                                quicksum(cost[(i.index, j.index)] *combo[(i.index, j.index)] for i in customers) for j in facilities))

    model.optimize()

    if model.status == GRB.Status.INF_OR_UNBD:
        # Turn presolve off to determine whether model is infeasible
        # or unbounded
        model.setParam(GRB.Param.Presolve, 0)
        model.optimize()

    if model.status == GRB.Status.OPTIMAL:
        print('Optimal objective: %g' %model.objVal)
        model.printAttr('x')
        # for v in model.getVars():
        #     if v.x != 0:
        #         print('Customer, Facility: %s' % (v.varName))
        #         #print(v.varName + ": " + float(v.x))

        exit(0)
    elif model.status != GRB.Status.INFEASIBLE:
        print('Optimization was stopped with status %d' % model.status)
        exit(0)

    print('')
    print('Model is infeasible')
    model.computeIIS()
    model.write("./log/model.ilp")
    print("IIS written to file 'model.ilp'")


    # output_data = '%.2f' % obj + ' ' + str(0) + '\n'
    # output_data += ' '.join(map(str, solution))

    #return output_data


import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/fl_16_2)')

