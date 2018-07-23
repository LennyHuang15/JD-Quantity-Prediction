
idx_begin = 901; idx_end = 1001;
k0 = 10; k1 = 5; k2 = 30;

from datetime import date as Date
from datetime import timedelta

MaxLen = 800
NumSku = 1000
NumDc = 6
NumType = 6
DayBegin = Date(2016,1,1)
MaxDays = (Date(2018,2,1)-DayBegin).days
infoDict, saleDict, saleDict_avrday = [],[],[]
promDict, promBoostDict, saleDict_cate3, cate3Dict = {},{},{},{}
monthDict, weekdayDict = [],[]

def saleTable():
	file = open("sku_sales.csv", 'r', encoding='utf-8')
	lines = file.readlines()
	file.close()
	global saleDict, saleDict_avrday, saleDict_cate3
	saleDict = [[[(-1,-1,-1,-1) for i in range(MaxLen)] for dc in range(NumDc)] for sku in range(NumSku+1)]
	for line in lines[1:]:
		item_sku_id,dc_id,date,quantity,vendibility,original_price,discount = line.strip().split(',')
		date = [int(x) for x in date.split('-')]
		date = (Date(date[0],date[1],date[2])- DayBegin).days
		item_sku_id,dc_id,quantity,vendibility = int(item_sku_id),int(dc_id),float(quantity),float(vendibility)
		if(original_price == ''):	original_price = -1
		else:	original_price = float(original_price)
		if(discount == ''):	discount = 10
		else:	discount = float(discount)
		saleDict[item_sku_id][dc_id][date] = (int(quantity),int(vendibility),original_price,discount)
	saleDict_avrday = [[[-1,-1,-1] for i in range(NumDc+1)] for sku in range(NumSku+1)]
	for sku_id in range(1, NumSku+1):
		tot_vec = []
		cate3 = infoDict[sku_id][2]
		for dc_id in range(NumDc):
			vec = [x[:3] for x in saleDict[sku_id][dc_id] if x[0] != -1]
			tot_vec += vec
			if(len(vec) == 0):	saleDict_avrday[sku_id][dc_id] = [-1,-1,-1]; continue;# (avr_quan, num_vend, avr_ori_price)
			saleDict_avrday[sku_id][dc_id] = [sum([x[0] for x in vec])/len(vec), len([x[1] for x in vec if x[1] == 0]), -1]
			vec = [x[2] for x in vec if x[2] != -1]
			if(len(vec) != 0): saleDict_avrday[sku_id][dc_id][2] = sum(vec) / len(vec)
		if(len(tot_vec) == 0):	saleDict_avrday[sku_id][NumDc] = [-1,-1,-1]; continue;
		saleDict_avrday[sku_id][NumDc] = [sum([x[0] for x in tot_vec])/len(tot_vec), len([x[1] for x in tot_vec if x[1] == 0]),-1]
		tot_vec = [x[2] for x in tot_vec if x[2] != -1]
		if(len(tot_vec) != 0): saleDict_avrday[sku_id][NumDc][2] = sum(tot_vec) / len(tot_vec)
		saleDict_cate3[cate3][0] += len(tot_vec); saleDict_cate3[cate3][1] += sum(tot_vec);
	saleDict_cate3 = {key: val[1]/val[0] for key,val in saleDict_cate3.items() if val[0] != 0}
	print("sale table finished")
	
def infoTable():
	file = open("sku_info.csv", 'r', encoding='utf-8')
	lines = file.readlines()
	file.close()
	global infoDict, cate3Dict, saleDict_cate3
	infoDict = [-1]
	for line in lines[1:]:
		item_sku_id,first_cate_cd,second_cate_cd,third_cate_cd,brand_code = [int(x) for x in line.strip().split(',')]
		infoDict.append((first_cate_cd,second_cate_cd,third_cate_cd,brand_code))
		if(third_cate_cd not in cate3Dict): cate3Dict[third_cate_cd] = set()
		cate3Dict[third_cate_cd].add(item_sku_id)
		if(third_cate_cd not in saleDict_cate3): saleDict_cate3[third_cate_cd] = [0,0]
	print("info table finished")
	
