FORMULA =  r'''\forall X: (\forall Y: (E(X, Y) -> LEQ(X, Y))) &
\forall X: (\forall Y: (E(X, Y) -> ((Red(X) & ~Red(Y)) | (Red(Y) & ~Red(X)))))
'''


def write_wfomcs(n):
    with open(f'{n}.wfomcs', "w") as fw:
        fw.write(FORMULA)
        fw.write('\n')
        fw.write(f"domain = {n}\n")
    

if __name__ == "__main__":
    write_wfomcs(1)

    for i in range(50, 1001, 50):
        write_wfomcs(i)
