import networkx as nx
import requests


def jisuan(n, m):
    G = nx.generators.random_graphs.gnm_random_graph(n, m)
    betweenness = nx.algorithms.centrality.betweenness_centrality(G, endpoints=True)
    #print(betweenness)
    total = 0
    for key in betweenness:
        total += betweenness[key]

    print(f'n:{n},m:{m}; total betweenness:{total}')


for i in range(10):
    jisuan(30, 400)

'''


key = '27ea3472ed190ddbc5e3160188e74111'
address = '蓟州站'
url = f'https://restapi.amap.com/v3/geocode/geo?address={address}&key={key}'

r = requests.get(url)
d = r.json()
print(d)
if d["count"] == '0':  # 未查到该车站
    print(0)
else:
    city = d['geocodes'][0]['city']
    print(city)
'''
