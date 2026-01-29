from typing import Callable
from functools import reduce

from wfomc.cell_graph import build_cell_graphs
from wfomc.context.wfomc_context import WFOMCContext
from wfomc.utils import RingElement, Rational
from wfomc.fol.syntax import Const, Pred, QFFormula, AtomicFormula, a, b
from enum import Enum
import math

def incremental_multiple_orders_wfomc(context: WFOMCContext, t) -> RingElement:
    if context.predecessor_preds is None:
        return incremental_multiple_orders_wfomc_old(context, t)
    else:
        return _incremental_wfomc_with_predecessor_and_successor(context)

def _incremental_wfomc_with_predecessor(context: WFOMCContext):
    formula = context.formula
    domain = context.domain
    get_weight = context.get_weight
    leq_pred = context.leq_pred
    predecessor_preds = context.predecessor_preds

    evidence = dict()
    evidence["with PRED"] = frozenset((
        AtomicFormula(predecessor_preds[1], (b, a), True),
        AtomicFormula(predecessor_preds[1], (a, b), False),
    ))
    evidence["without PRED"] = frozenset((
        AtomicFormula(predecessor_preds[1], (b, a), False),
        AtomicFormula(predecessor_preds[1], (b, a), False),
    ))
    
    res = Rational(0, 1)
    domain_size = len(domain)
    for cell_graph, weight in build_cell_graphs(
        formula, get_weight,
        leq_pred=leq_pred,
        predecessor_preds=predecessor_preds,
        domain_size=domain_size
    ):
        #cell_graph.show()
        cells = cell_graph.get_cells()
        n_cells = len(cells)
        domain_size = len(domain)

        table = dict(
            (
                (
                    tuple(int(k == i) for k in range(n_cells)),
                    cell
                ),
                cell_graph.get_cell_weight(cell),
            )
            for i, cell in enumerate(cells)
        )

        for _ in range(domain_size - 1):
            old_table = table
            table = dict()
            for j, cell in enumerate(cells):
                w = cell_graph.get_cell_weight(cell)
                for key, w_old in old_table.items():
                    
                    ivec, last_cell = key
                    w_new = w_old * w
                    for k, other_cell in enumerate(cells):
                        if other_cell == last_cell:
                            w_new = (
                                w_new * cell_graph.get_two_table_with_pred_weight((cell, other_cell), index=1,  evidences=evidence["with PRED"])
                                * cell_graph.get_two_table_weight((cell, other_cell), evidences=evidence["without PRED"]) ** max(ivec[k] - 1, 0)
                            )
                        else:
                            w_new = w_new * cell_graph.get_two_table_weight((cell, other_cell), evidences=evidence["without PRED"]) ** ivec[k]
                    ivec = list(ivec)
                    ivec[j] += 1
                    ivec = tuple(ivec)
                    w_new = w_new + table.get((ivec, cell), Rational(0, 1))
                    table[(tuple(ivec), cell)] = w_new

            print(table)
        res = res + weight * sum(table.values())

    return res

