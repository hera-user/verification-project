import pickle
from utils import parse_inst

from z3 import *
import networkx as nx
import matplotlib.pyplot as plt

COUNTER = 0
id_list = list()
class GraphBuilder:
    @staticmethod
    def safe_label_and_type(expr):
        label = str(expr)
        type_var = "var"
        if is_const(expr):
            type_var = "const"
        elif is_quantifier(expr):
            label =  "forall" if expr.is_forall() else "exists"
            type_var = "quantifier"
        elif is_app(expr):
            label = expr.decl().name()
            type_var = "op"
        return label, type_var

    @staticmethod
    def build_z3_graph(expr, G=None, parent=None, var_list=None):
        if var_list is None:
            var_list = list()
        global COUNTER
        COUNTER += 1
        if G is None:
            G = nx.DiGraph()
        label, type = GraphBuilder.safe_label_and_type(expr)
        node_id =  label
        if type not in ['var', 'const']:
           node_id += f"_{COUNTER}"
        else:
            if 'Var(' in label:
                label = var_list[int(label.replace('Var(', '').replace(')', ''))]
                node_id = label
    
        if node_id not in G:
    
            G.add_node(node_id, label=label, type=type)
    
        if parent is not None:
            G.add_edge(parent, node_id)
    
        if is_app(expr):
            for child in expr.children():
                GraphBuilder.build_z3_graph(child, G, node_id, var_list)
        elif is_quantifier(expr):
            current_var_names = [expr.var_name(i) for i in range(expr.num_vars())][::-1]
            new_var_names_list = current_var_names + var_list.copy()
            [GraphBuilder.build_z3_graph(Const(expr.var_name(i),expr.var_sort(i)), G, node_id) for i in range(expr.num_vars())]
            body = expr.body()
            GraphBuilder.build_z3_graph(body, G, node_id, new_var_names_list)
    
        return G

    @staticmethod
    def construct(smt_filename, inst_str):
        # Load SMT2 file1
        fmls = parse_smt2_file(smt_filename)
        # Z3 returns a list of assertions
        goal = Goal()
        for fml in fmls:
            goal.add(fml)
    
        # Apply Skolemization via the nnf tactic
        t = Tactic('nnf')
        result = t(goal)

        subst_map = parse_inst(inst_str)
        G = nx.DiGraph()
        for f in result:
            G = GraphBuilder.build_z3_graph(f.as_expr(), G)
            for var_name, value_list in subst_map.items():
                for value in value_list:
                    G.add_edge(var_name, value)
        return G

