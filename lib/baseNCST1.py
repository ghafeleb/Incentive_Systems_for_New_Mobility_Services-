import numpy as np
import pandas as pd
import datetime
import os
import matplotlib.pyplot as plt
import matplotlib
import networkx as nx
import pickle
from collections import OrderedDict
import copy
from scipy.sparse import csr_matrix
from scipy import io
import seaborn as sns
import joblib
from itertools import islice


class Link:
    def __init__(self, ID, length, fft):
        self.ID = ID
        self.length = length
        self.fft = fft


class Path:
    def __init__(self):
        self.node_list = None
        self.link_list = None
        # cost and p will be assigned in get_P function
        self.cost = None
        self.p = None
        # self.length_ = None
        return

    # Construct the link_list attribute of the Path object from node_list attribute
    def node_to_list(self, G, link_dict):
        # self.length_ = list()
        if self.node_list == None:
            print "Nothing to convert"
            return
        # tmp is going to finally become link_list attribute
        tmp = list()
        # Loop in the number of links in the path (from O to D) - 1
        for i in xrange(len(self.node_list) - 1):
            try:
                # print "OK"
                # self.length_.append(G[self.node_list[i]][self.node_list[i+1]]["length"])
                # print "node_list[", i,"] and node_list[", i+1, "]:", self.node_list[i], self.node_list[i+1]
                link_ID = G[self.node_list[i]][self.node_list[i + 1]]["ID"]
                # if i==0:
                #     # if G[self.node_list[i]][self.node_list[i+1]]["length"]!=0:
                #     print "Weight of edge from O:", G[self.node_list[i]][self.node_list[i+1]]["length"]
                # elif i==len(self.node_list) - 1-1:
                #     # if G[self.node_list[i]][self.node_list[i+1]]["length"]!=0:
                #     print "Weight of edge to D:", G[self.node_list[i]][self.node_list[i + 1]]["length"],
                # If the edge is not traversed before, we add its information to link_dict
                if link_ID not in link_dict.keys():
                    # print('if1')

                    # Construct a Link object
                    # print "Node ", self.node_list[i], " to ", self.node_list[i + 1]
                    # print "Link ID: ", link_ID, ", Length: ", G[self.node_list[i]][self.node_list[i + 1]][
                    #     "length"], ", fft:", G[self.node_list[i]][self.node_list[i + 1]]["fft"]
                    tmp_link = Link(link_ID, G[self.node_list[i]][self.node_list[i + 1]]["length"],
                                    G[self.node_list[i]][self.node_list[i + 1]]["fft"])
                    # print('if2')
                    tmp.append(tmp_link)
                    # print('if3')
                    link_dict[link_ID] = tmp_link
                else:
                    # print "\nThis link has been checked before, link_ID:", link_ID
                    tmp.append(link_dict[link_ID])
                    # print('else')

            except:
                print "ERROR"
                print self.node_list[i], self.node_list[i + 1]
        self.link_list = tmp


def overlap(min1, max1, min2, max2):
    # min((cur_time_date2 - basis), (arrival_time_date2 - basis)) - max((cur_time_date - basis), (arrival_time_date - basis))
    # MIN(cur_time_date2, arrival_time_date2) - MAX(cur_time_date, arrival_time_date)
    return max(0, min(max1, max2) - max(min1, min2))


