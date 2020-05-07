import json
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from operator import itemgetter
import matplotlib.pyplot as plt
import requests
from collections import Counter


# 将上一步的到的paths转换为无向图的边
def getUDEdges(paths):
    edges = []
    for k in paths:
        node = k.split('-')
        edges.append((node[0], node[1]))
    return edges


def getCBEdges(paths):
    edges = []
    for k, v in paths.items():
        weight = len(v)
        node = k.split('-')
        edges.append((node[0], node[1], {'no': weight}))
    return edges


def getTimeEdges(paths):
    edges = []
    for k, v in paths.items():
        tl = [e[0] for e in v]
        for i in range(len(tl)):
            if tl[i] <= 0:
                tl[i] = tl[i] + 1440

        weight = int(sum(tl)/len(v))
        nodes = k.split('-')
        edges.append((nodes[0], nodes[1], {'time': weight}))
    return edges


# 去掉 x-x 的边
def popdict(dict):
    list = []
    for path in dict:
        if path.split('-')[0] == path.split('-')[1]:
            list.append(path)

    for path in list:
        dict.pop(path)


def dopaths(nefile):
    Dinfo = loadinfo(nefile)
    stations = Dinfo[0]
    #print(len(stations))
    #print(f"contains {len(stations)} stations: {stations}")

    Dpaths = Dinfo[1]
    l = len(Dpaths)
    popdict(Dpaths)
    #print(f"paths len: {l}, quchonghou: {len(Dpaths)}")

    return stations, Dpaths


# 把动车，高铁的边集合并
def mergedges(dpaths, gpaths):
    allpaths = dict()
    for k in dpaths:
        allpaths[k] = dpaths[k]

    for kk in gpaths:
        if kk in allpaths:
            allpaths[kk].extend(gpaths[kk])
        else:
            allpaths[kk] = gpaths[kk]

    return allpaths



def loadinfo(injson):
    with open(injson, 'r', encoding='utf-8') as f:
        dinfo = json.load(f)
        return dinfo