def promTable():
	file = open("sku_prom.csv", 'r', encoding='utf-8')
	lines = file.readlines()
	file.close()
	file = open("sku_prom_testing_2018Jan.csv", 'r', encoding='utf-8')
	lines += file.readlines()[1:]
	file.close()
	global promDict, promBoostDict
	promDict = {}
	promBoostDict = {}# (after/before for sku, 3_cate)
	for line in lines[1:]:
		date,item_sku_id,item_third_cate_cd,promotion_type = line.strip().split(',')
		date = [int(x) for x in date.split('/')]
		date = Date(date[0],date[1],date[2])
		delta = (date - DayBegin).days
		item_sku_id,item_third_cate_cd,promotion_type = int(item_sku_id),int(item_third_cate_cd),int(promotion_type)
		if(item_third_cate_cd not in promDict):						promDict[item_third_cate_cd] = {}
		if(delta not in promDict[item_third_cate_cd]):				promDict[item_third_cate_cd][delta] = {}
		promDict[item_third_cate_cd][delta][item_sku_id] = promotion_type
		if(promotion_type not in promBoostDict):
			promBoostDict[promotion_type] = [[[0,0] for sku in range(NumSku+1)], {}]
		if(item_third_cate_cd not in promBoostDict[promotion_type][1]):
			promBoostDict[promotion_type][1][item_third_cate_cd] = [0,0]# cnt, sum
		if(item_sku_id != -999):
			for dc_id in range(NumDc):
				if saleDict[item_sku_id][dc_id][delta][0] != -1:
					promBoostDict[promotion_type][0][item_sku_id][0] +=1
					promBoostDict[promotion_type][0][item_sku_id][1] += saleDict[item_sku_id][dc_id][delta][0]
					promBoostDict[promotion_type][1][item_third_cate_cd][0] += 1;
					promBoostDict[promotion_type][1][item_third_cate_cd][1] += saleDict[item_sku_id][dc_id][delta][0]
		else:
			for sku in cate3Dict[item_third_cate_cd]:
				for dc_id in range(NumDc):
					if saleDict[sku][dc_id][delta][0] != -1:
						promBoostDict[promotion_type][0][sku][0] +=1
						promBoostDict[promotion_type][0][sku][1] += saleDict[sku][dc_id][delta][0]
						promBoostDict[promotion_type][1][item_third_cate_cd][0] += 1;
						promBoostDict[promotion_type][1][item_third_cate_cd][1] += saleDict[sku][dc_id][delta][0]
	for prom_type in promBoostDict:
		for sku in range(NumSku+1):
			if(promBoostDict[prom_type][0][sku][0] <= 0):	promBoostDict[prom_type][0][sku] = 1.0
			else:
				promBoostDict[prom_type][0][sku] = promBoostDict[prom_type][0][sku][1] \
					/ promBoostDict[prom_type][0][sku][0] / saleDict_avrday[sku][NumDc][0]
		for cate3 in promBoostDict[prom_type][1]:
			if(promBoostDict[prom_type][1][cate3][0] <= 0):	promBoostDict[prom_type][1][cate3] = 1.0
			else:
				promBoostDict[prom_type][1][cate3] = promBoostDict[prom_type][1][cate3][1] \
					/ promBoostDict[prom_type][1][cate3][0] / saleDict_cate3[cate3]
	print("prom table finished")
	