def get_finish_time(spd, length_togo, start_time, tmp_date):
    basis = datetime.datetime.combine(tmp_date, datetime.time(0, 0, 0)) # !!
    # a function with lambda is defined, then all the values in spd.index inserted in this function using map(function, values)
    # Next line changes all the speed values in data to time_seq
    # spd: The row of the speed data at a specific day at a specific sensor
    # spd.index is the list of time intervals included in the column indecies of speed data in seconds >> 5AM = 18000
    time_seq = map(lambda x: (datetime.datetime.combine(tmp_date, x) - basis).total_seconds(), spd.index)
    # Create a float array of speed data
    data = np.array(spd.tolist()).astype(np.float)
    #     print data
    #     print time_seq
    # np.interp(x_tilt, x_data, f(x_data)): finds the linear interpolation between two consecutive points of (x_data, f(x_data)) if f() is a function,
    # in other words, it wants to find the value of f(x_tilt) with interpolation based on x=x_data and y=f(x_data)
    # Dividing by 1600 to convert meter to miles (?!)
    # Multiply by 3600 to convert time to seconds (?!)
    # Therefore: (meter/hour)*(miles/1600 meter)*(hour/3600 seconds) --> (miles/seconds)
    # And: (miles/hour)*(1600 meter/1 mile)*(1 hour/3600 seconds) --> (meters/seconds)
    # cur_spd = np.interp((datetime.datetime.combine(tmp_date, start_time) - basis).total_seconds(), time_seq, data) / 1600.0 * 3600.0 # !! His code
    cur_spd = np.interp((datetime.datetime.combine(tmp_date, start_time) - basis).total_seconds(), time_seq,
                        data) * 1600.0 / 3600.0  # !! My code
    try:
        # length_togo is the length of the link <<>> link_dict[ID].length
        # Using timedelta function to manipulate the time
        # We use ".time()" to convert seconds to time format > example: (basis + datetime.timedelta(seconds = 3600)).time() --> datetime.time(1, 0)
        # start_time + time needed to reach link
        # print "current speed: ", cur_spd
        # print "length_togo: ", length_togo
        new_start_time = (datetime.datetime.combine(tmp_date, start_time) + datetime.timedelta(
            seconds=length_togo / cur_spd)).time()
    #     print "need:", length_togo/cur_spd
        # print '1: ', cur_spd, datetime.datetime.combine(tmp_date, start_time) - basis, new_start_time
    except:
        new_start_time = (datetime.datetime.combine(tmp_date, start_time) + datetime.timedelta(seconds=10)).time()  # !!
        # print '2: ', cur_spd, datetime.datetime.combine(tmp_date, start_time) - basis, new_start_time
    return new_start_time


# It gives a list of ratios for a specific link
def get_pv(arrival_time, arrival_time2, analysis_start_time, time_interval, tmp_date):
    # analysis_start_time is start_time which is (h)
    basis = datetime.datetime.combine(tmp_date, datetime.time(0, 0, 0))  # !!
    # arrival_time and arrival_time2 are the times that we depart the link if we start driving at start_time (h) and start_time2 (h+1) respectively
    arrival_time_date = datetime.datetime.combine(tmp_date, arrival_time)
    arrival_time_date2 = datetime.datetime.combine(tmp_date, arrival_time2)
    total = np.float((arrival_time_date2 - arrival_time_date).total_seconds())
    cur_time_date = datetime.datetime.combine(tmp_date, analysis_start_time)
    pv = list()
    # for \ro(h1, h2) we only check h1 (arrival_time_date) up to h2 (arrival_time_date2). h2 is the latest time that we can depart the link
    while (cur_time_date < arrival_time_date2):
        # time_interval is 5 minutes >>> time_interval = datetime.timedelta(minutes=5)
        cur_time_date2 = cur_time_date + time_interval
        # overlap(t, t+5minutes, h, h+5minutes) >> MIN(cur_time_date2, arrival_time_date2) - MAX(cur_time_date, arrival_time_date)
        overlap_zone = overlap((cur_time_date - basis).total_seconds(), (cur_time_date2 - basis).total_seconds(),
                               (arrival_time_date - basis).total_seconds(),
                               (arrival_time_date2 - basis).total_seconds())
        #         print np.float(overlap_zone) / total
        # pv is something like >> [0, 0, ..., 0, 5, 5, ..., 5, 0, 0, ..., 0]
        # First 5 is at MAX(cur_time_date, arrival_time_date) = cur_time_date
        # Last 5 is at MIN(cur_time_date2, arrival_time_date2) = arrival_time_date2
        # print "np.float(overlap_zone) / total: ", np.float(overlap_zone) / total
        pv.append(np.float(overlap_zone) / total)
        cur_time_date = cur_time_date2
    return pv


