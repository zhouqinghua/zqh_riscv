#!/usr/bin/python3
import os
import getopt
import sys
import importlib
import random
from functools import reduce

def printVec(t, name, data):
  print("const " + t + " " + name + "[" + str(len(data)) + "] = {")
  print(" "+reduce(lambda a,b: str(a) + ",\n " + str(b), data))
  print("};")

def spmv(p, d, idx, v):
  y = []
  for i in range(len(p) - 1):
    yi = 0
    for k in range(p[i], p[i+1]):
      yi = yi + d[k]*v[idx[k]]
    y.append(yi)
  return y


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h:', ['help', 'm=', 'n=', 'nnz=', 'seed='])
    except getopt.GetoptError:
        print("argv error,please input")

    m = 500
    n = 500
    approx_nnz = 500
    seed = 111

    for (k,v) in opts:
        if (k == '--m'):
            m = int(v)
        elif (k == '--n'):
            n = int(v)
        elif (k == '--nnz'):
            approx_nnz = int(v)
        elif (k == '--seed'):
            seed = int(v)
        else:
            assert(0), 'illegal prameter name: %s' %(k)

    random.seed(seed)
    
    pnnz = approx_nnz/(m*n)
    idx = []
    p = [0]
    
    for i in range(m):
      for j in range(n):
        if (random.random() < pnnz):
          idx.append(j)
      p.append(len(idx))
    
    nnz = len(idx)
    v = list(map(lambda i: random.randint(0, 1000), range(n)))
    d = list(map(lambda i: random.randint(0,1000), range(nnz)))

    print("#define R " + str(m))
    print("#define C " + str(n))
    print("#define NNZ " + str(nnz))
    printVec("double", "val", d)
    printVec("int", "idx", idx)
    printVec("double", "x", v)
    printVec("int", "ptr", p)
    printVec("double", "verify_data", spmv(p, d, idx, v))

if __name__ == "__main__":
    main()
