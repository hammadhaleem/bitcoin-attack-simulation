import networkx as nx
from nltk.corpus import words
import difflib, pprint
from tqdm import tqdm

pp = pprint.pprint

word_list = words.words()

word_list = [i.lower() for i in word_list]

word_list = list(sorted(filter(lambda x: len(x) < 5, word_list)))

def string_diff(s1, s2):
	count = max(len(s1), len(s2))
	s = difflib.SequenceMatcher(None, s1, s2)
	data = s.find_longest_match(0,len(s1),0,len(s2))
	if count - data.size == 1:
		return True

	return False

def construct_graph(word_list, load=True, file_name="word_graph.csv"):
	done = []
	if load is False:
		G=nx.Graph()
		edges= []

		for index1 in tqdm(range(len(word_list))):

			w1 = word_list[index1]
			G.add_node(w1)

			for index2 in range(index1+1, len(word_list)):
				w2 = word_list[index2]
				w1,w2 = max(w1, w2), min(w1,w2)

				if abs(len(w2) - len(w1)) <=1 and w1 != w2:
					if string_diff(w1,w2) == True:
						edges.append([w1,w2])

		G.add_edges_from(edges)

		fh=open(file_name,'wb')
		nx.write_edgelist(G, fh)
		fh.close()

	else:
		fh=open(file_name, 'r')
		G=nx.read_edgelist(fh)
		fh.close()

	return G



G = construct_graph(word_list, load=True)
w1,w2 = input("Please enter 2 words, seperated by space (`a  aal`) ").lower().split(" ")

if w1 in G.nodes() and w2 in G.nodes():
	try:
		path = nx.shortest_path(G,source=w1,target=w2)
	except:
		path = []
	print("Path : {}".format(path))
else:
	print("Not in our dictionary")