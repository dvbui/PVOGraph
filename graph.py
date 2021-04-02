from access_parser import AccessParser
import networkx as nx
from pyvis.network import Network

database_path = input("Nhap ten file: ")
concepts = input("Nhap cac concept can ve cay: ")
concepts = concepts.split(', ')
db = AccessParser(database_path)
db.print_database()
concept_table = db.parse_table("tblWord")
example_table = db.parse_table("tblExample")
concept_relation_table = db.parse_table("tblWordRelation")
example_relation_table = db.parse_table("tblWordExampleRelation")
G = nx.DiGraph()

list_of_nodes = []
list_of_edges = []

def get_concept_from_id(concept_id):
    index = concept_table["ID"].index(concept_id)
    return concept_table["Word"][index]

def get_example_from_id(example_id):
    index = example_table["ExampleID"].index(example_id)
    return example_table["Keywords"][index]
    
def find_concept_neighbor(concept_id):
    list_of_neighbors = []
    for i in range(len(concept_relation_table["ID1"])):
        if concept_relation_table["ID1"][i] == concept_id:
            list_of_neighbors.append(concept_relation_table["ID2"][i])
    return list_of_neighbors

def find_example_neighbor(concept_id):
    list_of_neighbors = []
    for i in range(len(example_relation_table["wID"])):
        if example_relation_table["wID"][i] == concept_id:
            list_of_neighbors.append(example_relation_table["eID"][i])
    return list_of_neighbors
    
def draw(concept_id):
    print("draw", concept_id)
    if ("concept", concept_id) in list_of_nodes:
        return
    list_of_nodes.append(("concept", concept_id))
    neighbors = find_concept_neighbor(concept_id)
    
    for n in neighbors:
        draw(n)
        list_of_edges.append((("concept", concept_id), ("concept", n)))
    
    neighbors = find_example_neighbor(concept_id)
    for n in neighbors:
        list_of_nodes.append(("example", n))
        list_of_edges.append((("concept", concept_id), ("example", n)))


for concept in concepts:
    if not concept in concept_table["Word"]:
        print("Khong tim thay {}".concept)
        continue
    concept_id = concept_table["ID"][concept_table["Word"].index(concept)]
    draw(concept_id)


G.add_nodes_from([
    (hash(node), {"label": get_concept_from_id(node[1]) if node[0]=="concept" else get_example_from_id(node[1]),
            "color": "blue" if node[0]=="concept" else "orange"})
    for node in list_of_nodes
])
G.add_edges_from([(hash(edge[0]), hash(edge[1])) for edge in list_of_edges])

net = Network()

net.from_nx(G)

net.show("example.html")