def main():
    ds_gtw, dpaths_gtw = dopaths('DNode_Edge_gtw.json')
    gs_gtw, gpaths_gtw = dopaths('GNode_Edge_gtw.json')
    ds_xc, dpaths_xc = dopaths('DNode_Edge_xc.json')
    gs_xc, gpaths_xc = dopaths('GNode_Edge_xc.json')

    p1 = mergedges(dpaths_gtw, gpaths_gtw)
    p2 = mergedges(p1, dpaths_xc)
    allpaths = mergedges(p2, gpaths_xc)

    print(f"边总共有{len(allpaths)}条:")
    #print(allpaths)

    UDedges = getUDEdges(allpaths)
    CBEdges = getCBEdges(allpaths)
    TimeEdges = getTimeEdges(allpaths)
    nodes = set(ds_gtw) | set(gs_gtw) | set(ds_xc) | set(gs_xc)
    print(f"聚合后城市有{len(nodes)}个:")
    # print(nodes)

    ###############################################
    # 简单无向图模型
    print('------简单无向图----------------------------')

    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(UDedges)

    print('--点度数-----')
    deg = G.degree()
    sdeg = sorted(deg, key=lambda x: (x[1]), reverse=True)
    print(sdeg)
    ns = len(deg)

    degv = [x[1] for x in sdeg]
    print(degv)
    maxdeg = max(degv)
    result = list(range(maxdeg+1))
    print(len(result))
    for i in range(maxdeg+1):
        result[i] = degv.count(i)
    print(result)

    # 幂律处理
    j = 1
    tmp = 0
    mi = list(range(6))
    for i in range(maxdeg):
        if i <= 2**j:
            tmp += result[i]
        else:
            mi[j-1] = tmp
            j += 1
            tmp = result[i]

    print(mi)
    x = [2**(i+1) for i in range(6)]
    plt.semilogx(x, mi)
    plt.show()

    # 点介数
    print('--点介数-----')
    betweenness = nx.algorithms.centrality.betweenness_centrality(G, endpoints=True)
    sbetweenness = sorted(betweenness.items(), key=lambda x: (x[1]), reverse=True)
    print(sbetweenness)
    x = [k[1] for k in sbetweenness]
    plt.plot(x)
    plt.show()

    asp = nx.algorithms.shortest_paths.generic.average_shortest_path_length(G)
    print(f'--平均最短路径长度为: {asp}')

    print('--聚类系数-----')
    clu = nx.algorithms.cluster.clustering(G, weight='time')
    sclu = sorted(clu.items(), key=lambda y: (y[1]), reverse=False)
    print(sclu)
    x = [k[1] for k in sclu]
    plt.plot(x)
    plt.show()
    ''''''

    ###############################################
    # 考虑重边模型
    '''
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(CBEdges)

    deg = G.degree(weight='no')
    sdeg = sorted(deg, key=lambda x: (x[1]), reverse=True)
    print(sdeg)
    ns = len(deg)

    degv = [x[1] for x in sdeg]
    print(degv)
    maxdeg = max(degv)
    result = list(range(maxdeg + 1))
    print(len(result))
    for i in range(maxdeg + 1):
        result[i] = degv.count(i)
    print(result)

    # 幂律处理
    j = 1
    tmp = 0
    mi = list(range(10))
    for i in range(maxdeg):
        if i <= 2 ** j:
            tmp += result[i]
        else:
            mi[j - 1] = tmp
            j += 1
            tmp = result[i]

    x = [2 ** (i + 1) for i in range(10)]
    plt.semilogx(x, mi)
    plt.show()

    # 累积概率分布
    leiji = list(range(maxdeg + 1))
    fenmu = sum(result)
    for i in range(maxdeg + 1):
        leiji[i] = sum(result[i:-1])/fenmu

    plt.semilogx(leiji)
    plt.show()
    
    
    '''
    #############################################
    # 时间赋权图
    print('------时间赋权图----------------------------')
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(TimeEdges)

    # 点介数
    print('--点介数-----')
    betweenness = nx.algorithms.centrality.betweenness_centrality(G, weight='time', endpoints=True)
    sbetweenness = sorted(betweenness.items(), key=lambda y: (y[1]), reverse=True)
    print(sbetweenness)
    x = [k[1] for k in sbetweenness]
    plt.plot(x)
    plt.show()

    asp = nx.algorithms.shortest_paths.generic.average_shortest_path_length(G, weight='time')
    print(f'--平均最短路径长度为: {asp}')

    print('--聚类系数-----')
    clu = nx.algorithms.cluster.clustering(G, weight='time')
    sclu = sorted(clu.items(), key=lambda y: (y[1]), reverse=False)
    print(sclu)
    x = [k[1] for k in sclu]
    plt.plot(x)
    plt.show()
    ''''''


    # 其他
    '''
    G = nx.DiGraph()

    stations, trains = getSandT()
    print('stations: %d' % len(stations))

    # odd 是被聚类去掉的站点
    edges, odd = getS_Tedge(stations)
    print('odds: %d' % len(odd))

    sj = stations - odd
    print('stations - odds: %d' % len(sj))

    paths = getTimePaths(sj)
    timedges = getTimeEdges(paths)

    
    # 赋权图
    G.add_nodes_from(sj)
    G.add_edges_from(timedges)
    
    btw = nx.algorithms.centrality.betweenness_centrality(G, weight='time')
    print(sorted(btw.items(), key=lambda x: (x[1]), reverse=True))

    btw = nx.algorithms.centrality.betweenness_centrality(G)
    print(sorted(btw.items(), key=lambda x: (x[1]), reverse=True))

    deg = G.degree()
    print(sorted(deg, key=lambda x: (x[1]), reverse=True))
    data = [x[1] for x in deg if x[1] > 0]
    data1 = [len(bin(d))-1 for d in data]

    
    sub = [node[0] for node in deg if node[1] == 2]

    addons = [ '湛江', '北海', '福州', '上海']
    st = set(sub) | set(addons)

    
    
    btw = nx.algorithms.centrality.betweenness_centrality_subset(G,  weight='time', sources=st, targets=st)
    print(sorted(btw.items(), key=lambda x: (x[1]), reverse=True))
    btw = nx.algorithms.centrality.betweenness_centrality_subset(G, sources=st, targets=st)
    print(sorted(btw.items(), key=lambda x: (x[1]), reverse=True)
    

    # 二部图
    edges, odd = getS_Tedge(stations)
    print(len(odd))

    G1 = nx.DiGraph()

    G1.add_nodes_from(trains)
    G1.add_nodes_from(sj)
    G1.add_edges_from(edges)

    ind = G1.in_degree()
    print(ind)
    print(sorted(ind, key=lambda x: (x[1]), reverse=True))
    data = [x[1] for x in ind if x[1] > 0]
    data1 = [len(bin(d)) - 1 for d in data]


    # print(data)
    plt.hist(data1, bins=100)
    plt.show()

    fig1, ax1 = plt.subplots()
    ax1.hist(data, bins=100)
    ax1.set_xscale("log")
    ax1.set_xlim(1e0, 1e2)
    ax1.grid()
    plt.draw()
    plt.show()'''


if __name__ == "__main__":
    main()