def dateTable():
	global monthDict, weekdayDict# [first_cate,second_cate,third_cate,brand,sku,sku-dc]
	monthDict = [[{} for type in range(NumType)] for month in range(12)]
	weekdayDict = [[{} for type in range(NumType)] for weekday in range(7)]
	for sku_id in range(1, NumSku+1):
		if(sku_id % 100 == 0):	print("dateTable %d in %d"%(sku_id, NumSku))
		for dc_id in range(NumDc):
			sku_dc = sku_id * 6 + dc_id
			first_cate,second_cate,third_cate,brand = infoDict[sku_id]
			types = [first_cate, second_cate, third_cate, brand, sku_id, sku_dc]
			for delta in range(MaxDays):
				date = DayBegin + timedelta(delta)
				month, weekday = date.month-1, date.weekday()
				month_dict, weekday_dict = monthDict[month], weekdayDict[weekday]
				quantity = saleDict[sku_id][dc_id][delta][0]
				for idx in range(NumType):
					type, mon_dict, wee_dict = types[idx], month_dict[idx], weekday_dict[idx]
					if(type not in mon_dict):	mon_dict[type] = [0,0]
					if(quantity != -1):	mon_dict[type][0] += 1;	mon_dict[type][1] += quantity
					if(type not in wee_dict):	wee_dict[type] = [0,0]
					if(quantity != -1):	wee_dict[type][0] += 1;	wee_dict[type][1] += quantity
	'''monthDict_avr = []
	for type_idx in range(NumType):
		keys = set()
		for mon_dict in monthDict:
			for key in mon_dict[type_idx].keys():
				keys.add(key)
		type_dict = {}
		for key in keys:
			vec = [monthDict[mon][type_idx][key] for mon in range(12) if key in monthDict[mon][type_idx]]
			type_dict[key] = sum([x[1] for x in vec]) / sum([x[0] for x in vec])
		monthDict_avr.append(type_dict)'''
	for mon_dict in monthDict:
		for type_idx in range(NumType):
			for key in mon_dict[type_idx]:
				num, s = mon_dict[type_idx][key]
				if(num == 0):	mon_dict[type_idx][key] = 0#monthDict_avr[type_idx][key]
				else:			mon_dict[type_idx][key] = s / num
	#monthDict = [[{key: val[1]/val[0] for key,val in type_dict.items() if val[0] != 0} \
	#	for type_dict in mon_dict] for mon_dict in monthDict]
	'''weekdayDict_avr = []
	for type_idx in range(NumType):
		keys = set()
		for wee_dict in weekdayDict:
			for key in wee_dict[type_idx].keys():
				keys.add(key)
		type_dict = {}
		for key in keys:
			vec = [weekdayDict[wee][type_idx][key] for wee in range(12) if key in weekdayDict[wee][type_idx]]
			type_dict[key] = sum([x[1] for x in vec]) / sum([x[0] for x in vec])
		weekdayDict_avr.append(type_dict)'''
	for wee_dict in weekdayDict:
		for type_idx in range(NumType):
			for key in wee_dict[type_idx]:
				num, s = wee_dict[type_idx][key]
				if(num == 0):	wee_dict[type_idx][key] = 0#weekdayDict_avr[type_idx][key]
				else:			wee_dict[type_idx][key] = s / num
	#weekdayDict = [[{key: val[1]/val[0] for key,val in type_dict.items() if val[0] != 0} \
	#	for type_dict in wee_dict]for wee_dict in weekdayDict]
	print("date table finished")
	
def featuringAll():
	from queue import Queue
	table = []
	for sku_id in range(idx_begin,idx_end):# NumSku+1):
		if(sku_id % 10 == 0):	print("sku %d"%sku_id)
		for dc_id in range(NumDc):
			tot_discount_k1 = {'cnt': 0, 'sum': .0,'q': Queue(k1)}
			tot_discount_k2 = {'cnt': 0, 'sum': .0,'q': Queue(k2)}
			tot_quan_k1 = {'cnt': 0, 'sum': .0,'q': Queue(k1)}
			tot_quan_k2 = {'cnt': 0, 'sum': .0,'q': Queue(k2)}
			for date in range(MaxDays):
				tmp = [sku_id, dc_id, DayBegin+timedelta(date)]
				table.append(tmp + featuring(sku_id, dc_id, date, tot_discount_k1, tot_discount_k2, tot_quan_k1, tot_quan_k2))
				#if(sku_id % 100 == 0 and dc_id == 0 and date == 40): print(table[-1])
	print("features got")
	return table
	