def _incremental_wfomc_with_predecessor_and_successor(context: WFOMCContext):
    formula = context.formula
    domain = context.domain
    get_weight = context.get_weight
    leq_pred = context.leq_pred
    predecessor_preds = context.predecessor_preds
    successor_pred = context.successor_pred

    #All possible evidence - 
    # SUC(a, b), SUC(b, a), ~SUC, LEQ(b, a), PRED(b, a), ~PRED(b, a)
    # 1          0          0     1          1           0
    # 1          0          0     1          0           1
    # 0          1          0     1          1           0
    # 0          1          0     1          0           1
    # 0          0          1     1          1           0
    # 0          0          1     1          0           1

    #remember last string -> keeps info about last predicate

    #make that into a new file

    evidence = dict()
    evidence["SUC type 1"] = frozenset((
        AtomicFormula(successor_pred, (a, b), False),
        AtomicFormula(successor_pred, (b, a), False),
    ))
    
    evidence["SUC type 2"] = frozenset((
        AtomicFormula(successor_pred, (a, b), False),
        AtomicFormula(successor_pred, (b, a), True),
    ))
    evidence["SUC type 3"] = frozenset((
        AtomicFormula(successor_pred, (a, b), True),
        AtomicFormula(successor_pred, (b, a), False),
    ))

    class pred_pos(Enum):
        LEFT = 1
        MIDDLE = 2
        RIGHT = 3
        SINGLE = 4
    
    res = Rational(0, 1)
    domain_size = len(domain)
    for cell_graph, weight in build_cell_graphs(
        formula, get_weight,
        leq_pred=leq_pred,
        predecessor_preds=predecessor_preds,
        successor_pred=successor_pred,
        domain_size=domain_size
    ):
        #cell_graph.show()
        cells = cell_graph.get_cells()
        n_cells = len(cells)
        domain_size = len(domain)

        def only(h_old, sigma, rho_single, rho, cell, m, pred):
            out = []
            W_cell = cell_graph.get_cell_weight(cell)
            pred_type, pred_segment, pred_cell = pred

            lambda_ = math.prod(cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
                        if cell_s != pred else \
                        cell_graph.get_two_table_with_pred_weight((cell, cell_s), index = 1, evidences=evidence["SUC type 1"]) * \
                        cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** (sigma[e] - 1) \
                        for e, cell_s in enumerate(cells))
            
            #lambda_ = math.prod(cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
            #            for e, cell_s in enumerate(cells))
            new_rho_single = list(rho_single)
            new_rho_single[m] += 1
            new_sigma = list(sigma)
            new_sigma[m] += 1
            new_pred = (pred_pos.SINGLE, m, cell)
            new_key = (tuple(new_sigma), tuple(new_rho_single), rho, new_pred)
            if (h_old * W_cell * lambda_ != 0):
                out.append((new_key, h_old * W_cell * lambda_))
            return out

        def tail(h_old, sigma, rho_single, rho, cell, m, pred):
            out = []
            pred_type, pred_segment, pred_cell = pred
            W_cell = cell_graph.get_cell_weight(cell)

            for i, cell_i in enumerate(cells):
                for j, cell_j in enumerate(cells):
                    lambda_eta = 0
                    if rho[i * n_cells + j] > 0 and pred_type == pred_pos.RIGHT and pred_segment == (i, j):
                        lambda_eta = (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred_cell), index = 1, evidences=evidence["SUC type 3"]) * \
                            math.prod(1 if e == j else cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
                            for e, cell_s in enumerate(cells)) \
                             + \
                            (rho[i * n_cells + j] - 1) * \
                            cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                            (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred_cell), index = 1, evidences=evidence["SUC type 1"]) * \
                            math.prod(1 if e == j else cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
                            for e, cell_s in enumerate(cells))
                    elif rho[i * n_cells + j] > 0 and pred_cell == cell_j:
                        lambda_eta = rho[i * n_cells + j] * \
                            cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                            (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred_cell), index = 1, evidences=evidence["SUC type 1"]) * \
                            math.prod(1 if e == j else cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
                            for e, cell_s in enumerate(cells))
                    elif rho[i * n_cells + j] > 0:
                        lambda_eta = rho[i * n_cells + j] * \
                            cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                            (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred_cell), index = 1, evidences=evidence["SUC type 1"]) * \
                            (cell_graph.get_two_table_weight((cell, pred_cell), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred_cell)] - 1)) * \
                            math.prod(1 if (e == j or cell_s == pred_cell) else \
                            (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                            for e, cell_s in enumerate(cells))

                    new_rho = list(rho)
                    new_rho[i * n_cells + j] -= 1
                    new_rho[i * n_cells + m] += 1
                    new_sigma = list(sigma)
                    new_sigma[m] += 1
                    new_pred = (pred_pos.RIGHT, (i, m), cell)
                    new_key = (tuple(new_sigma), rho_single, tuple(new_rho), new_pred) 
                    if h_old * W_cell * lambda_eta != 0: #Multiplying all by rho is bad !!!
                        out.append((new_key, h_old * W_cell * lambda_eta))

                    if i != j or rho_single[j] <= 0:
                        continue

                    if pred_type == pred_pos.SINGLE and pred_segment == j:
                        lambda_eta = (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred_cell), index = 1, evidences=evidence["SUC type 3"]) * \
                            math.prod(1 if e == j else cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
                            for e, cell_s in enumerate(cells)) \
                             + \
                            (rho_single[j] - 1) *  \
                            cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                            (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred_cell), index = 1, evidences=evidence["SUC type 1"]) * \
                            math.prod(1 if e == j else cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
                            for e, cell_s in enumerate(cells))
                    elif pred_cell == cell_j:
                        lambda_eta = (rho_single[j]) * \
                            cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                            (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred_cell), index = 1, evidences=evidence["SUC type 1"]) * \
                            math.prod(1 if (e == j) else \
                            (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                            for e, cell_s in enumerate(cells))
                    else:
                        lambda_eta = (rho_single[j]) * \
                            cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                            (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred_cell), index = 1, evidences=evidence["SUC type 1"]) * \
                            cell_graph.get_two_table_weight((cell, pred), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred_cell)] - 1) * \
                            math.prod(1 if (e == j or cell_s == pred) else \
                            (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                            for e, cell_s in enumerate(cells))
                    new_rho_single = list(rho_single)
                    new_rho_single[j] -= 1
                    new_rho = list(rho)
                    new_rho[j * n_cells + m] += 1
                    new_sigma = list(sigma)
                    new_sigma[m] += 1
                    new_pred = (pred_pos.RIGHT, (j, m), cell)
                    new_key = (tuple(new_sigma), tuple(new_rho_single), tuple(new_rho), new_pred) 
                    if h_old * W_cell * lambda_eta != 0: #Multiplying all by rho is bad !!!
                        out.append((new_key, h_old * W_cell * lambda_eta))
            return out
        
        def head(h_old, sigma, rho_single, rho, cell, m, pred):
            out = []
            pred_type, pred_segment, pred_cell = pred
            W_cell = cell_graph.get_cell_weight(cell)

            for i, cell_i in enumerate(cells):
                for j, cell_j in enumerate(cells):
                    lambda_eta = 0
                    if rho[i * n_cells + j] > 0 and pred_type == pred_pos.LEFT and pred_segment == (i, j):
                        lambda_eta = (cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 1"]) ** (sigma[i] - 1)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred_cell), index = 1, evidences=evidence["SUC type 2"]) * \
                            math.prod(1 if e == i else cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
                            for e, cell_s in enumerate(cells)) \
                             + \
                            (rho[i * n_cells + j] - 1) * \
                            cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 2"]) * \
                            (cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred_cell), index = 1, evidences=evidence["SUC type 1"]) * \
                            math.prod(1 if e == i else cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
                            for e, cell_s in enumerate(cells))
                    elif rho[i * n_cells + j] > 0 and pred_cell == cell_i:
                        lambda_eta = rho[i * n_cells + j] * \
                            cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 2"]) * \
                            (cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred_cell), index = 1, evidences=evidence["SUC type 1"]) * \
                            math.prod(1 if e == i else cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
                            for e, cell_s in enumerate(cells))
                    elif rho[i * n_cells + j] > 0:
                        lambda_eta = rho[i * n_cells + j] * \
                            cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 2"]) * \
                            (cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred_cell), index = 1, evidences=evidence["SUC type 1"]) * \
                            (cell_graph.get_two_table_weight((cell, pred_cell), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred_cell)] - 1)) * \
                            math.prod(1 if (e == i or cell_s == pred_cell) else \
                            (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                            for e, cell_s in enumerate(cells))

                    new_rho = list(rho)
                    new_rho[i * n_cells + j] -= 1
                    new_rho[m * n_cells + j] += 1
                    new_sigma = list(sigma)
                    new_sigma[m] += 1
                    new_pred = (pred_pos.LEFT, (m, j), cell)
                    new_key = (tuple(new_sigma), rho_single, tuple(new_rho), new_pred) 
                    if h_old * W_cell * lambda_eta != 0: #Multiplying all by rho is bad !!!
                        out.append((new_key, h_old * W_cell * lambda_eta))

                    if i != j or rho_single[i] <= 0:
                        continue

                    if pred_type == pred_pos.SINGLE and pred_segment == i:
                        lambda_eta = (cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 1"]) ** (sigma[i] - 1)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred_cell), index = 1, evidences=evidence["SUC type 2"]) * \
                            math.prod(1 if e == i else cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
                            for e, cell_s in enumerate(cells)) \
                             + \
                            (rho_single[i] - 1) *  \
                            cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 2"]) * \
                            (cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 1"]) ** (sigma[i] - 2)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred_cell), index = 1, evidences=evidence["SUC type 1"]) * \
                            math.prod(1 if e == i else cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
                            for e, cell_s in enumerate(cells))
                    elif pred_cell == cell_i:
                        lambda_eta = (rho_single[i]) * \
                            cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 2"]) * \
                            (cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 1"]) ** (sigma[i] - 2)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred_cell), index = 1, evidences=evidence["SUC type 1"]) * \
                            math.prod(1 if (e == i) else \
                            (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                            for e, cell_s in enumerate(cells))
                    else:
                        lambda_eta = (rho_single[i]) * \
                            cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 2"]) * \
                            (cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 1"]) ** (sigma[i] - 1)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred_cell), index = 1, evidences=evidence["SUC type 1"]) * \
                            cell_graph.get_two_table_weight((cell, pred), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred_cell)] - 1) * \
                            math.prod(1 if (e == i or cell_s == pred) else \
                            (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                            for e, cell_s in enumerate(cells))
                    new_rho_single = list(rho_single)
                    new_rho_single[i] -= 1
                    new_rho = list(rho)
                    new_rho[m * n_cells + i] += 1
                    new_sigma = list(sigma)
                    new_sigma[m] += 1
                    new_pred = (pred_pos.LEFT, (m, j), cell)
                    new_key = (tuple(new_sigma), tuple(new_rho_single), tuple(new_rho), new_pred) 
                    if h_old * W_cell * lambda_eta != 0: #Multiplying all by rho is bad !!!
                        out.append((new_key, h_old * W_cell * lambda_eta))
            return out
        
        def merge(h_old, sigma, rho_single, rho, cell, m, pred): #will only run for two same cell segments for now
            out = []
            pred_type, pred_segment, pred_cell = pred
            W_cell = cell_graph.get_cell_weight(cell)

            lambda_eta = 0

            for i, cell_i in enumerate(cells):
                for j, cell_j in enumerate(cells):
                    #if rho[i * n_cells + j] <= 0:
                    #    continue
                    for c, cell_c in enumerate(cells):
                        #merge to as if connecting a -'-,-> b to b-'-,-> c
                        #merge2
                        #----------------------------------------------------------------
                        
                        if rho[i * n_cells + j] > 0 and rho[j * n_cells + c] > 0:
                            if pred_type == pred_pos.RIGHT and pred_segment == (i, j):
                                lambda_eta = ((rho[j * n_cells + c]) if (i != j or j != c) else (rho[j * n_cells + c] - 1)) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    math.prod(1 if (e == j) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                                if rho[i * n_cells + j] > 1:
                                    lambda_eta = lambda_eta + \
                                        (((rho[i * n_cells + j] - 1) * rho[j * n_cells + c]) if (i != j or j != c) else ((rho[i * n_cells + j] - 1) * (rho[j * n_cells + c] - 1))) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                        cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 1"]) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 3)) * \
                                        math.prod(1 if (e == j) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells))
                            elif pred_type == pred_pos.LEFT and pred_segment == (j, c):
                                lambda_eta = (rho[i * n_cells + j] if i != j or j != c else rho[i * n_cells + j] - 1) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    math.prod(1 if (e == j) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                                if rho[j * n_cells + c] > 1:
                                    lambda_eta = lambda_eta + \
                                        (((rho[j * n_cells + c] - 1) * rho[i * n_cells + j]) if (i != j or j != c) else ((rho[i * n_cells + j] - 1) * (rho[j * n_cells + c] - 1))) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                        cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 1"]) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 3)) * \
                                        math.prod(1 if (e == j) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells))
                            elif pred_cell == cell_j:
                                lambda_eta = (((rho[i * n_cells + j]) * rho[j * n_cells + c])   \
                                    if i != j or j != c else \
                                    ((rho[i * n_cells + j]) * (rho[i * n_cells + j] - 1))) \
                                     * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 1"])) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 3)) * \
                                    math.prod(1 if (e == j) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                            else:
                                lambda_eta = (((rho[i * n_cells + j]) * rho[j * n_cells + c])   \
                                    if i != j or j != c else \
                                    ((rho[i * n_cells + j]) * (rho[i * n_cells + j] - 1))) \
                                     * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    cell_graph.get_two_table_weight((cell, pred_cell), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred_cell)] - 1) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, pred_cell), index = 1, evidences=evidence["SUC type 1"]) * \
                                    math.prod(1 if (e == j or cell_s == pred_cell) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                            
                                
                            new_rho = list(rho)
                            new_rho[i * n_cells + j] -= 1
                            new_rho[j * n_cells + c] -= 1
                            new_rho[i * n_cells + c] += 1
                            new_sigma = list(sigma)
                            new_sigma[m] += 1
                            new_pred = (pred_pos.MIDDLE, (i, c), cell)
                            new_key = (tuple(new_sigma), rho_single, tuple(new_rho), new_pred)
                            if h_old * W_cell * lambda_eta != 0:
                                out.append((new_key, h_old * W_cell * lambda_eta))

                        if i == j and rho_single[j] > 0 and rho[j * n_cells + c] > 0:
                            if pred_type == pred_pos.SINGLE and pred_segment == j:
                                lambda_eta = (rho[j * n_cells + c]) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    math.prod(1 if (e == j) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                                if rho_single[j] > (1):
                                    lambda_eta = lambda_eta + \
                                        (((rho_single[j] - 1) * rho[j * n_cells + c])) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                        cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 1"]) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 3)) * \
                                        math.prod(1 if (e == j) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells))
                            elif pred_type == pred_pos.LEFT and pred_segment == (j, c):
                                lambda_eta = (rho_single[j]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    math.prod(1 if (e == j) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                                if rho[j * n_cells + c] > 1:
                                    lambda_eta = lambda_eta + \
                                        (((rho[j * n_cells + c] - 1) * rho_single[j])) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                        cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 1"]) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 3)) * \
                                        math.prod(1 if (e == j) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells))
                            elif pred_cell == cell_j:
                                lambda_eta = ((rho_single[j]) * rho[j * n_cells + c]) \
                                     * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 1"])) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 3)) * \
                                    math.prod(1 if (e == j) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                            else:
                                lambda_eta = rho_single[j] * rho[j * n_cells + c] *\
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    cell_graph.get_two_table_weight((cell, pred_cell), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred_cell)] - 1) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, pred_cell), index = 1, evidences=evidence["SUC type 1"]) * \
                                    math.prod(1 if (e == j or cell_s == pred_cell) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                                
                            new_rho = list(rho)
                            new_rho_single = list(rho_single)
                            new_rho_single[j] -= 1
                            new_rho[j * n_cells + c] -= 1
                            new_rho[i * n_cells + c] += 1
                            new_sigma = list(sigma)
                            new_sigma[m] += 1
                            new_pred = (pred_pos.MIDDLE, (i, c), cell)
                            new_key = (tuple(new_sigma), tuple(new_rho_single), tuple(new_rho), new_pred)
                            if h_old * W_cell * lambda_eta != 0:
                                out.append((new_key, h_old * W_cell * lambda_eta))
                        
                        if c == j and rho_single[j] > 0 and rho[i * n_cells + j] > 0:
                            if pred_type == pred_pos.SINGLE and pred_segment == j:
                                lambda_eta = (rho[i * n_cells + j]) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 2"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    math.prod(1 if (e == j) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                                if rho_single[j] > 1:
                                    lambda_eta = lambda_eta + \
                                        (((rho_single[j] - 1) * rho[i * n_cells + j])) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                        cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 1"]) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 3)) * \
                                        math.prod(1 if (e == j) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells))
                            elif pred_type == pred_pos.RIGHT and pred_segment == (i, j):
                                lambda_eta = (rho_single[j]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 3"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    math.prod(1 if (e == j) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                                if rho[i * n_cells + j] > 1:
                                    lambda_eta = lambda_eta + \
                                        (((rho[i * n_cells + j] - 1) * rho_single[j])) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                        cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 1"]) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 3)) * \
                                        math.prod(1 if (e == j) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells))
                            elif pred_cell == cell_j:
                                lambda_eta = ((rho_single[j]) * rho[i * n_cells + j]) \
                                     * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 1"])) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 3)) * \
                                    math.prod(1 if (e == j) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                            else:
                                lambda_eta = rho_single[j] * rho[i * n_cells + j] *\
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    cell_graph.get_two_table_weight((cell, pred_cell), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred_cell)] - 1) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, pred_cell), index = 1, evidences=evidence["SUC type 1"]) * \
                                    math.prod(1 if (e == j or cell_s == pred_cell) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                                
                            new_rho = list(rho)
                            new_rho_single = list(rho_single)
                            new_rho_single[j] -= 1
                            new_rho[i * n_cells + j] -= 1
                            new_rho[i * n_cells + c] += 1
                            new_sigma = list(sigma)
                            new_sigma[m] += 1
                            new_pred = (pred_pos.MIDDLE, (i, c), cell)
                            new_key = (tuple(new_sigma), tuple(new_rho_single), tuple(new_rho), new_pred)
                            if h_old * W_cell * lambda_eta != 0:
                                out.append((new_key, h_old * W_cell * lambda_eta))

                        if i == j and j == c and rho_single[j] > 1:
                            if pred_type == pred_pos.SINGLE and pred_segment == j:
                                lambda_eta = (rho_single[j] - 1) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    math.prod(1 if (e == j) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells)) \
                                     + \
                                    (rho_single[j] - 1) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 2"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    math.prod(1 if (e == j) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                                if rho_single[j] > 2:
                                    lambda_eta = lambda_eta + \
                                        (((rho_single[j] - 1) * (rho_single[j] - 2))) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                        cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 1"]) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 3)) * \
                                        math.prod(1 if (e == j) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells))
                            elif pred_cell == cell_j:
                                    lambda_eta = ((rho_single[j]) * (rho_single[j] - 1)) \
                                     * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 1"])) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 3)) * \
                                    math.prod(1 if (e == j) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                            else:
                                lambda_eta = ((rho_single[j]) * (rho_single[j] - 1)) *\
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    cell_graph.get_two_table_weight((cell, pred_cell), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred_cell)] - 1) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, pred_cell), index = 1, evidences=evidence["SUC type 1"]) * \
                                    math.prod(1 if (e == j or cell_s == pred_cell) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                                
                            new_rho = list(rho)
                            new_rho_single = list(rho_single)
                            new_rho_single[j] -= 2
                            new_rho[i * n_cells + c] += 1
                            new_sigma = list(sigma)
                            new_sigma[m] += 1
                            new_pred = (pred_pos.MIDDLE, (i, c), cell)
                            new_key = (tuple(new_sigma), tuple(new_rho_single), tuple(new_rho), new_pred)
                            if h_old * W_cell * lambda_eta != 0:
                                out.append((new_key, h_old * W_cell * lambda_eta))
                        #----------------------------------------------------------------
                        if j == c:
                            continue
                        for d, cell_d in enumerate(cells):
                            if rho[c * n_cells + d] <= (0 if i != c or j != d else 1):
                                continue
                            #merge1
                            eta = Rational(rho[i * n_cells + j] * rho[c * n_cells + d], 1) \
                                if i != c or j != d else \
                                Rational(rho[i * n_cells + j] * (rho[i * n_cells + j] - 1), 1)
                            W_cell = cell_graph.get_cell_weight(cell)
                            if cell_j == pred:
                                lambda_eta = (rho[c * n_cells + d] if i != c or j != d else rho[c * n_cells + d] - 1) * \
                                cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 3"]) * \
                                cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 2"]) * \
                                (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                                (cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 1"]) ** (sigma[c] - 1)) * \
                                math.prod(1 if (e == j or e == c) else \
                                (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                for e, cell_s in enumerate(cells))
                                if sigma[j] >= 2:
                                    lambda_eta = lambda_eta + \
                                    (Rational((rho[i * n_cells + j] - 1) * rho[c * n_cells + d], 1) \
                                    if i != c or j != d else \
                                    Rational((rho[i * n_cells + j] - 1) * (rho[i * n_cells + j] - 1), 1)) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    (cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 1"]) ** (sigma[c] - 1)) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1,  evidences=evidence["SUC type 1"])* \
                                    math.prod(1 if (e == j or e == c) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                            elif cell_c == pred:
                                lambda_eta = (rho[i * n_cells + j] if i != c or j != d else rho[i * n_cells + j] - 1) * \
                                cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                cell_graph.get_two_table_with_pred_weight((cell, cell_c), index = 1, evidences=evidence["SUC type 2"]) * \
                                (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                                (cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 1"]) ** (sigma[c] - 1)) * \
                                math.prod(1 if (e == j or e == c) else \
                                (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e]) \
                                for e, cell_s in enumerate(cells))
                                if sigma[c] >= 2:
                                    lambda_eta = lambda_eta + \
                                    (Rational((rho[i * n_cells + j]) * (rho[c * n_cells + d] - 1), 1) \
                                    if i != c or j != d else \
                                    Rational((rho[i * n_cells + j]) * (rho[i * n_cells + j] - 2), 1)) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                                    (cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 1"]) ** (sigma[c] - 2)) * \
                                    (cell_graph.get_two_table_with_pred_weight((cell, cell_c), index = 1, evidences=evidence["SUC type 1"])) * \
                                    math.prod(1 if (e == j or e == c) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e]) \
                                    for e, cell_s in enumerate(cells))
                            else:
                                lambda_eta = eta * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                                    (cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 1"]) ** (sigma[c] - 1)) * \
                                    cell_graph.get_two_table_weight((cell, pred), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred)] - 1) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 1"]) * \
                                    math.prod(1 if (e == j or e == c or cell_s == pred) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                            new_rho = list(rho)
                            new_rho[i * n_cells + j] -= 1
                            new_rho[c * n_cells + d] -= 1
                            new_rho[i * n_cells + d] += 1
                            new_sigma = list(sigma)
                            new_sigma[m] += 1
                            new_key = (tuple(new_sigma), tuple(new_rho), cell)
                            if h_old * W_cell * lambda_eta != 0:
                                out.append((new_key, h_old * W_cell * lambda_eta))
            return out

        table = dict(
            (
                (
                    tuple(int(k == i) for k in range(n_cells)), #count of cells
                    tuple(int(k == i) for k in range(n_cells)), #count of single cell segments
                    tuple(0 for _ in range(n_cells**2)), #count of multi cell segments
                    (pred_pos.SINGLE, i, cell), #where the pred is
                ),
                cell_graph.get_cell_weight(cell),
            )
            for i, cell in enumerate(cells)
        )



        for i in range(1, domain_size):
            old_table = table
            table = dict()
            if i >= (domain_size + 1) // 2:
                max_rho_size = domain_size - i
            else:
                max_rho_size = domain_size
            for j, cell in enumerate(cells):
                for key, h_old in old_table.items():
                    sigma, rho_single, rho, pred = key
                    rho_size = sum(list(rho)) + sum(list(rho_single))
                    if rho_size > 1:
                    #if merge is possible, add merges
                        h_news = merge(h_old, sigma, rho_single, rho, cell, j, pred)
                        #print("merge:", h_news)
                        for new_key, h_new in h_news:
                            table[new_key] = table.get(new_key, Rational(0, 1)) + h_new
                    
                    if rho_size <= max_rho_size:
                    #if |rho_old| = |rho_new| is possible, do head and tail
                        h_news = tail(h_old, sigma, rho_single, rho, cell, j, pred)
                        #print("tail:", h_news)
                        for new_key, h_new in h_news:
                            table[new_key] = table.get(new_key, Rational(0, 1)) + h_new
                        h_news = head(h_old, sigma, rho_single, rho, cell, j, pred)
                        #print("head:",  h_news)
                        for new_key, h_new in h_news:
                            table[new_key] = table.get(new_key, Rational(0, 1)) + h_new

                    if rho_size < max_rho_size:
                    #if |rho_old| + 1 = |rho_new| is posible, do only
                    #e. g. at no time we need h(m, sigma, rho)
                    #where |rho| > domain_size - m + 1
                        h_news = only(h_old, sigma, rho_single, rho, cell, j, pred)
                        #print("only:", h_news)
                        for new_key, h_new in h_news:
                            table[new_key] = table.get(new_key, Rational(0, 1)) + h_new

            #print(table)
        res = res + weight * sum(table.values())
    return res


def _incremental_wfomc_with_predecessor_and_successor_old(context: WFOMCContext):
    formula = context.formula
    domain = context.domain
    get_weight = context.get_weight
    leq_pred = context.leq_pred
    predecessor_preds = context.predecessor_preds
    successor_pred = context.successor_pred

    #All possible evidence - 
    # SUC(a, b), SUC(b, a), ~SUC, LEQ(b, a), PRED(b, a), ~PRED(b, a)
    # 1          0          0     1          1           0
    # 1          0          0     1          0           1
    # 0          1          0     1          1           0
    # 0          1          0     1          0           1
    # 0          0          1     1          1           0
    # 0          0          1     1          0           1

    #remember last string -> keeps info about last predicate

    #make that into a new file

    evidence = dict()
    evidence["SUC type 1"] = frozenset((
        AtomicFormula(successor_pred, (a, b), False),
        AtomicFormula(successor_pred, (b, a), False),
    ))
    
    evidence["SUC type 2"] = frozenset((
        AtomicFormula(successor_pred, (a, b), False),
        AtomicFormula(successor_pred, (b, a), True),
    ))
    evidence["SUC type 3"] = frozenset((
        AtomicFormula(successor_pred, (a, b), True),
        AtomicFormula(successor_pred, (b, a), False),
    ))
    
    res = Rational(0, 1)
    domain_size = len(domain)
    for cell_graph, weight in build_cell_graphs(
        formula, get_weight,
        leq_pred=leq_pred,
        predecessor_preds=predecessor_preds,
        successor_pred=successor_pred,
        domain_size=domain_size
    ):
        #cell_graph.show()
        cells = cell_graph.get_cells()
        n_cells = len(cells)
        domain_size = len(domain)

        table = dict(
            (
                (
                    tuple(int(k == i) for k in range(n_cells)), #count of cells
                    tuple(int(k == i) for k in range(n_cells)), #count of single cell segments
                    tuple(0 for _ in range(n_cells**2)), #count of multi cell segments
                    cell
                ),
                cell_graph.get_cell_weight(cell),
            )
            for i, cell in enumerate(cells)
        )

        def merge_2(h_old, sigma, rho_single, rho, cell, m, pred):
            out = []
            for i, cell_i in enumerate(cells):
                for j, cell_j in enumerate(cells):
                    if rho[i * n_cells + j] <= 0:
                        continue
                    for c, cell_c in enumerate(cells):
                        #merge to as if connecting a -'-,-> b to b-'-,-> c
                        #merge2
                        #----------------------------------------------------------------
                        if rho[j * n_cells + c] > (0 if i != j or j != c else 1):
                            eta = Rational(rho[i * n_cells + j] * rho[j * n_cells + c], 1) \
                                if i != j or j != c else \
                                Rational(rho[i * n_cells + j] * (rho[i * n_cells + j] - 1), 1)
                            W_cell = cell_graph.get_cell_weight(cell)
                            

                            if cell_j == pred:
                                lambda_eta = (rho[j * n_cells + c] if i != j or j != c else rho[j * n_cells + c] - 1) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    math.prod(1 if (e == j) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells)) + \
                                    (rho[i * n_cells + j] if i != j or j != c else rho[i * n_cells + j] - 1) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    math.prod(1 if (e == j) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                                if sigma[j] >= 3:
                                    lambda_eta = lambda_eta + \
                                    ((((rho[i * n_cells + j] - 1) * rho[j * n_cells + c])   \
                                    if i != j or j != c else \
                                    ((rho[i * n_cells + j] - 1) * (rho[i * n_cells + j] - 1))) +  \
                                    (((rho[i * n_cells + j]) * (rho[j * n_cells + c] - 1))   \
                                    if i != j or j != c else \
                                    ((rho[i * n_cells + j]) * (rho[i * n_cells + j] - 2))) + \
                                    (eta if sigma[j] > rho[i * n_cells + j] + rho[j * n_cells + c] else 0)) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 1"])) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 3)) * \
                                    math.prod(1 if (e == j) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                            elif cell_j != pred:
                                lambda_eta = eta *\
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    cell_graph.get_two_table_weight((cell, pred), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred)] - 1) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 1"]) * \
                                    math.prod(1 if (e == j or cell_s == pred) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                            
                                
                            new_rho = list(rho)
                            new_rho[i * n_cells + j] -= 1
                            new_rho[j * n_cells + c] -= 1
                            new_rho[i * n_cells + c] += 1
                            new_sigma = list(sigma)
                            new_sigma[m] += 1
                            new_key = (tuple(new_sigma), rho_single, tuple(new_rho), cell)
                            if h_old * W_cell * lambda_eta != 0:
                                out.append((new_key, h_old * W_cell * lambda_eta))
                        #----------------------------------------------------------------
                        if j == c:
                            continue
                        for d, cell_d in enumerate(cells):
                            if rho[c * n_cells + d] <= (0 if i != c or j != d else 1):
                                continue
                            #merge1
                            eta = Rational(rho[i * n_cells + j] * rho[c * n_cells + d], 1) \
                                if i != c or j != d else \
                                Rational(rho[i * n_cells + j] * (rho[i * n_cells + j] - 1), 1)
                            W_cell = cell_graph.get_cell_weight(cell)
                            if cell_j == pred:
                                lambda_eta = (rho[c * n_cells + d] if i != c or j != d else rho[c * n_cells + d] - 1) * \
                                cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 3"]) * \
                                cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 2"]) * \
                                (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                                (cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 1"]) ** (sigma[c] - 1)) * \
                                math.prod(1 if (e == j or e == c) else \
                                (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                for e, cell_s in enumerate(cells))
                                if sigma[j] >= 2:
                                    lambda_eta = lambda_eta + \
                                    (Rational((rho[i * n_cells + j] - 1) * rho[c * n_cells + d], 1) \
                                    if i != c or j != d else \
                                    Rational((rho[i * n_cells + j] - 1) * (rho[i * n_cells + j] - 1), 1)) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    (cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 1"]) ** (sigma[c] - 1)) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1,  evidences=evidence["SUC type 1"])* \
                                    math.prod(1 if (e == j or e == c) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                            elif cell_c == pred:
                                lambda_eta = (rho[i * n_cells + j] if i != c or j != d else rho[i * n_cells + j] - 1) * \
                                cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                cell_graph.get_two_table_with_pred_weight((cell, cell_c), index = 1, evidences=evidence["SUC type 2"]) * \
                                (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                                (cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 1"]) ** (sigma[c] - 1)) * \
                                math.prod(1 if (e == j or e == c) else \
                                (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e]) \
                                for e, cell_s in enumerate(cells))
                                if sigma[c] >= 2:
                                    lambda_eta = lambda_eta + \
                                    (Rational((rho[i * n_cells + j]) * (rho[c * n_cells + d] - 1), 1) \
                                    if i != c or j != d else \
                                    Rational((rho[i * n_cells + j]) * (rho[i * n_cells + j] - 2), 1)) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                                    (cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 1"]) ** (sigma[c] - 2)) * \
                                    (cell_graph.get_two_table_with_pred_weight((cell, cell_c), index = 1, evidences=evidence["SUC type 1"])) * \
                                    math.prod(1 if (e == j or e == c) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e]) \
                                    for e, cell_s in enumerate(cells))
                            else:
                                lambda_eta = eta * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                                    (cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 1"]) ** (sigma[c] - 1)) * \
                                    cell_graph.get_two_table_weight((cell, pred), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred)] - 1) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 1"]) * \
                                    math.prod(1 if (e == j or e == c or cell_s == pred) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                            new_rho = list(rho)
                            new_rho[i * n_cells + j] -= 1
                            new_rho[c * n_cells + d] -= 1
                            new_rho[i * n_cells + d] += 1
                            new_sigma = list(sigma)
                            new_sigma[m] += 1
                            new_key = (tuple(new_sigma), rho_single, tuple(new_rho), cell)
                            if h_old * W_cell * lambda_eta != 0:
                                out.append((new_key, h_old * W_cell * lambda_eta))
            for i, cell_i in enumerate(cells):
                for j, cell_j in enumerate(cells):
                    for c, cell_c in enumerate(cells):
                        if i == j and j != c:
                            #merge to as if connecting a -'-,-> b to b-'-,-> c
                            #merge2
                            #----------------------------------------------------------------
                            if rho_single[j] > 0 and rho[j * n_cells + c] > 0:
                                eta = Rational(rho_single[j] * rho[j * n_cells + c], 1)
                                W_cell = cell_graph.get_cell_weight(cell)

                                if cell_j == pred:
                                    lambda_eta = rho[j * n_cells + c] * \
                                        cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                        math.prod(1 if (e == j) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells)) + \
                                        (rho_single[j]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 2"]) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                        math.prod(1 if (e == j) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells))
                                    if sigma[j] >= 3:
                                        lambda_eta = lambda_eta + \
                                        (((rho_single[j] - 1) * rho[j * n_cells + c])   \
                                         +  \
                                        ((rho_single[j]) * (rho[j * n_cells + c] - 1))   \
                                        + \
                                        (eta if sigma[j] > rho_single[j] + rho[j * n_cells + c] else 0)) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                        (cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 1"])) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 3)) * \
                                        math.prod(1 if (e == j) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells))
                                elif cell_j != pred:
                                    lambda_eta = eta *\
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                        cell_graph.get_two_table_weight((cell, pred), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred)] - 1) * \
                                        cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 1"]) * \
                                        math.prod(1 if (e == j or cell_s == pred) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells))
                                
                                    
                                new_rho = list(rho)
                                new_rho_single = list(rho_single)
                                new_rho_single[j] -= 1
                                new_rho[j * n_cells + c] -= 1
                                new_rho[i * n_cells + c] += 1
                                new_sigma = list(sigma)
                                new_sigma[m] += 1
                                new_key = (tuple(new_sigma), tuple(new_rho_single), tuple(new_rho), cell)
                                if h_old * W_cell * lambda_eta != 0:
                                    out.append((new_key, h_old * W_cell * lambda_eta))
                            #----------------------------------------------------------------
                        if i != j and j == c:
                            #merge to as if connecting a -'-,-> b to b-'-,-> c
                            #merge2
                            #----------------------------------------------------------------
                            if rho_single[j] > 0 and rho[i * n_cells + j] > 0:
                                eta = Rational(rho_single[j] * rho[i * n_cells + j], 1)
                                W_cell = cell_graph.get_cell_weight(cell)
                                

                                if cell_j == pred:
                                    lambda_eta = (rho_single[j]) * \
                                        cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                        math.prod(1 if (e == j) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells)) + \
                                        rho[i * n_cells + j] * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 2"]) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                        math.prod(1 if (e == j) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells))
                                    if sigma[j] >= 3:
                                        lambda_eta = lambda_eta + \
                                        (((rho[i * n_cells + j] - 1) * rho_single[j])   \
                                         +  \
                                        ((rho[i * n_cells + j]) * (rho_single[j] - 1))   \
                                         + \
                                        (eta if sigma[j] > rho[i * n_cells + j] + rho_single[j] else 0)) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                        (cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 1"])) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 3)) * \
                                        math.prod(1 if (e == j) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells))
                                elif cell_j != pred:
                                    lambda_eta = eta *\
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                        cell_graph.get_two_table_weight((cell, pred), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred)] - 1) * \
                                        cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 1"]) * \
                                        math.prod(1 if (e == j or cell_s == pred) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells))
                                
                                    
                                new_rho = list(rho)
                                new_rho_single = list(rho_single)
                                new_rho[i * n_cells + j] -= 1
                                new_rho_single[j] -= 1
                                new_rho[i * n_cells + c] += 1
                                new_sigma = list(sigma)
                                new_sigma[m] += 1
                                new_key = (tuple(new_sigma), list(new_rho_single), tuple(new_rho), cell)
                                if h_old * W_cell * lambda_eta != 0:
                                    out.append((new_key, h_old * W_cell * lambda_eta))
                            #----------------------------------------------------------------
                        if i == j and j == c:
                            #merge to as if connecting a -'-,-> b to b-'-,-> c
                            #merge2
                            #----------------------------------------------------------------
                            if rho_single[j] > 1:
                                eta = Rational(rho_single[j] * (rho_single[j] - 1), 1)
                                W_cell = cell_graph.get_cell_weight(cell)
                                

                                if cell_j == pred:
                                    lambda_eta = (rho_single[j] - 1) * \
                                        cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                        math.prod(1 if (e == j) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells)) + \
                                        (rho_single[j] - 1) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 2"]) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                        math.prod(1 if (e == j) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells))
                                    if sigma[j] >= 3:
                                        lambda_eta = lambda_eta + \
                                        (((rho_single[j] - 1) * (rho_single[j] - 2)) \
                                         +  \
                                        (eta if sigma[j] > rho_single[j] + rho_single[j] else 0)) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                        (cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 1"])) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 3)) * \
                                        math.prod(1 if (e == j) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells))
                                elif cell_j != pred:
                                    lambda_eta = eta *\
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                        cell_graph.get_two_table_weight((cell, pred), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred)] - 1) * \
                                        cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 1"]) * \
                                        math.prod(1 if (e == j or cell_s == pred) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells))
                                
                                    
                                new_rho = list(rho)
                                new_rho_single = list(rho_single)
                                new_rho_single[j] -= 2
                                new_rho[i * n_cells + c] += 1
                                new_sigma = list(sigma)
                                new_sigma[m] += 1
                                new_key = (tuple(new_sigma), tuple(new_rho_single), tuple(new_rho), cell)
                                if h_old * W_cell * lambda_eta != 0:
                                    out.append((new_key, h_old * W_cell * lambda_eta))
                            #----------------------------------------------------------------
                        if i == j and j == c:
                            #merge to as if connecting a -'-,-> b to b-'-,-> c
                            #merge2
                            #----------------------------------------------------------------
                            if rho_single[j] > 0 and rho[j * n_cells + j] > 0:
                                eta = 2 * Rational(rho_single[j] * rho[j * n_cells + c], 1)
                                W_cell = cell_graph.get_cell_weight(cell)
                                

                                if cell_j == pred:
                                    lambda_eta = (rho_single[j] + rho[j * n_cells + j]) * \
                                        cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                        math.prod(1 if (e == j) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells)) + \
                                        (rho_single[j] + rho[j * n_cells + j]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 2"]) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                        math.prod(1 if (e == j) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells))
                                    if sigma[j] >= 3:
                                        lambda_eta = lambda_eta + \
                                        (((rho_single[j] - 1) * rho[j * n_cells + c])   \
                                         +  \
                                        ((rho[i * n_cells + j]) * (rho_single[j]))   \
                                        + \
                                        (eta if sigma[j] > 2 * rho[i * n_cells + j] + rho_single[j] else 0)) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                        (cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 1"])) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 3)) * \
                                        math.prod(1 if (e == j) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells))
                                elif cell_j != pred:
                                    lambda_eta = eta *\
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                        cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                        (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                        cell_graph.get_two_table_weight((cell, pred), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred)] - 1) * \
                                        cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 1"]) * \
                                        math.prod(1 if (e == j or cell_s == pred) else \
                                        (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                        for e, cell_s in enumerate(cells))
                                
                                    
                                new_rho = list(rho)
                                new_rho_single = list(rho_single)
                                new_rho[i * n_cells + j] -= 1
                                new_rho_single[j] -= 1
                                new_rho[i * n_cells + c] += 1
                                new_sigma = list(sigma)
                                new_sigma[m] += 1
                                new_key = (tuple(new_sigma), tuple(new_rho_single), tuple(new_rho), cell)
                                if h_old * W_cell * lambda_eta != 0:
                                    out.append((new_key, h_old * W_cell * lambda_eta))
                            #----------------------------------------------------------------
                        if j == c:
                            continue
                        for d, cell_d in enumerate(cells):
                            if rho[c * n_cells + d] <= (0 if i != c or j != d else 1):
                                continue
                            #merge1
                            eta = Rational(rho[i * n_cells + j] * rho[c * n_cells + d], 1) \
                                if i != c or j != d else \
                                Rational(rho[i * n_cells + j] * (rho[i * n_cells + j] - 1), 1)
                            W_cell = cell_graph.get_cell_weight(cell)
                            if cell_j == pred:
                                lambda_eta = (rho[c * n_cells + d] if i != c or j != d else rho[c * n_cells + d] - 1) * \
                                cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 3"]) * \
                                cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 2"]) * \
                                (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                                (cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 1"]) ** (sigma[c] - 1)) * \
                                math.prod(1 if (e == j or e == c) else \
                                (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                for e, cell_s in enumerate(cells))
                                if sigma[j] >= 2:
                                    lambda_eta = lambda_eta + \
                                    (Rational((rho[i * n_cells + j] - 1) * rho[c * n_cells + d], 1) \
                                    if i != c or j != d else \
                                    Rational((rho[i * n_cells + j] - 1) * (rho[i * n_cells + j] - 1), 1)) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    (cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 1"]) ** (sigma[c] - 1)) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1,  evidences=evidence["SUC type 1"])* \
                                    math.prod(1 if (e == j or e == c) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                            elif cell_c == pred:
                                lambda_eta = (rho[i * n_cells + j] if i != c or j != d else rho[i * n_cells + j] - 1) * \
                                cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                cell_graph.get_two_table_with_pred_weight((cell, cell_c), index = 1, evidences=evidence["SUC type 2"]) * \
                                (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                                (cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 1"]) ** (sigma[c] - 1)) * \
                                math.prod(1 if (e == j or e == c) else \
                                (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e]) \
                                for e, cell_s in enumerate(cells))
                                if sigma[c] >= 2:
                                    lambda_eta = lambda_eta + \
                                    (Rational((rho[i * n_cells + j]) * (rho[c * n_cells + d] - 1), 1) \
                                    if i != c or j != d else \
                                    Rational((rho[i * n_cells + j]) * (rho[i * n_cells + j] - 2), 1)) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                                    (cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 1"]) ** (sigma[c] - 2)) * \
                                    (cell_graph.get_two_table_with_pred_weight((cell, cell_c), index = 1, evidences=evidence["SUC type 1"])) * \
                                    math.prod(1 if (e == j or e == c) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e]) \
                                    for e, cell_s in enumerate(cells))
                            else:
                                lambda_eta = eta * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                                    (cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 1"]) ** (sigma[c] - 1)) * \
                                    cell_graph.get_two_table_weight((cell, pred), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred)] - 1) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 1"]) * \
                                    math.prod(1 if (e == j or e == c or cell_s == pred) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                            new_rho = list(rho)
                            new_rho[i * n_cells + j] -= 1
                            new_rho[c * n_cells + d] -= 1
                            new_rho[i * n_cells + d] += 1
                            new_sigma = list(sigma)
                            new_sigma[m] += 1
                            new_key = (tuple(new_sigma), rho_single, tuple(new_rho), cell)
                            if h_old * W_cell * lambda_eta != 0:
                                out.append((new_key, h_old * W_cell * lambda_eta))
            return out

        def merge(h_old, sigma, rho_single, rho, cell, m, pred):
            out = []
            for i, cell_i in enumerate(cells):
                for j, cell_j in enumerate(cells):
                    if rho[i * n_cells + j] <= 0:
                        continue
                    for c, cell_c in enumerate(cells):
                        #merge to as if connecting a -'-,-> b to b-'-,-> c
                        #merge2
                        #----------------------------------------------------------------
                        if rho[j * n_cells + c] > (0 if i != j or j != c else 1):
                            eta = Rational(rho[i * n_cells + j] * rho[j * n_cells + c], 1) \
                                if i != j or j != c else \
                                Rational(rho[i * n_cells + j] * (rho[i * n_cells + j] - 1), 1)
                            W_cell = cell_graph.get_cell_weight(cell)
                            

                            if cell_j == pred:
                                lambda_eta = (rho[j * n_cells + c] if i != j or j != c else rho[j * n_cells + c] - 1) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    math.prod(1 if (e == j) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells)) + \
                                    (rho[i * n_cells + j] if i != j or j != c else rho[i * n_cells + j] - 1) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    math.prod(1 if (e == j) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                                if sigma[j] >= 3:
                                    lambda_eta = lambda_eta + \
                                    ((((rho[i * n_cells + j] - 1) * rho[j * n_cells + c])   \
                                    if i != j or j != c else \
                                    ((rho[i * n_cells + j] - 1) * (rho[i * n_cells + j] - 1))) +  \
                                    (((rho[i * n_cells + j]) * (rho[j * n_cells + c] - 1))   \
                                    if i != j or j != c else \
                                    ((rho[i * n_cells + j]) * (rho[i * n_cells + j] - 2))) + \
                                    (eta if sigma[j] > rho[i * n_cells + j] + rho[j * n_cells + c] else 0)) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 1"])) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 3)) * \
                                    math.prod(1 if (e == j) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                            elif cell_j != pred:
                                lambda_eta = eta *\
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    cell_graph.get_two_table_weight((cell, pred), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred)] - 1) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 1"]) * \
                                    math.prod(1 if (e == j or cell_s == pred) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                            
                                
                            new_rho = list(rho)
                            new_rho[i * n_cells + j] -= 1
                            new_rho[j * n_cells + c] -= 1
                            new_rho[i * n_cells + c] += 1
                            new_sigma = list(sigma)
                            new_sigma[m] += 1
                            new_key = (tuple(new_sigma), tuple(new_rho), cell)
                            if h_old * W_cell * lambda_eta != 0:
                                out.append((new_key, h_old * W_cell * lambda_eta))
                        #----------------------------------------------------------------
                        if j == c:
                            continue
                        for d, cell_d in enumerate(cells):
                            if rho[c * n_cells + d] <= (0 if i != c or j != d else 1):
                                continue
                            #merge1
                            eta = Rational(rho[i * n_cells + j] * rho[c * n_cells + d], 1) \
                                if i != c or j != d else \
                                Rational(rho[i * n_cells + j] * (rho[i * n_cells + j] - 1), 1)
                            W_cell = cell_graph.get_cell_weight(cell)
                            if cell_j == pred:
                                lambda_eta = (rho[c * n_cells + d] if i != c or j != d else rho[c * n_cells + d] - 1) * \
                                cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1, evidences=evidence["SUC type 3"]) * \
                                cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 2"]) * \
                                (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                                (cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 1"]) ** (sigma[c] - 1)) * \
                                math.prod(1 if (e == j or e == c) else \
                                (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                for e, cell_s in enumerate(cells))
                                if sigma[j] >= 2:
                                    lambda_eta = lambda_eta + \
                                    (Rational((rho[i * n_cells + j] - 1) * rho[c * n_cells + d], 1) \
                                    if i != c or j != d else \
                                    Rational((rho[i * n_cells + j] - 1) * (rho[i * n_cells + j] - 1), 1)) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                    (cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 1"]) ** (sigma[c] - 1)) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, cell_j), index = 1,  evidences=evidence["SUC type 1"])* \
                                    math.prod(1 if (e == j or e == c) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                            elif cell_c == pred:
                                lambda_eta = (rho[i * n_cells + j] if i != c or j != d else rho[i * n_cells + j] - 1) * \
                                cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                cell_graph.get_two_table_with_pred_weight((cell, cell_c), index = 1, evidences=evidence["SUC type 2"]) * \
                                (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                                (cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 1"]) ** (sigma[c] - 1)) * \
                                math.prod(1 if (e == j or e == c) else \
                                (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e]) \
                                for e, cell_s in enumerate(cells))
                                if sigma[c] >= 2:
                                    lambda_eta = lambda_eta + \
                                    (Rational((rho[i * n_cells + j]) * (rho[c * n_cells + d] - 1), 1) \
                                    if i != c or j != d else \
                                    Rational((rho[i * n_cells + j]) * (rho[i * n_cells + j] - 2), 1)) * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                                    (cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 1"]) ** (sigma[c] - 2)) * \
                                    (cell_graph.get_two_table_with_pred_weight((cell, cell_c), index = 1, evidences=evidence["SUC type 1"])) * \
                                    math.prod(1 if (e == j or e == c) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e]) \
                                    for e, cell_s in enumerate(cells))
                            else:
                                lambda_eta = eta * \
                                    cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                    cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 2"]) * \
                                    (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                                    (cell_graph.get_two_table_weight((cell, cell_c), evidences=evidence["SUC type 1"]) ** (sigma[c] - 1)) * \
                                    cell_graph.get_two_table_weight((cell, pred), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred)] - 1) * \
                                    cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 1"]) * \
                                    math.prod(1 if (e == j or e == c or cell_s == pred) else \
                                    (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                                    for e, cell_s in enumerate(cells))
                            new_rho = list(rho)
                            new_rho[i * n_cells + j] -= 1
                            new_rho[c * n_cells + d] -= 1
                            new_rho[i * n_cells + d] += 1
                            new_sigma = list(sigma)
                            new_sigma[m] += 1
                            new_key = (tuple(new_sigma), tuple(new_rho), cell)
                            if h_old * W_cell * lambda_eta != 0:
                                out.append((new_key, h_old * W_cell * lambda_eta))
            return out
        
        def head(h_old, sigma, rho_single, rho, cell, m, pred):
            out = []
            for i, cell_i in enumerate(cells):
                for j, cell_j in enumerate(cells):
                    if rho[i * n_cells + j] <= 0 and (rho_single[i] <= 0 or i != j):
                        continue
                    W_cell = cell_graph.get_cell_weight(cell)
                    lambda_eta = 0                    
                    if cell_i == pred and rho[i * n_cells + j] > 0:
                        lambda_eta = (cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 1"]) ** (sigma[i] - 1)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 2"]) * \
                            math.prod(1 if e == i else cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
                            for e, cell_s in enumerate(cells))
                        if sigma[i] >= 2:
                            eta = 0
                            if rho[i * n_cells + j] > 0:
                                eta = rho[i * n_cells + j] - 1
                            if sigma[i] > rho[i * n_cells + j]:
                                eta += rho[i * n_cells + j]
                            lambda_eta = lambda_eta + \
                                eta * \
                                cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 2"]) * \
                                (cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 1"]) ** (sigma[i] - 2)) * \
                                cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 1"]) * \
                                math.prod(1 if e == i else cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
                                for e, cell_s in enumerate(cells))
                    elif cell_i != pred and rho[i * n_cells + j] > 0:
                        lambda_eta = rho[i * n_cells + j] * \
                            cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 2"]) * \
                            (cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 1"]) ** (sigma[i] - 1)) * \
                            (cell_graph.get_two_table_weight((cell, pred), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred)] - 1)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 1"]) * \
                            math.prod(1 if (e == j or cell_s == pred) else \
                            (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                            for e, cell_s in enumerate(cells))
                    new_rho = list(rho)
                    new_rho[i * n_cells + j] -= 1
                    new_rho[m * n_cells + j] += 1
                    new_sigma = list(sigma)
                    new_sigma[m] += 1
                    new_key = (tuple(new_sigma), rho_single, tuple(new_rho), cell)
                    if h_old * W_cell * lambda_eta != 0:
                        out.append((new_key, h_old * W_cell * lambda_eta))

                    if i != j or rho_single[i] <= 0:
                        continue

                    if cell_i == pred and rho_single[i] > 0:
                        lambda_eta = (cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 1"]) ** (sigma[i] - 1)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 2"]) * \
                            math.prod(1 if e == i else cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
                            for e, cell_s in enumerate(cells))
                        if sigma[i] >= 2:
                            eta = 0
                            if rho_single[i] > 0:
                                eta = rho_single[i] - 1
                            if sigma[i] > rho_single[i]:
                                eta += rho_single[i]
                            lambda_eta = lambda_eta + \
                                eta * \
                                cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 2"]) * \
                                (cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 1"]) ** (sigma[i] - 2)) * \
                                cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 1"]) * \
                                math.prod(1 if e == i else cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
                                for e, cell_s in enumerate(cells))
                    elif cell_i != pred and rho_single[i] > 0:
                        lambda_eta = rho_single[i] * \
                            cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 2"]) * \
                            (cell_graph.get_two_table_weight((cell, cell_i), evidences=evidence["SUC type 1"]) ** (sigma[i] - 1)) * \
                            (cell_graph.get_two_table_weight((cell, pred), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred)] - 1)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 1"]) * \
                            math.prod(1 if (e == j or cell_s == pred) else \
                            (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                            for e, cell_s in enumerate(cells))
                    new_rho_single = list(rho_single)
                    new_rho_single[i] -= 1
                    new_rho = list(rho)
                    new_rho[m * n_cells + j] += 1
                    new_sigma = list(sigma)
                    new_sigma[m] += 1
                    new_key = (tuple(new_sigma), tuple(new_rho_single), tuple(new_rho), cell)
                    if h_old * W_cell * lambda_eta != 0:
                        out.append((new_key, h_old * W_cell * lambda_eta))
            return out
        
        def tail(h_old, sigma, rho_single, rho, cell, m, pred):
            out = []
            for i, cell_i in enumerate(cells):
                for j, cell_j in enumerate(cells):
                    if rho[i * n_cells + j] <= 0 and (rho_single[i] <= 0 or i != j):
                        continue
                    W_cell = cell_graph.get_cell_weight(cell)
                    lambda_eta = 0
                    if cell_j == pred and rho[i * n_cells + j] > 0:
                        lambda_eta = (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 3"]) * \
                            math.prod(1 if e == j else cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
                            for e, cell_s in enumerate(cells))
                        if sigma[j] >= 2:
                            eta = 0
                            if rho[i * n_cells + j] > 0:
                                eta = rho[i * n_cells + j] - 1
                            if sigma[j] > rho[i * n_cells + j]:
                                eta += rho[i * n_cells + j]
                            lambda_eta = lambda_eta + \
                                eta * \
                                cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 1"]) * \
                                math.prod(1 if e == j else cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
                                for e, cell_s in enumerate(cells))
                    elif cell_j != pred and rho[i * n_cells + j] > 0:
                        lambda_eta = (rho[i * n_cells + j]) * \
                            cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                            \
                            (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                            \
                            cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 1"]) * \
                            cell_graph.get_two_table_weight((cell, pred), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred)] - 1) * \
                            math.prod(1 if (e == j or cell_s == pred) else \
                            (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                            for e, cell_s in enumerate(cells))
                    new_rho = list(rho)
                    new_rho[i * n_cells + j] -= 1
                    new_rho[i * n_cells + m] += 1
                    new_sigma = list(sigma)
                    new_sigma[m] += 1
                    new_key = (tuple(new_sigma), rho_single, tuple(new_rho), cell) 
                    if h_old * W_cell * lambda_eta != 0: #Multiplying all by rho is bad !!!
                        out.append((new_key, h_old * W_cell * lambda_eta))

                    if i != j or rho_single[j] <= 0:
                        continue

                    if cell_j == pred and rho_single[j] > 0:
                        lambda_eta = (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                            cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 3"]) * \
                            math.prod(1 if e == j else cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
                            for e, cell_s in enumerate(cells))
                        if sigma[j] >= 2:
                            eta = 0
                            if rho_single[j] > 0:
                                eta = rho_single[j] - 1
                            if sigma[j] > rho_single[j]:
                                eta += rho_single[j]
                            lambda_eta = lambda_eta + \
                                eta * \
                                cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                                (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 2)) * \
                                cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 1"]) * \
                                math.prod(1 if e == j else cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
                                for e, cell_s in enumerate(cells))
                    elif cell_j != pred and rho_single[j] > 0:
                        lambda_eta = (rho_single[j]) * \
                            cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 3"]) * \
                            \
                            (cell_graph.get_two_table_weight((cell, cell_j), evidences=evidence["SUC type 1"]) ** (sigma[j] - 1)) * \
                            \
                            cell_graph.get_two_table_with_pred_weight((cell, pred), index = 1, evidences=evidence["SUC type 1"]) * \
                            cell_graph.get_two_table_weight((cell, pred), evidences=evidence["SUC type 1"]) ** (sigma[cells.index(pred)] - 1) * \
                            math.prod(1 if (e == j or cell_s == pred) else \
                            (cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e])\
                            for e, cell_s in enumerate(cells))
                    new_rho_single = list(rho_single)
                    new_rho_single[j] -= 1
                    new_rho = list(rho)
                    new_rho[j * n_cells + m] += 1
                    new_sigma = list(sigma)
                    new_sigma[m] += 1
                    new_key = (tuple(new_sigma), tuple(new_rho_single), tuple(new_rho), cell) 
                    if h_old * W_cell * lambda_eta != 0: #Multiplying all by rho is bad !!!
                        out.append((new_key, h_old * W_cell * lambda_eta))
            return out
        
        def only(h_old, sigma, rho_single, rho, cell, m, pred):
            out = []
            W_cell = cell_graph.get_cell_weight(cell)
            
            lambda_ = math.prod(cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
                        if cell_s != pred else \
                        cell_graph.get_two_table_with_pred_weight((cell, cell_s), index = 1, evidences=evidence["SUC type 1"]) * \
                        cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** (sigma[e] - 1) \
                        for e, cell_s in enumerate(cells))
            
            #lambda_ = math.prod(cell_graph.get_two_table_weight((cell, cell_s), evidences=evidence["SUC type 1"]) ** sigma[e] \
            #            for e, cell_s in enumerate(cells))
            new_rho_single = list(rho_single)
            new_rho_single[m] += 1
            new_sigma = list(sigma)
            new_sigma[m] += 1
            new_key = (tuple(new_sigma), tuple(new_rho_single), rho, cell)
            if (h_old * W_cell * lambda_ != 0):
                out.append((new_key, h_old * W_cell * lambda_))
            return out
        
        for i in range(1, domain_size):
            old_table = table
            table = dict()
            if i >= (domain_size + 1) // 2:
                max_rho_size = domain_size - i
            else:
                max_rho_size = domain_size
            for j, cell in enumerate(cells):
                for key, h_old in old_table.items():
                    sigma, rho_single, rho, pred = key
                    rho_size = sum(list(rho)) + sum(list(rho_single))
                    if rho_size > 1:
                    #if merge is possible, add merges
                        h_news = merge_2(h_old, sigma, rho_single, rho, cell, j, pred)
                        print("merge:", h_news)
                        for new_key, h_new in h_news:
                            table[new_key] = table.get(new_key, Rational(0, 1)) + h_new
                    
                    if rho_size <= max_rho_size:
                    #if |rho_old| = |rho_new| is possible, do head and tail
                        h_news = tail(h_old, sigma, rho_single, rho, cell, j, pred)
                        print("tail:", h_news)
                        for new_key, h_new in h_news:
                            table[new_key] = table.get(new_key, Rational(0, 1)) + h_new
                        h_news = head(h_old, sigma, rho_single, rho, cell, j, pred)
                        print("head:",  h_news)
                        for new_key, h_new in h_news:
                            table[new_key] = table.get(new_key, Rational(0, 1)) + h_new

                    if rho_size < max_rho_size:
                    #if |rho_old| + 1 = |rho_new| is posible, do only
                    #e. g. at no time we need h(m, sigma, rho)
                    #where |rho| > domain_size - m + 1
                        h_news = only(h_old, sigma, rho_single, rho, cell, j, pred)
                        print("only:", h_news)
                        for new_key, h_new in h_news:
                            table[new_key] = table.get(new_key, Rational(0, 1)) + h_new

            print(table)
        res = res + weight * sum(table.values())
    return res




