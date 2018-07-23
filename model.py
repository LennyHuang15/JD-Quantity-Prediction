
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from scipy.stats import norm

vars = []
monthIdxs = []
dict_q = []
#[1,3,5,7,9,11,13,15,17]

def read(idx):# read "features{idx}.csv" and return X, y(label)
	file = "features" + str(idx) + ".csv"
	data = np.loadtxt(file, dtype=np.str, delimiter=",", skiprows=1)
	#indexs = data[:,:2].astype(np.int32)
	#dates = data[:,2]
	y = data[:, 3].astype(np.float32)
	data = data[:,4:].astype(np.float32)
	print("read(%d): "%idx + str(data.shape))
	return data.reshape(100, -1, data.shape[1]), y.reshape(100, -1)

def getVars():# read stdvars for all (sku,dc) into global vars
	global vars
	vars = np.loadtxt("stat.csv", dtype=np.str, delimiter=",", skiprows=1)
	vars = vars[:, 3].astype(np.float32)
	vars = vars.reshape(1000, 7)
	for sku in range(1000):
		for dc in range(6):
			if(vars[sku,dc] < 1e-3):
				vars[sku,dc] = vars[sku,6]
	vars = vars[:, :6]
	print("vars: " + str(vars.shape))

def getQs():# read q for all sku into global dict_q
	global dict_q
	dict_q = [0 for x in range(1000)]
	qs = np.loadtxt("sku_quantile.csv", dtype=np.str, delimiter=",", skiprows=1)
	skus, qs = qs[:,0].astype(np.int32), qs[:,1].astype(np.float32)
	for idx in range(1000):
		dict_q[skus[idx]-1] = qs[idx]
	dict_q = np.array(dict_q, dtype=np.float32)
	print("qs: "+str(dict_q.shape))

def getData(idx):# get 100 X, y, X_test, y_test, vars-for-skudc, q-for-sku for train and test
	data_X, data_y = read(idx)
	data_X = data_X.reshape(data_X.shape[0], 6, -1, data_X.shape[2])
	data_y = data_y.reshape(data_y.shape[0], 6, -1)
	#X, y = data_X[:,:,:monthIdxs[12],:], data_y[:,:,:monthIdxs[12]]
	#X_t, y_t = data_X[:,:,monthIdxs[12]:monthIdxs[13],:], data_y[:,:,monthIdxs[12]:monthIdxs[13]]
	X, y = data_X[:,:,:monthIdxs[24],:], data_y[:,:,:monthIdxs[24]]
	X_t, y_t = data_X[:,:,monthIdxs[24]:,:], data_y[:,:,monthIdxs[24]:]
	return X.reshape(-1, X.shape[-1]), y.reshape(-1),\
		X_t.reshape(-1, X_t.shape[-1]), y_t.reshape(-1),\
		vars[idx*100:(idx+1)*100,:], dict_q[idx*100:(idx+1)*100]
	
def modelValidate(X, y, X_t, y_t, stdvar, qs):# use 12 months to train and 2017.1 to validate
	print("train begin")
	n = stdvar.shape[0]
	regr = RandomForestRegressor()
	regr.fit(X, y)
	yy_t = regr.predict(X_t)
	yy_t, y_t = yy_t.reshape(n, 6, -1), y_t.reshape(n, 6, -1)
	err = np.array([[error(qs[sku], yy_t[sku,dc,:], stdvar[sku,dc], y_t[sku,dc,:])\
		for dc in range(6)] for sku in range(n)], dtype=np.float32)
	err = np.sum(err)
	print("predict: %f"%err)
	
def model(X, y, X_t, y_t, stdvar, qs):# use 24 months to train and 2018.1 to test and output into test.csv
	print("train begin")
	n = stdvar.shape[0]
	regr = RandomForestRegressor()
	regr.fit(X, y)
	X_t = X_t.reshape(n,6,31,-1)
	yy_t = []
	for sku in range(n):
		for dc in range(6):
			for day in range(31):
				y = regr.predict(X_t[sku,dc,day,:].reshape(1,-1))
				yy_t.append(y)
				# use 'y' we predict as a feature for next 9 points
				for i in range(1,10):
					mday = day+i
					if(mday >= 31): break
					idx = 2*i - 1
					X_t[sku,dc,mday,idx] = y
	yy_t = np.array(yy_t)
	yy_t, y_t = yy_t.reshape(n, 6, -1), y_t.reshape(n, 6, -1)
	for sku in range(n):
		for dc in range(6):
			for day in range(31):
				yy_t[sku,dc,day] = qQuan(yy_t[sku,dc,day], stdvar[sku,dc], qs[sku])
	return yy_t.reshape(-1)
	