def featuring(sku_id, dc_id, date, tot_discount_k1, tot_discount_k2, tot_quan_k1, tot_quan_k2):
	result = []
	for delta in range(k0):	#(0, 2k0-1) -- k0*(quantity,vendibility) 
		dd = date - delta
		if(saleDict[sku_id][dc_id][dd][0] != -1):		result += saleDict[sku_id][dc_id][dd][:2]
		elif(saleDict_avrday[sku_id][dc_id][0] != -1):	result += [saleDict_avrday[sku_id][dc_id][0], 1]
		else:											result += [saleDict_avrday[sku_id][NumDc][0], 1]
	sale_info = saleDict[sku_id][dc_id][date]
	result += sale_info[2:]	#(2k0, 2k0+1) -- (original_price, discount)
	if(result[-2] == -1):
		if(saleDict_avrday[sku_id][dc_id][2] != -1):	result[-2] = saleDict_avrday[sku_id][dc_id][2]
		else:											result[-2] = saleDict_avrday[sku_id][NumDc][2]
	if(result[-1] == -1):	result[-1] = 10
	first_cate,second_cate,third_cate,brand_code = infoDict[sku_id]
	prom_type = -1
	if(third_cate in promDict and date in promDict[third_cate]):
		prom = promDict[third_cate][date]
		if(-999 in prom):		prom_type = prom[-999]
		elif(sku_id in prom):	prom_type = prom[sku_id]
	#result.append(prom_type)
	if(prom_type == -1):	result += [1,1]#(2k0+2) -- (prom-type for sku, cate3)
	else:					result += [promBoostDict[prom_type][0][sku_id], promBoostDict[prom_type][1][third_cate]]
	
	if(date < k1):#(2k0+3, 2k0+4) -- (k1-avr-discount, k1-avr-quantity)
		result.append(10)
		if(saleDict_avrday[sku_id][dc_id][0] != -1):	result.append(saleDict_avrday[sku_id][dc_id][0])
		else:											result.append(saleDict_avrday[sku_id][NumDc][0])
		#result += [10,-1]
	else:
		if(tot_discount_k1['cnt'] == 0):	result.append(10)
		else:								result.append(tot_discount_k1['sum'] / tot_discount_k1['cnt'])
		rem = tot_discount_k1['q'].get()
		if(rem != -1):	tot_discount_k1['cnt'] -= 1; tot_discount_k1['sum'] -= rem;
		
		if(tot_quan_k1['cnt'] == 0):		result.append(result[0])
		else:								result.append(tot_quan_k1['sum'] / tot_quan_k1['cnt'])
		rem = tot_quan_k1['q'].get()
		if(rem != -1):	tot_quan_k1['cnt'] -= 1; tot_quan_k1['sum'] -= rem;
	tmp = sale_info[3]; tot_discount_k1['q'].put(tmp)
	if(tmp != -1):	tot_discount_k1['cnt']+=1; tot_discount_k1['sum']+=tmp;
	tmp = sale_info[0]; tot_quan_k1['q'].put(tmp)
	if(tmp != -1):	tot_quan_k1['cnt']+=1; tot_quan_k1['sum']+=tmp;
	
	if(date < k2):#(2k0+5, 2k0+6) -- (k2-avr-discount, k2-avr-quantity)
		result.append(10)
		if(saleDict_avrday[sku_id][dc_id][0] != -1):	result.append(saleDict_avrday[sku_id][dc_id][0])
		else:											result.append(saleDict_avrday[sku_id][NumDc][0])
	#if(date < k2):	result += [10,-1]	
	else:
		if(tot_discount_k2['cnt'] == 0):	result.append(10)
		else:								result.append(tot_discount_k2['sum'] / tot_discount_k2['cnt'])
		rem = tot_discount_k2['q'].get()
		if(rem != -1):	tot_discount_k2['cnt'] -= 1; tot_discount_k2['sum'] -= rem;
		
		if(tot_quan_k2['cnt'] == 0):		result.append(result[0])
		else:								result.append(tot_quan_k2['sum'] / tot_quan_k2['cnt'])
		rem = tot_quan_k2['q'].get()
		if(rem != -1):	tot_quan_k2['cnt'] -= 1; tot_quan_k2['sum'] -= rem;
	tmp = sale_info[3]; tot_discount_k2['q'].put(tmp)
	if(tmp != -1):	tot_discount_k2['cnt']+=1; tot_discount_k2['sum']+=tmp;
	tmp = sale_info[0]; tot_quan_k2['q'].put(tmp)
	if(tmp != -1):	tot_quan_k2['cnt']+=1; tot_quan_k2['sum']+=tmp;
	
	date = DayBegin + timedelta(date)
	sku_dc = sku_id * 6 + dc_id
	types = [first_cate, second_cate, third_cate, brand_code, sku_id, sku_dc]
	result += [monthDict[date.month-1][idx][types[idx]] for idx in range(NumType)]		#(2k0+7, 2k0+12) -- (types month average)
	result += [weekdayDict[date.weekday()][idx][types[idx]] for idx in range(NumType)]	#(2k0+3, 2k0+18) -- (types weekday average)
	return result
	