def incremental_multiple_orders_wfomc_old(context: WFOMCContext, t) -> RingElement:
    formula = context.formula
    domain = context.domain
    get_weight = context.get_weight
    leq_pred = context.leq_pred
    predecessor_preds = context.predecessor_preds
    successor_pred = context.successor_pred
    first_pred = context.first_pred
    last_pred = context.last_pred

    #All possible evidence - 
    # SUC(a, b), SUC(b, a), ~SUC, LEQ(b, a), PRED(b, a), ~PRED(b, a)
    # 1          0          0     1          1           0
    # 1          0          0     1          0           1
    # 0          1          0     1          1           0
    # 0          1          0     1          0           1
    # 0          0          1     1          1           0
    # 0          0          1     1          0           1

    #remember last string -> keeps info about last predicate

    #make that into a new file
    

    if first_pred is not None or last_pred is not None:
        if successor_pred is None:
            raise RuntimeError("FIRST and LAST are only supported with SUC at the moment!")
    if predecessor_preds is not None and successor_pred is not None:
        raise RuntimeError("PRED is only supported without SUC at the moment!")
    res = Rational(0, 1)
    domain_size = len(domain)
    for cell_graph, weight in build_cell_graphs(
        formula, get_weight,
        leq_pred=leq_pred,
        predecessor_preds=predecessor_preds,
        successor_pred=successor_pred,
        first_pred=first_pred,
        last_pred=last_pred,
        domain_size=domain_size
    ):
        #cell_graph.show()
        cells = cell_graph.get_cells()
        n_cells = len(cells)
        domain_size = len(domain)

        if first_pred is not None and last_pred is not None and domain_size > 1:
            first_cells = []
            body_cells = []
            last_cells = []
            for i, cell in enumerate(cells):
                if cell.is_positive(first_pred):
                    first_cells.append((i, cell))
                elif cell.is_positive(last_pred):
                    last_cells.append((i, cell))
                else:
                    body_cells.append((i, cell))
        elif first_pred is not None and domain_size > 1:
            first_cells = []
            body_cells = []
            for i, cell in enumerate(cells):
                if cell.is_positive(first_pred):
                    first_cells.append((i, cell))
                else:
                    body_cells.append((i, cell))
        elif last_pred is not None and domain_size > 1:
            last_cells = []
            body_cells = []
            for i, cell in enumerate(cells):
                if cell.is_positive(last_pred):
                    last_cells.append((i, cell))
                else:
                    body_cells.append((i, cell))
        elif last_pred is not None:
            last_cells = [(i, cell) for i, cell in enumerate(cells)]

        if successor_pred is not None and last_pred is not None:
            table = dict(
                (
                    (
                        tuple(int(k == i) for k in range(n_cells)),
                        tuple(int(i * n_cells + i == k) for k in range(n_cells**2))
                    ),
                    cell_graph.get_cell_weight(cell),
                )
                for i, cell in last_cells
            )
        elif successor_pred is not None and first_pred is not None:
            table = dict(
                (
                    (
                        tuple(int(k == i) for k in range(n_cells)),
                        tuple(int(i * n_cells + i == k) for k in range(n_cells**2))
                    ),
                    cell_graph.get_cell_weight(cell),
                )
                for i, cell in body_cells
            )
        elif successor_pred is not None:
            table = dict(
                (
                    (
                        tuple(int(k == i) for k in range(n_cells)),
                        tuple(int(i * n_cells + i == k) for k in range(n_cells**2))
                    ),
                    cell_graph.get_cell_weight(cell),
                )
                for i, cell in enumerate(cells)
            )
        elif predecessor_preds is not None:
            table = dict(
                (
                    (
                        tuple(int(k == i) for k in range(n_cells)),
                        cell
                    ),
                    cell_graph.get_cell_weight(cell),
                )
                for i, cell in enumerate(cells)
            )
        else:
            table = dict(
                (
                    tuple(int(k == i) for k in range(n_cells)),
                    cell_graph.get_cell_weight(cell),
                )
                for i, cell in enumerate(cells)
            )

        if successor_pred is None:
            for _ in range(domain_size - 1):
                old_table = table
                table = dict()
                for j, cell in enumerate(cells):
                    w = cell_graph.get_cell_weight(cell)
                    for key, w_old in old_table.items():
                        if predecessor_preds is None:
                            ivec = key
                            w_new = w_old * w * reduce(
                                lambda x, y: x * y,
                                (
                                    cell_graph.get_two_table_weight((cell, cells[k]))
                                    ** int(ivec[k]) for k in range(n_cells)
                                ),
                                Rational(1, 1)
                            )
                        else:
                            ivec, last_cell = key
                            w_new = w_old * w
                            for k, other_cell in enumerate(cells):
                                if other_cell == last_cell:
                                    w_new = (
                                        w_new * cell_graph.get_two_table_with_pred_weight((cell, other_cell))
                                        * cell_graph.get_two_table_weight((cell, other_cell)) ** max(ivec[k] - 1, 0)
                                    )
                                else:
                                    w_new = w_new * cell_graph.get_two_table_weight((cell, other_cell)) ** ivec[k]
                        ivec = list(ivec)
                        ivec[j] += 1
                        ivec = tuple(ivec)
                        if predecessor_preds is None:
                            w_new = w_new + table.get(ivec, Rational(0, 1))
                            table[ivec] = w_new
                        else:
                            w_new = w_new + table.get((ivec, cell), Rational(0, 1))
                            table[(tuple(ivec), cell)] = w_new
            res = res + weight * sum(table.values())
            continue
        def merge(h_old, sigma, rho, cell, m):
            out = []
            for a, cell_a in enumerate(cells):
                for b, cell_b in enumerate(cells):
                    if rho[a * n_cells + b] <= 0:
                        continue
                    for c, cell_c in enumerate(cells):
                        #merge to as if connecting a -'-,-> b to b-'-,-> c
                        #merge2
                        #----------------------------------------------------------------
                        if rho[b * n_cells + c] > (0 if a != b or b != c else 1):
                            eta = Rational(rho[a * n_cells + b] * rho[b * n_cells + c], 1) \
                                if a != b or b != c else \
                                Rational(rho[a * n_cells + b] * (rho[a * n_cells + b] - 1), 1)
                            W_cell = cell_graph.get_cell_weight(cell)
                            lambda_ = cell_graph.get_two_table_with_suc_weight((cell_b, cell), suc_type = 2) * \
                                cell_graph.get_two_table_with_suc_weight((cell_b, cell), suc_type = 3) * \
                                (cell_graph.get_two_table_with_suc_weight((cell_b, cell), suc_type = 1) ** (sigma[b] - 2)) * \
                                math.prod(1 if (e == b) else \
                                (cell_graph.get_two_table_with_suc_weight((cell_s, cell), suc_type = 1) ** sigma[e])\
                                for e, cell_s in enumerate(cells))
                            new_rho = list(rho)
                            new_rho[a * n_cells + b] -= 1
                            new_rho[b * n_cells + c] -= 1
                            new_rho[a * n_cells + c] += 1
                            new_sigma = list(sigma)
                            new_sigma[m] += 1
                            new_key = (tuple(new_sigma), tuple(new_rho))
                            if h_old * eta * W_cell * lambda_ != 0:
                                out.append((new_key, h_old * eta * W_cell * lambda_))
                        #----------------------------------------------------------------
                        if b == c:
                            continue
                        for d, cell_d in enumerate(cells):
                            if rho[c * n_cells + d] <= (0 if a != c or b != d else 1):
                                continue
                            #merge1
                            eta = Rational(rho[a * n_cells + b] * rho[c * n_cells + d], 1) \
                                if a != c or b != d else \
                                Rational(rho[a * n_cells + b] * (rho[a * n_cells + b] - 1), 1)
                            W_cell = cell_graph.get_cell_weight(cell)
                            lambda_ = cell_graph.get_two_table_with_suc_weight((cell_b, cell), suc_type = 2) * \
                                cell_graph.get_two_table_with_suc_weight((cell_c, cell), suc_type = 3) * \
                                (cell_graph.get_two_table_with_suc_weight((cell_b, cell), suc_type = 1) ** (sigma[b] - 1)) * \
                                (cell_graph.get_two_table_with_suc_weight((cell_c, cell), suc_type = 1) ** (sigma[c] - 1)) * \
                                math.prod(1 if (e == b or e == c) else \
                                (cell_graph.get_two_table_with_suc_weight((cell_s, cell), suc_type = 1) ** sigma[e])\
                                for e, cell_s in enumerate(cells))
                            new_rho = list(rho)
                            new_rho[a * n_cells + b] -= 1
                            new_rho[c * n_cells + d] -= 1
                            new_rho[a * n_cells + d] += 1
                            new_sigma = list(sigma)
                            new_sigma[m] += 1
                            new_key = (tuple(new_sigma), tuple(new_rho))
                            if h_old * eta * W_cell * lambda_ != 0:
                                out.append((new_key, h_old * eta * W_cell * lambda_))
            return out
        
        def head(h_old, sigma, rho, cell, m):
            out = []
            for a, cell_a in enumerate(cells):
                for b, cell_b in enumerate(cells):
                    if rho[a * n_cells + b] <= 0:
                        continue

                    W_cell = cell_graph.get_cell_weight(cell)
                    lambda_ = cell_graph.get_two_table_with_suc_weight((cell_a, cell), suc_type=3) * \
                        (cell_graph.get_two_table_with_suc_weight((cell_a, cell), suc_type=1) ** (sigma[a] - 1)) * \
                        math.prod(1 if e == a else cell_graph.get_two_table_with_suc_weight((cell_s, cell), suc_type = 1) ** sigma[e] \
                        for e, cell_s in enumerate(cells))
                    new_rho = list(rho)
                    new_rho[a * n_cells + b] -= 1
                    new_rho[m * n_cells + b] += 1
                    new_sigma = list(sigma)
                    new_sigma[m] += 1
                    new_key = (tuple(new_sigma), tuple(new_rho))
                    if h_old * rho[a * n_cells + b] * W_cell * lambda_ != 0:
                        out.append((new_key, h_old * rho[a * n_cells + b] * W_cell * lambda_))
            return out
        
        def tail(h_old, sigma, rho, cell, m):
            out = []
            for a, cell_a in enumerate(cells):
                for b, cell_b in enumerate(cells):
                    if rho[a * n_cells + b] <= 0:
                        continue
                    W_cell = cell_graph.get_cell_weight(cell)
                    lambda_ = cell_graph.get_two_table_with_suc_weight((cell_b, cell), suc_type=2) * \
                        (cell_graph.get_two_table_with_suc_weight((cell_b, cell), suc_type=1) ** (sigma[b] - 1)) * \
                        math.prod(1 if e == b else cell_graph.get_two_table_with_suc_weight((cell_s, cell), suc_type = 1) ** sigma[e] \
                        for e, cell_s in enumerate(cells))
                    new_rho = list(rho)
                    new_rho[a * n_cells + b] -= 1
                    new_rho[a * n_cells + m] += 1
                    new_sigma = list(sigma)
                    new_sigma[m] += 1
                    new_key = (tuple(new_sigma), tuple(new_rho))
                    if h_old * rho[a * n_cells + b] * W_cell * lambda_ != 0:
                        out.append((new_key, h_old * rho[a * n_cells + b] * W_cell * lambda_))
            return out
        
        def only(h_old, sigma, rho, cell, m):
            out = []
            W_cell = cell_graph.get_cell_weight(cell)
            lambda_ = math.prod(cell_graph.get_two_table_with_suc_weight((cell_s, cell), suc_type = 1) ** sigma[e] \
                        for e, cell_s in enumerate(cells))
            new_rho = list(rho)
            new_rho[m * n_cells + m] += 1
            new_sigma = list(sigma)
            new_sigma[m] += 1
            new_key = (tuple(new_sigma), tuple(new_rho))
            if (h_old * W_cell * lambda_ != 0):
                out.append((new_key, h_old * W_cell * lambda_))
            return out
        
        for i in range(1, domain_size - (0 if first_pred is None else 1)):
            old_table = table
            table = dict()
            if i >= (domain_size + 1) // 2:
                max_rho_size = domain_size - i
            else:
                max_rho_size = domain_size
            for j, cell in enumerate(cells) if last_pred is None and first_pred is None else body_cells:
                w = cell_graph.get_cell_weight(cell)
                for key, h_old in old_table.items():
                    sigma, rho = key
                    rho_size = sum(list(rho))
                    if rho_size > 1:
                    #if merge is possible, add merges
                        h_news = merge(h_old, sigma, rho, cell, j)
                        for new_key, h_new in h_news:
                            table[new_key] = table.get(new_key, Rational(0, 1)) + h_new
                    
                    if rho_size <= max_rho_size:
                    #if |rho_old| = |rho_new| is possible, do head and tail
                        h_news = tail(h_old, sigma, rho, cell, j)
                        for new_key, h_new in h_news:
                            table[new_key] = table.get(new_key, Rational(0, 1)) + h_new
                        h_news = head(h_old, sigma, rho, cell, j)
                        for new_key, h_new in h_news:
                            table[new_key] = table.get(new_key, Rational(0, 1)) + h_new

                    if rho_size < max_rho_size:
                    #if |rho_old| + 1 = |rho_new| is posible, do only
                    #e. g. at no time we need h(m, sigma, rho)
                    #where |rho| > domain_size - m + 1
                        h_news = only(h_old, sigma, rho, cell, j)
                        for new_key, h_new in h_news:
                            table[new_key] = table.get(new_key, Rational(0, 1)) + h_new

        print(sum(table.values()))
        if first_pred is not None and domain_size > 1:
            max_rho_size = 1
            old_table = table
            table = dict()
            for j, cell in first_cells:
                w = cell_graph.get_cell_weight(cell)
                for key, h_old in old_table.items():
                    sigma, rho = key
                    rho_size = sum(list(rho))
                    if rho_size == 2:
                    #if merge is possible, add merges
                        h_news = merge(h_old, sigma, rho, cell, j)
                        for new_key, h_new in h_news:
                            table[new_key] = table.get(new_key, Rational(0, 1)) + h_new
                    
                    if rho_size <= max_rho_size:
                    #if |rho_old| = |rho_new| is possible, do head and tail
                        h_news = tail(h_old, sigma, rho, cell, j)
                        for new_key, h_new in h_news:
                            table[new_key] = table.get(new_key, Rational(0, 1)) + h_new
                        h_news = head(h_old, sigma, rho, cell, j)
                        for new_key, h_new in h_news:
                            table[new_key] = table.get(new_key, Rational(0, 1)) + h_new
        print(sum(table.values()))
        res = res + weight * sum(table.values())

    return res
