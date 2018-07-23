import numpy as np
import pandas as pd

def test():
	data = np.loadtxt("features0.csv", dtype=np.str, delimiter=",", skiprows=1)
	indexs = data[:,:2].astype(np.int32)
	dates = data[:,2]
	data = data[:,3:].astype(np.float32)
	print(data.shape)

if __name__ == "__main__":
	test()
	