def models(num=10):# run model(1-10) (or less data to debug)
	ys = np.array([])
	for idx in range(num):
		X, y, X_t, y_t, stdvar, q = getData(idx)
		print("get data(X, y, X_t, y_t, var): "\
			+ str(X.shape) + str(y.shape) + str(X_t.shape) + str(y_t.shape)) + str(stdvar.shape)
		ys = np.append(ys, model(X, y, X_t, y_t, stdvar, q))
	print(ys.shape)
	output(ys.reshape(-1,1))
	
def output(ys):
	n = ys.shape[0]
	idxs = [[x+1,y,z+1] for z in range(n/6/31) for y in range(6) for x in range(31)]
	np.savetxt("test.csv", np.hstack((idxs, ys)), delimiter=",",\
		header="date,dc_id,item_sku_id,quantity", fmt="%d,%d,%d,%f", comments='')

def qQuan(y, stdvar, q):# quantile at q for y
	return norm(y,stdvar).ppf(q)
def relu(x):# used in the quantile error formula
	return max(x,0)
def error(q, yy, stdvar, y):# (int,[31],int,[31]) for a sku_dc
	ans = 0
	n = yy.shape[0]
	for idx in range(n):
		qy = qQuan(yy[idx], stdvar, q)
		ans += q*relu(y[idx]-qy) + (1-q)*relu(qy-y[idx])
	sum_y = np.sum(y)
	if(sum_y < 1e-3): sum_y = 1
	return ans / n / sum_y
	
def fileIdx(sku):
	return int((sku-1)/100)
def skuIdx(idxFile, idx):
	return idxFile * 100 + idx
def getMonthIdx():# month[x]:month[x+1] for the x'th month's data
	global monthIdxs
	monthIdxs = [31,28,31,30,31,30,31,31,30,31,30,31]
	monthIdxs = [0] + monthIdxs + monthIdxs
	monthIdxs[2] = 29
	for i in range(1, len(monthIdxs)):
		monthIdxs[i] = monthIdxs[i] + monthIdxs[i-1]
	
def calStdvar():# calculate stdvars for all (sku,dc,month)
	idx_data = np.array([[x,y] for x in range(1,1001) for y in range(6)])
	vars_data = []#np.array([],dtype=np.float32)
	for idx in range(10):
		data_ys = read(idx)[1]
		for i in range(100):
			#sku = skuIdx(idx, i)
			ys_sku = data_ys[i,:]
			ys_sku = ys_sku.reshape(6, -1)
			dcs = np.hstack([ys_sku[dc,:monthIdxs[24]] for dc in range(6)])
			for dc in range(6):
				ys_dc = ys_sku[dc]
				vars_dc = [np.std(ys_dc[:monthIdxs[24]])]
				for month in range(1,13):
					vars_dc.append(np.std(np.append(\
						ys_dc[monthIdxs[month-1]:monthIdxs[month]],\
						ys_dc[monthIdxs[month+12-1]:monthIdxs[month+12]])))
				vars_dc.append(np.std(dcs))
				vars_data.append(vars_dc)
	np.savetxt("stdvar.csv", np.hstack((idx_data, vars_data)), delimiter=",",\
		fmt="%d,%d,"+','.join(['%f' for x in range(14)]))

def getStdvars():# read stdvars for each(sku,dc,month) into global vars
	global vars
	tmp = np.loadtxt("stdvar.csv", dtype=np.str, delimiter=",")
	tmp = tmp[:, 2:].astype(np.float32)
	tmp = tmp.reshape(1000, 6, -1)
	vars = tmp[:,:,1]
	for sku in range(1000):
		for dc in range(6):
			for month in range(0,1):#13):
				if(vars[sku,dc,month] < 1e-3):
					if(tmp[sku,dc,0] < 1e-3):
						vars[sku,dc,month] = tmp[sku,dc,0]
					else:
						vars[sku,dc,month] = tmp[sku,dc,-1]
	#vars = vars.reshape(1000, 6)
	print("vars: "+str(vars.shape))
	return 

if __name__ == "__main__":
	getMonthIdx()
	#calStdvar()
	getVars()
	getQs()
	models()
	'''dates = read(0)[2]
	print(dates[5, monthIdxs[1]:monthIdxs[2]])
	print(dates[7, monthIdxs[12+2]:monthIdxs[12+3]])'''
	#stdvar()