def get_arrival_time(start_time, link, spd_data, tmp_date, link_dict):
    link_to_pass = link

    # If link has 0 length >>> time of traversing is zero >>> return the time without any change
    if link_to_pass.length == np.float(0):
        return start_time

    # If the speed data of link is not available
    if link_to_pass.ID not in spd_data.keys():
        new_start_time = (datetime.datetime.combine(tmp_date, start_time) + datetime.timedelta(
            seconds=link_to_pass.fft)).time()
        return new_start_time

    # If the speed data of link is available
    try:
        # .loc[tmp_date] is the row of the speed at this specific day
        # spd_data[link_to_pass.ID] is the data of sensor with ID of checked link which is link_to_pass.ID
        spd = spd_data[link_to_pass.ID].loc[tmp_date]  # !!
    # If the speed data of link is not available
    except:
        new_start_time = (datetime.datetime.combine(tmp_date, start_time) + datetime.timedelta(
            seconds=link_to_pass.fft)).time()
        return new_start_time
    length_togo = link_to_pass.length

    # 000099: gets the speed data of a link at a day, length and start time to find the finish_time. finish_time = time that we reach the destination
    # print "link.ID: ", link.ID
    new_start_time = get_finish_time(spd, length_togo, start_time, tmp_date)
    return new_start_time


def get_ratio(path, h, spd_data, analysis_start_time, time_interval, tmp_date, link_dict):
    # time_interval is 5 minutes
    pv_dict = dict()

    # RATIO AT TIME (tmp_date and "'h * time_interval' to '(h+1) * time_interval'")
    # tmp_date = tmp_date in the DPFE-v0.1 file >>> "for tmp_date in date_need_to_finish", between (2014, 1, 1) and (2016, 12, 31)
    # For instance, "(2014, 1, 1) 1:10:00" to "(2014, 1, 1) 1:15:00"
    start_time = (datetime.datetime.combine(tmp_date, analysis_start_time) + h * time_interval).time()
    start_time2 = (datetime.datetime.combine(tmp_date, analysis_start_time) + (h + 1) * time_interval).time()
    arrival_time = copy.copy(start_time)
    arrival_time2 = copy.copy(start_time2)

    # Iterating over links in this specific path
    for link in path.link_list:
        # arrival_time: time that if we depart origin at arrival_time (h) we reach the destination
        arrival_time = get_arrival_time(arrival_time, link, spd_data, tmp_date, link_dict)
        # arrival_time2: time that if we depart origin at arrival_time2 (h+1) we reach the destination
        arrival_time2 = get_arrival_time(arrival_time2, link, spd_data, tmp_date, link_dict)

        # p_v is a list of ratios for a specific link
        # arrival_time and arrival_time2 are the times that we depart the link if we start driving at start_time and start_time2 respectively
        p_v = get_pv(arrival_time, arrival_time2, start_time, time_interval, tmp_date)
        # print "p_v0: ", p_v
        # print "link.ID0: ", link.ID
        pv_dict[link] = p_v
    return pv_dict


def get_assign_matrix(N, spd_data, analysis_start_time, time_interval, tmp_date, link_dict, link_list, link_loc,
                      path_list):
    num_link = len(link_list)
    # print "num_link: ", num_link  # debugging
    num_path = len(path_list)
    # print "num_path: ", num_path  # debugging
    row_list = list()
    col_list = list()
    data_list = list()
    # counter: debugging
    counter = 1
    # Constructing the rows of assignment matrix by iterating over "paths"
    # k: counter of paths
    # path: it is a Path object
    for k, path in enumerate(path_list):
        #         if k % 1 == 0:
        #             print k, len(path_list), len(path.link_list)
        # Iterating over number of time intervals (N=288 for 24 hours)
        # h = 0 to N-1
        # print "\n\ncounter: ", counter  # debugging
        # print "k: ", k  # debugging
        # print "path: ", path  # debugging
        counter += 1  # debugging
        # h: time interval
        for h in xrange(N):
            # print "h: ", h  # debugging
            # analysis_start_time = datetime.time(0, 0, 0)
            # time_interval is 5 minutes >>> time_interval = datetime.timedelta(minutes=5)
            # tmp_date = tmp_date in the DPFE-v0.1 file >>> "for tmp_date in date_need_to_finish", between (2014, 1, 1) and (2016, 12, 31)
            # get_ratio: gives the \ro ratio of links in a path (elements of DAR matrix)
            # pv_dict: dictionary of overlap ratio of links in the path
            # pv_dict: keys are link objects of the links that are included in the path.
            # pv_dict: values are vector of overlap of the link in different time intervals
            pv_dict = get_ratio(path, h, spd_data, analysis_start_time, time_interval, tmp_date, link_dict)
            #             print pv_dict
            # .iteritems() is .items() and it is removed in python3.x
            # For loop on the pv_dict which is explained above. It iterates over keys (link) and values (p_v).
            # Here, we have processed the first path. We need to know the location of links in the path 
            for link, p_v in pv_dict.iteritems():
                # print "p_v: ", p_v  # debugging
                # a is the index of the link in the link_list.
                # This link is included in the path
                # This link_loc gives the column index of link in the columns of path. For instance, 10th link in system
                # is the 2nd link in the path.
                # We give "link" to "link_loc" and it gives the index.
                a = link_loc[link]
                # For loop on the all the combinations of (h1, h2) for the specific link in the specific path
                # h + idx = h2 - 1
                # h = h1 - 1
                for idx, p in enumerate(p_v):
                    # print "idx: ", idx  # debugging
                    # print "p: ", p  # debugging
                    if (h + idx < N): # His code
                    # if (idx < N): # My code
                        # row index of the element >> Paper, page 7, Table 2, Description
                        y_loc = a + num_link * (h + idx) # His code
                        # y_loc = a + num_link * (idx) # My code
                        # print "y_loc: ", y_loc  # debugging
                        # column index of the element >> Paper, page 7, Table 2, Description
                        x_loc = k + num_path * h
                        # if x_loc>30000:
                        #     print "x_loc: ", x_loc
                        #     print "y_loc: ", y_loc
                        # print "x_loc: ", x_loc  # debugging
                        row_list.append(y_loc)
                        col_list.append(x_loc)
                        data_list.append(p)
                        # print "y_loc: ", y_loc # debugging
                        # print "x_loc: ", x_loc # debugging
                        # print "p: ", p # debugging
    #     print row_list, col_list
    # csr_matrix: includes the value of elements (in the data_list) and their index in the matrix but in two 1-D arrays (row_list ad col_list)
    r = csr_matrix((data_list, (row_list, col_list)), shape=(num_link * N, num_path * N))
    return r



