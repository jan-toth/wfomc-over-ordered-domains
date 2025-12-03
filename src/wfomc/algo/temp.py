from functools import reduce

from wfomc.cell_graph import build_cell_graphs
from wfomc.context import WFOMCContext
from wfomc.network import UnaryEvidenceEncoding
from wfomc.utils import RingElement, Rational, MultinomialCoefficients
from enum import Enum
import math


############### THIS VERSION SUPPOSES SUC WAS ALREADY FOUND ########################################


def incremental_wfomc_with_successor_from_another_linear_order(context: WFOMCContext,
                      circle_len: int = None) -> RingElement:
    formula = context.formula
    domain = context.domain
    get_weight = context.get_weight
    leq_pred = context.leq_pred
    res = Rational(0, 1)
    domain_size = len(domain)

    for cell_graph, weight in build_cell_graphs(
        formula, get_weight,
        leq_pred=leq_pred
    ):
        # cell_graph.show()
        cells = cell_graph.get_cells()
        n_cells = len(cells)

        def helper(cell, pc_pred, pc_ccs):
            for i, p in enumerate(pc_pred):
                if cell.is_positive(p) and pc_ccs[i] > 0:
                    return i
            return None

        if context.unary_evidence_encoding == \
                UnaryEvidenceEncoding.PC:
            pc_pred, pc_ccs = zip(*context.partition_constraint.partition)
            table = dict()
            for i, cell in enumerate(cells):
                j = helper(cell, pc_pred, pc_ccs)
                if j is None:
                    continue
                table[
                    (
                        tuple(int(k == i) for k in range(n_cells)),
                    )
                ] = (
                    cell_graph.get_cell_weight(cell),
                    tuple(cc - 1 if k == j else cc
                          for k, cc in enumerate(pc_ccs))
                )
        else:
            table = dict(
                (
                    (
                        tuple(int(k == i) for k in range(n_cells)),
                    ),
                    (
                        cell_graph.get_cell_weight(cell),
                        None
                    )
                )
                for i, cell in enumerate(cells)
            )

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

        for cur_idx in range(domain_size - 1):
            old_table = table
            table = dict()
            for j, cell in enumerate(cells):
                w = cell_graph.get_cell_weight(cell)
                for (ivec, last_cells, first_cell), (w_old, old_ccs) in old_table.items():
                    old_ivec = list(ivec)
                    if old_ccs is not None:
                        idx = helper(cell, pc_pred, old_ccs)
                        if idx is None:
                            continue
                        new_ccs = tuple(
                            cc - 1 if k == idx else cc
                            for k, cc in enumerate(old_ccs)
                        )
                    else:
                        new_ccs = None

                    w_new = w_old * w
                    # for cycular predecessor
                    # NOTE: only support either circular predecessor or predecessors but not both
                    if cur_idx == circle_len - 2 and first_cell is not None:
                        w_new = w_new * cell_graph.get_two_table_with_pred_weight(
                            (first_cell, cell), 1
                        )
                        old_ivec[cells.index(first_cell)] -= 1
                    # for predecessors
                    if last_cells is not None:
                        for pred_idx in pred_orders:
                            if cur_idx >= pred_idx - 1:
                                pred_cell = last_cells[-pred_idx]
                                w_new = w_new * cell_graph.get_two_table_with_pred_weight(
                                    (cell, pred_cell), pred_idx
                                )
                                old_ivec[cells.index(pred_cell)] -= 1
                        new_last_cells = last_cells[1:] + (cell,)
                    else:
                        new_last_cells = None
                    w_new = w_new * reduce(
                        lambda x, y: x * y,
                        (
                            cell_graph.get_two_table_weight((cell, other_cell)) ** old_ivec[k]
                            for k, other_cell in enumerate(cells)
                        )
                    )
                    ivec = tuple((num if k != j else num + 1) for k, num in enumerate(ivec))
                    new_last_cells = (
                        tuple(new_last_cells)
                        if new_last_cells is not None else None
                    )
                    w_new = w_new + table.get(
                        (ivec, new_last_cells, first_cell),
                        (Rational(0, 1), ())
                    )[0]
                    table[(tuple(ivec), new_last_cells, first_cell)] = (
                        w_new, new_ccs
                    )
        res = res + weight * sum(w for w, _ in table.values())

    if context.unary_evidence_encoding == \
            UnaryEvidenceEncoding.PC:
        res = res / MultinomialCoefficients.coef(
            tuple(
                i for _, i in context.partition_constraint.partition
            )
        )
    return res
