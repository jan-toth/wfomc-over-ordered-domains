def write_cnf(n):
    nvars = n + n**2 + n**2
    
    def next_id():
        for i in range(1, nvars + 1):
            yield i

    ids = next_id()

    red = [next(ids) for i in range(n)]
    edge = [[next(ids) for i in range(n)] for j in range(n)]
    leq = [[next(ids) for j in range(n)] for i in range(n)]
    

    clauses = []

    for i in range(n):
        for j in range(n):
            clauses.append([-edge[i][j], leq[i][j]])
            clauses.append([-edge[i][j], red[i], red[j]])
            clauses.append([-edge[i][j], -red[i], -red[j]])

        for j in range(i):
            clauses.append([-leq[i][j]])
        for j in range(i, n):
            clauses.append([leq[i][j]])

    with open(f'{n}_e1.cnf', 'w') as fw:
        fw.write(f"p cnf {nvars} {len(clauses)}\n")
        for cl in clauses:
            for x in cl:
                fw.write(f"{x} ")
            fw.write("0\n")


if __name__ == "__main__":
    for i in range(5, 31, 5):
        write_cnf(i)
