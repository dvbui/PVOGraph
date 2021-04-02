from access_parser import AccessParser
import networkx as nx
from pyvis.network import Network
from striprtf.striprtf import rtf_to_text

database_path = input("File: ")
concepts = input("Concept(s): ")
concepts = concepts.split(',')
example_type = input("Example Type (E for Example, K for Keywords): ")
message = """Type(s) of Concept-Concept Relations:
0: No relation
1: General association
2: Of the same concept cluster
3: A part of
4: A type of
5: Describing
-1: All
"""
concept_relations = input(message)
concept_relations = list(map(int,concept_relations.split(",")))
if concept_relations == [-1]:
    concept_relations = range(0,6)
    
message = """Type(s) of Example-Concept Relations:
0: Same concept or subconcept
1: Related concepts
2: Doer of action
3: Receiver of action
4: Action
5: Being described by
6: Describing
7: Idiom & fixed expressions
8: Related phrases
9: Pun/Word play
10: Other examples
11: Temporarily uncategorized
-1: All
"""

example_relations = input(message)
example_relations = list(map(int,example_relations.split(",")))
if example_relations == [-1]:
    example_relations = range(0,12)

db = AccessParser(database_path)
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
    if example_type.upper() == "E":
        return rtf_to_text(str(example_table["Description"][index]))
    else:
        return str(example_table["Keywords"][index])
    
def find_concept_neighbor(concept_id):
    list_of_neighbors = []
    for i in range(len(concept_relation_table["ID1"])):
        if concept_relation_table["ID1"][i] == concept_id and concept_relation_table["Relation"][i] in concept_relations:
            list_of_neighbors.append(concept_relation_table["ID2"][i])
    return list_of_neighbors

def find_example_neighbor(concept_id):
    list_of_neighbors = []
    for i in range(len(example_relation_table["wID"])):
        if example_relation_table["wID"][i] == concept_id and example_relation_table["Relation"][i] in example_relations:
            list_of_neighbors.append(example_relation_table["eID"][i])
    return list_of_neighbors
    
def draw(concept_id):
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
    index = -1
    for i in range(len(concept_table["Word"])):
        if index == -1 and concept_table["Word"][i].strip().lower() == concept.strip().lower():
            index = i
        if concept_table["Word"][i] == concept:
            index = i
    if index == -1:
        print("Khong tim thay {}".concept)
        continue
    concept_id = concept_table["ID"][index]
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