# single_date: tmp_date in the other file, it is the variable iterates over time interval list
def save_r(N, spd_data, analysis_start_time, time_interval, single_date, link_dict, link_list, link_loc, path_list,
           region_, fileNameSetting1, folderADMM, folderRun):
    import joblib
    # Changing the format of single_date to string to print
    date_str = single_date.strftime("%Y-%m-%d")
    print "date_str:", date_str
    # N = 204
    # analysis_start_time = datetime.time(0, 0, 0) !!
    # time_interval is 5 minutes >>> time_interval = datetime.timedelta(minutes=5)
    # single_date = tmp_date in the DPFE-v0.1 file >>> "for tmp_date in date_need_to_finish", between (2014, 1, 1) and (2016, 12, 31)
    # shape=(num_link * N, num_path * N)
    r = get_assign_matrix(N, spd_data, analysis_start_time, time_interval, single_date, link_dict, link_list, link_loc,
                          path_list)
    # print "r:", r
    joblib.dump(r, os.path.join('../data', region_, fileNameSetting1, folderADMM, folderRun, "R"+date_str+".pickle"))
    pickle.dump(r, open(os.path.join('../data', region_, fileNameSetting1, folderADMM, folderRun, "R"+date_str+"_pck.pickle"), "wb"))


# def softmax(x, incentive, theta=-0.01):
def softmax(x, theta=1):

    #     print x
    """Compute softmax values for each sets of scores in x."""
    # Multiplication by theta to make the values of np.exp(.) more reasonable
    # y = np.copy(x) * theta
    y = (np.copy(x)/60.0 * -0.086) * theta

    # print y
    p = np.minimum(np.maximum(np.exp(y), 1e-20), 1e20) / np.sum(np.minimum(np.maximum(np.exp(y), 1e-20), 1e20), axis=0)
    #     print p
    # If any element of p is Nan, return equal probablity for all the paths
    if np.isnan(p).any():
        p = np.ones(len(x)) / len(x)
    return p


