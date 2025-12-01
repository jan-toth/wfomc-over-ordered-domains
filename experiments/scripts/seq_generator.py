import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description='Generate seqeunce splits CNFs for various domain sizes',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--dom_size', "-n", required=True, type=int)
    parser.add_argument("--head_tail", "-ht", action="store_true", help="Gnerate HEAD-TAIL cnf")
    parser.add_argument("--head_middle_tail", "-hmt", action="store_true", help="Gnerate HEAD-MIDDLE-TAIL cnf", default=False)

    args = parser.parse_args()
    return args


def generate_head_tail(n):
    nvars = n * (n + 1)
    clauses = []

    leq_id = lambda i, j: n*i + j

    for i in range(1, n + 1):
        for j in range(1, i):
            clauses.append([-leq_id(i, j)])
        for j in range(i, n + 1):
            leq_i_j = n*i + j
            clauses.append([leq_id(i, j)])

    for i in range(1, n + 1):
        for j in range(1, n + 1):
            clauses.append([-i, j, -leq_id(i, j)])

    with open(f'{n}_ht_e1.cnf', 'w') as fw:
        fw.write(f"p cnf {nvars} {len(clauses)}\n")
        for cl in clauses:
            for x in cl:
                fw.write(f"{x} ")
            fw.write("0\n")


def generate_head_middle_tail(n):
    def next_id():
        for i in range(1, n**2 + 2*n + 100):
            yield i

    ids = next_id()

    heads = [next(ids) for i in range(n)]
    tails = [next(ids) for i in range(n)]
    leq = [[next(ids) for j in range(n)] for i in range(n)]

    clauses = []
    for i in range(n):
        for j in range(i):
            clauses.append([-leq[i][j]])
        for j in range(i, n):
            clauses.append([leq[i][j]])

    for i in range(n):
        clauses.append([-heads[i], -tails[i]])

        for j in range(n):
            clauses.append([-heads[i], heads[j], -leq[j][i]])
            clauses.append([-tails[i], tails[j], -leq[i][j]])

    nvars = n * (n + 2)
    # clauses = []

    # leq_id = lambda i, j: n * (i + 1) + j

    # for i in range(1, n + 1):
    #     for j in range(1, i):
    #         clauses.append([-leq_id(i, j)])
    #     for j in range(i, n + 1):
    #         clauses.append([leq_id(i, j)])

    # for i in range(1, n + 1):
    #     clauses.append([-i, -i-n])

    #     for j in range(1, n + 1):
    #         clauses.append([-i, j, -leq_id(i, j)])
    #         clauses.append([-2*i, 2*j, -leq_id(j, i)])

    with open(f'{n}_hmt_e1.cnf', 'w') as fw:
        fw.write(f"p cnf {nvars} {len(clauses)}\n")
        for cl in clauses:
            for x in cl:
                fw.write(f"{x} ")
            fw.write("0\n")

if __name__ == "__main__":
    args = parse_args()

    if args.head_tail:
        generate_head_tail(args.dom_size)

    if args.head_middle_tail:
        generate_head_middle_tail(args.dom_size)

