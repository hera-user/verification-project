import pickle
import sys
import os
from build_graph import GraphBuilder
from create_label_for_file import Z3PartialInstantiator
import matplotlib.pyplot as plt
import networkx as nx
class Smt2Data:
    @staticmethod
    def convert_smt2_file(smt2_file, inst_str):
        G = GraphBuilder.construct(smt2_file, inst_str)
        nx.draw(G, with_labels=True)
        plt.show()
        label = Z3PartialInstantiator(smt2_file, inst_str).create_label()


        new_pickle_file_name = os.path.basename(smt2_file).replace(".smt2", "") + inst_str + ".pkl"
        with open(f"dataset/graphs/{new_pickle_file_name}", "wb") as f:
            pickle.dump(G, f)
        new_label_file = new_pickle_file_name.replace(".pkl", ".txt")
        with open(f"dataset/labels/{new_label_file}", "w") as f:
            f.write(str(label))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 partial_instantiate_smt2.py input.smt2 var1=val1,var2=val2,...")
        exit()

    filename = sys.argv[1]
    inst_str = sys.argv[2]
    Smt2Data.convert_smt2_file(filename, inst_str)