def get_full_arrival_time(start_time, link_list, spd_data, tmp_date, link_dict, spd=None):
    #     if len(link_list) == 0:
    #         return start_time
    #     link_to_pass = link_list[0]
    #     if link_to_pass.length == np.float(0):
    #         link_list.pop(0)
    #         return get_full_arrival_time(start_time, link_list, spd_data, tmp_date, link_dict)
    #     if link_to_pass.ID not in spd_data.keys():
    #         link_list.pop(0)
    #         new_start_time = (datetime.datetime.combine(tmp_date, start_time) + datetime.timedelta(seconds = np.round(link_to_pass.fft))).time()
    #         return get_full_arrival_time(new_start_time, link_list, spd_data, tmp_date, link_dict)
    #     if type(spd) == type(None):
    #         spd = spd_data[link_to_pass.ID].loc[tmp_date]
    #     length_togo = link_to_pass.length
    #     new_start_time = get_finish_time(spd, length_togo, start_time, tmp_date)
    #     link_list.pop(0)
    arrival_time = copy.copy(start_time)
    for link in link_list:
        # Given the arrival_time to the last link, when is the departure time of the current link in the path?
        # Note that the we give the last arrival_time and we get the new one.
        arrival_time = get_arrival_time(arrival_time, link, spd_data, tmp_date, link_dict)
    return arrival_time


# tmp_date = datetime.date(2014, 1, 1)
# Generating route choice matrix
def get_P(N, spd_data, analysis_start_time, time_interval, tmp_date, path_list, OD_paths, theta):
    # vector of number of paths between each OD pair
    num_path_v = [len(x) for x in OD_paths.itervalues()]
    # Total number of paths
    num_path = np.sum(num_path_v)
    OD_list = list(OD_paths.keys())
    num_OD = len(OD_list)
    row_list = list()
    col_list = list()
    data_list = list()
    for h in xrange(N):
        #         print h, N
        start_time = (datetime.datetime.combine(tmp_date, analysis_start_time) + h * time_interval).time()
        # First finding the probabilities and assigning them ti "p" attribute of the Path objects
        for (O, D), paths in OD_paths.iteritems():
            #         print (O,D)
            # List of cost of different paths between a specific OD pair
            cost_list = list()
            for path in paths:
                # Given start driving from origin at start_time, when do we reach the destination? ans: arrival_time
                arrival_time = get_full_arrival_time(start_time, path.link_list, spd_data, tmp_date, None)
                cost = (datetime.datetime.combine(tmp_date, arrival_time) - datetime.datetime.combine(tmp_date,
                                                                                                      start_time)).total_seconds()
                # "cost" is an attribute of Path objects >> Travel time of the path
                path.cost = cost
                cost_list.append(cost)
            # p_list = softmax(cost_list)
            p_list = softmax(cost_list, theta)
            # print "cost_list:", cost_list
            # print "p_list:", p_list
            for idx, path in enumerate(paths):
                # "p" is an attribute of Path objects which is the probability of acceptance
                path.p = p_list[idx]
        #         print p_list
        # Second, assigning the generate probabilities to the route choice matrix
        # OD pair rs
        for rs, (O, D) in enumerate(OD_list):
            # Path k of OD
            for k, path in enumerate(path_list):
                # Iterating over all the paths between (O, D)
                if k < np.sum(num_path_v[0:rs + 1]) and k >= np.sum(num_path_v[0:rs]):
                    # (h-1)*|K| + rs >> Paper, page 7, Table 2, Description
                    x_loc = h * num_OD + rs
                    # (h-1)*|PI| + k >> Paper, page 7, Table 2, Description
                    y_loc = h * num_path + k
                    # Vector of probabilities of paths between OD
                    data = path.p
                    row_list.append(y_loc)
                    col_list.append(x_loc)
                    data_list.append(data)
    P = csr_matrix((data_list, (row_list, col_list)), shape=(num_path * N, num_OD * N))
    return P


def save_p(N, spd_data, analysis_start_time, time_interval, single_date, path_list, OD_paths, region_, fileNameSetting1, folderADMM, folderRun, theta):
    import joblib
    date_str = single_date.strftime("%Y-%m-%d")
    print "date: ", date_str
    P = get_P(N, spd_data, analysis_start_time, time_interval, single_date, path_list, OD_paths, theta)
    # print P
    joblib.dump(P, os.path.join('../data', region_, fileNameSetting1, folderADMM, folderRun, "P"+date_str+"_0.pickle"))
    pickle.dump(P, open(os.path.join('../data', region_, fileNameSetting1, folderADMM, folderRun, "P"+date_str+"_0_pck.pickle"), "wb"))