def output(table):
	print("table: (%d,%d)"%(len(table), len(table[0])))
	content = "sku_id,dc_id,date," + ','.join([str(-x)+"_quantity," + str(-x)+"_vendibility" for x in range(k0)]) + ","
	content += "original_price,discount,prom_sku,prom_cate3,"
	content += "k1days-avr-discount,k1days-avr-quantity,k2days-avr-discount,k2days-avr-quantity,"
	content += ",".join([("month-avr-quantity-"+x) for x in ["first_cate,second_cate,third_cate,brand_code,sku_id,sku_dc"]]) + ","
	content += ",".join([("weekday-avr-quantity-"+x) for x in ["first_cate,second_cate,third_cate,brand_code,sku_id,sku_dc"]]) + "\n"
	#content = ""
	cnt = 0; sku = 0;
	for record in table:
		content += ','.join([str(x) for x in record]) + '\n'
		cnt += 1
		if(cnt % (NumDc*MaxDays) == 0):
			sku += 1
			if(sku % 10 == 0):
				file = open("features.csv", 'a', encoding='utf-8')
				file.write(content); file.close();
				content = ""
			print("output %d"%(sku+idx_begin))
	file = open("features.csv", 'a', encoding='utf-8')
	file.write(content)
	file.close()
	
def stat():
	from numpy import mean, std
	statDict = [[[] for dc in range(NumDc+1)] for sku in range(NumSku+1)]
	content = ""
	for sku in range(1,NumSku+1):
		tot_vec = []
		for dc in range(NumDc):
			vec = [x[0] for x in saleDict[sku][dc] if x[0] != -1]
			tot_vec += vec
			if(len(vec) == 0):	statDict[sku][dc] = (0,0)
			else:				statDict[sku][dc] = (mean(vec),std(vec))
			content += str(sku)+","+str(dc)+","+",".join([str(x) for x in statDict[sku][dc]])+"\n"
		if(len(tot_vec) == 0):	statDict[sku][NumDc] = (0,0)
		else:					statDict[sku][NumDc] = (mean(tot_vec),std(tot_vec))
		content += str(sku)+",-1,"+",".join([str(x) for x in statDict[sku][NumDc]])+"\n"
	
	file = open("stat.csv", "w", encoding="utf-8")
	file.write("sku,dc,mean,stdvar\n")
	file.write(content)
	file.close()

if __name__ == "__main__":
	infoTable()
	saleTable()
	promTable()
	#stat()
	dateTable()
	
	output(featuringAll())
	