def softmax_opt(x, incentive, idx_i, theta=1):

    #     print x
    """Compute softmax values for each sets of scores in x."""
    # Multiplication by theta to make the values of np.exp(.) more reasonable
    # y = np.copy(x) * theta
    y = (np.copy(x)/60.0 * -0.086 + 0 * 0.7) * theta

    y[idx_i] = (np.copy(x[idx_i])/60.0 * -0.086 + incentive * 0.7) * theta
    # print y
    p = np.minimum(np.maximum(np.exp(y), 1e-20), 1e20) / np.sum(np.minimum(np.maximum(np.exp(y), 1e-20), 1e20), axis=0)
    # print y

    # If any element of p is Nan, return equal probablity for all the paths
    if np.isnan(p).any():
        p = np.ones(len(x)) / len(x)
    return p


def get_P_opt(N, spd_data, analysis_start_time, time_interval, tmp_date, path_list_opt, OD_paths_opt, incentive, theta):
    # vector of number of paths between each OD pair
    num_path_v = [len(x) for x in OD_paths_opt.itervalues()]
    # Total number of paths
    num_path = np.sum(num_path_v)
    OD_list_opt = list(OD_paths_opt.keys())
    num_OD = len(OD_list_opt)
    row_list = list()
    col_list = list()
    data_list = list()
    for h in xrange(N):
        # print h, N
        start_time = (datetime.datetime.combine(tmp_date, analysis_start_time) + h * time_interval).time()
        # First finding the probabilities and assigning them ti "p" attribute of the Path objects
        for (O, D), paths_opt in OD_paths_opt.iteritems():
            # print (O,D)
            # List of cost of different paths_opt between a specific OD pair
            cost_list = list()
            for path_opt in paths_opt:
                # Given start driving from origin at start_time, when do we reach the destination? ans: arrival_time
                arrival_time = get_full_arrival_time(start_time, path_opt.link_list, spd_data, tmp_date, None)
                cost = (datetime.datetime.combine(tmp_date, arrival_time) - datetime.datetime.combine(tmp_date,
                                                                                                      start_time)).total_seconds()
                # "cost" is an attribute of Path objects >> Travel time of the path_opt
                path_opt.cost = cost
                cost_list.append(cost)
            # p_list = softmax(cost_list)
            p_list = list()
            for idx_i in range(len(paths_opt)):
                # idx_i: the index of the path to which incentive is assigned
                p_list.append(softmax_opt(cost_list, incentive, idx_i, theta)) # ^^
            # print "cost_list:", cost_list
            # print "p_list:", p_list
            for idx_path, path_opt in enumerate(paths_opt):
                p_list_temp = list()
                # idx_i: index of the incentive assignment plan
                for idx_i in range(len(paths_opt)):
                    p_list_temp.append(p_list[idx_i][idx_path])
                    # print "p_list_temp:", p_list_temp
                # "p" is an attribute of Path objects which is the probability of acceptance
                # path_opt.p = p_list[idx_path]  # His code
                path_opt.p = p_list_temp  # My code
                # print "path_opt:", path_opt
                # print "p:", path_opt.p
        #         print p_list

        # Creating the vector of index of the OD pairs
        idx_x = [0]
        idx_x_temp = 0
        for rs, (O, D) in enumerate(OD_list_opt):
            n_path_temp = int(np.sum(num_path_v[rs]))
            idx_x_temp += n_path_temp
            idx_x.append(idx_x_temp)
        # Second, assigning the generate probabilities to the route choice matrix
        # OD pair rs
        for rs, (O, D) in enumerate(OD_list_opt):
            # Path k of OD
            for k, path_opt in enumerate(path_list_opt):
                # Iterating over all the paths_opt between (O, D)
                idx_path_first = np.sum(num_path_v[0:rs])
                idx_path_next = np.sum(num_path_v[0:rs + 1])
                num_path_OD = int(idx_path_next - idx_path_first)
                # num_path_SoFar = idx_path_first
                if k >= idx_path_first and k < idx_path_next:
                    for iter_i in range(num_path_OD):
                        # x_loc = h*num_OD + rs
                        x_loc = idx_x[rs] + iter_i
                        # print "x_loc:", x_loc
                        y_loc = h*num_path + k
                        # print "y_lock:", y_loc
                        # Vector of probabilities of paths_opt between OD
                        data = path_opt.p[iter_i]
                        # print "data:", data
                        # print "\n"
                        row_list.append(y_loc)
                        col_list.append(x_loc)
                        data_list.append(data)
    P = csr_matrix((data_list, (row_list, col_list)), shape=(num_path * N, num_path))
    return P


def save_p_opt(N, spd_data, analysis_start_time, time_interval, single_date, path_list_opt, OD_paths_opt, region_, fileNameSetting1, folderADMM, folderRun, incentive, theta):
    import joblib
    date_str = single_date.strftime("%Y-%m-%d")
    print "date: ", date_str
    print "incentive: ", incentive
    P = get_P_opt(N, spd_data, analysis_start_time, time_interval, single_date, path_list_opt, OD_paths_opt, incentive, theta)
    # print P
    joblib.dump(P, os.path.join('../data', fileNameSetting1, folderADMM, folderRun, "POpt"+date_str + "_" + str(incentive) + ".pickle"))
    pickle.dump(P, open(os.path.join('../data', fileNameSetting1, folderADMM, folderRun, "POpt"+date_str + "_" + str(incentive) + "_pck.pickle"), "wb"))


def softmax_opt0(x, theta=1):
    y = (np.copy(x)/60.0 * -0.086) * theta
    p = np.minimum(np.maximum(np.exp(y), 1e-20), 1e20) / np.sum(np.minimum(np.maximum(np.exp(y), 1e-20), 1e20), axis=0)
    if np.isnan(p).any():
        p = np.ones(len(x)) / len(x)
    return p


def get_P_opt0(N, spd_data, analysis_start_time, time_interval, tmp_date, path_list, OD_paths, theta):
    num_path_v = [len(x) for x in OD_paths.itervalues()]
    num_path = np.sum(num_path_v)
    OD_list = list(OD_paths.keys())
    num_OD = len(OD_list)
    row_list = list()
    col_list = list()
    data_list = list()
    for h in xrange(N):
        start_time = (datetime.datetime.combine(tmp_date, analysis_start_time) + h * time_interval).time()
        for (O, D), paths in OD_paths.iteritems():
            cost_list = list()
            for path in paths:
                arrival_time = get_full_arrival_time(start_time, path.link_list, spd_data, tmp_date, None)
                cost = (datetime.datetime.combine(tmp_date, arrival_time) - datetime.datetime.combine(tmp_date,
                        start_time)).total_seconds()
                path.cost = cost
                cost_list.append(cost)
            p_list = softmax_opt0(cost_list, theta)
            for idx, path in enumerate(paths):
                path.p = p_list[idx]
        for rs, (O, D) in enumerate(OD_list):
            for k, path in enumerate(path_list):
                if k < np.sum(num_path_v[0:rs + 1]) and k >= np.sum(num_path_v[0:rs]):
                    x_loc = rs
                    y_loc = h * num_path + k
                    data = path.p
                    row_list.append(y_loc)
                    col_list.append(x_loc)
                    data_list.append(data)
    P = csr_matrix((data_list, (row_list, col_list)), shape=(num_path * N, num_path))
    return P


def save_p_opt0(N, spd_data, analysis_start_time, time_interval, single_date, path_list_opt, OD_paths_opt, region_, fileNameSetting1, folderADMM, folderRun, theta):
    import joblib
    date_str = single_date.strftime("%Y-%m-%d")
    print "date: ", date_str
    P = get_P_opt0(N, spd_data, analysis_start_time, time_interval, single_date, path_list_opt, OD_paths_opt, theta)
    joblib.dump(P, os.path.join('../data', region_, fileNameSetting1, folderADMM, folderRun, "POpt"+date_str + "_0.pickle"))
    pickle.dump(P, open(os.path.join('../data', region_, fileNameSetting1, folderADMM, folderRun, "POpt"+ date_str + "_0_pck.pickle"), "wb"))

def to_south((O, D)):
    real_O = O % 1000
    real_D = D % 1000
    return real_O < real_D


def k_shortest_paths(G, source, target, k, weight='length'):  # !! My code
    return list(islice(nx.shortest_simple_paths(G, source, target, weight=weight), k))  # !! My code

# #############################################
def get_tt(N, spd_data, analysis_start_time, time_interval, tmp_date, path_list, OD_paths):
    # vector of number of paths between each OD pair
    num_path_v = [len(x) for x in OD_paths.itervalues()]
    # Total number of paths
    num_path = np.sum(num_path_v)
    max_num_path = max(num_path_v)
    OD_list = list(OD_paths.keys())
    num_OD = len(OD_list)
    # row_list = list()
    # col_list = list()
    # data_list = list()
    tt = np.zeros((max_num_path * N, num_OD))
    for h in xrange(N):
        #         print h, N
        start_time = (datetime.datetime.combine(tmp_date, analysis_start_time) + h * time_interval).time()
        # First finding the probabilities and assigning them ti "p" attribute of the Path objects
        for (O, D), paths in OD_paths.iteritems():
            #         print (O,D)
            # List of cost of different paths between a specific OD pair
            cost_list = list()
            for path in paths:
                # Given start driving from origin at start_time, when do we reach the destination? ans: arrival_time
                arrival_time = get_full_arrival_time(start_time, path.link_list, spd_data, tmp_date, None)
                cost = (datetime.datetime.combine(tmp_date, arrival_time) - datetime.datetime.combine(tmp_date,
                                                                                                      start_time)).total_seconds()
                # "cost" is an attribute of Path objects >> Travel time of the path
                path.cost = cost
                # cost_list.append(cost)
            # # p_list = softmax(cost_list)
            # p_list = softmax(cost_list, theta)
            # # print "cost_list:", cost_list
            # # print "p_list:", p_list
            # for idx, path in enumerate(paths):
            #     # "p" is an attribute of Path objects which is the probability of acceptance
            #     path.p = p_list[idx]
        #         print p_list
        # Second, assigning the generate probabilities to the route choice matrix
        # OD pair rs
        for rs, (O, D) in enumerate(OD_list):
            # print "\n\n\nrs:", rs
            counter = 0
            # Path k of OD
            for k, path in enumerate(path_list):
                # Iterating over all the paths between (O, D)
                if k < np.sum(num_path_v[0: rs + 1]) and k >= np.sum(num_path_v[0: rs]):
                    # print "k:", k
                    # print "counter:", counter
                    x_loc = rs
                    # print "x_loc:", x_loc
                    # y_loc = h * num_path + k
                    y_loc = h * max_num_path + counter
                    # print "y_loc:", y_loc
                    # Vector of probabilities of paths between OD
                    # data = path.p
                    data = path.cost
                    tt[y_loc, x_loc] = data
                    # row_list.append(y_loc)
                    # col_list.append(x_loc)
                    # data_list.append(data)
                    counter += 1
                else:
                    counter = 0
    # tt = csr_matrix((data_list, (row_list, col_list)), shape=(max_num_path * N, num_OD))
    return tt


def save_tt(N, spd_data, analysis_start_time, time_interval, single_date, path_list_opt, OD_paths_opt, region_, fileNameSetting1, folderADMM, folderRun):
    import joblib
    date_str = single_date.strftime("%Y-%m-%d")
    print "date: ", date_str
    tt = get_tt(N, spd_data, analysis_start_time, time_interval, single_date, path_list_opt, OD_paths_opt)
    # print tt
    # joblib.dump(tt, os.path.join('P_matrix_opt', new_file, date_str + ".pickle"))
    # pickle.dump(tt, open(os.path.join("tt", new_file, date_str + ".pickle"), "wb"))
    tt.to_csv(open(os.path.join('../data', region_, fileNameSetting1, folderADMM, folderRun, "tt"+date_str+".csv"), "wb"))


def save_tt_joblib(N, spd_data, analysis_start_time, time_interval, single_date, path_list_opt, OD_paths_opt, region_, fileNameSetting1, folderADMM, folderRun):
    import joblib
    date_str = single_date.strftime("%Y-%m-%d")
    print "date: ", date_str
    tt = get_tt(N, spd_data, analysis_start_time, time_interval, single_date, path_list_opt, OD_paths_opt)
    # print tt
    joblib.dump(tt, os.path.join('../data', region_, fileNameSetting1, folderADMM, folderRun, "tt"+date_str+".pickle"))
    pickle.dump(tt, open(os.path.join('../data', region_, fileNameSetting1, folderADMM, folderRun, "tt"+date_str+"_pck.pickle"), "wb"))
    pd.DataFrame(tt).to_csv(open(os.path.join('../data', region_, fileNameSetting1, folderADMM, folderRun, "tt"+date_str+".csv"), "wb"), header=False, index=False)

