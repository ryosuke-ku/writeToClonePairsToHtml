import urllib.request as req
from bs4 import BeautifulSoup as bs4
from collections import defaultdict
import collections
import re
import csv
import os

ProjectName = 'maven'

url = "file:///C:/Users/ryosuke-ku/Desktop/NiCad-5.1/systems/" + ProjectName + "_functions-blind-clones/" + ProjectName + "_functions-blind-clones-0.30.xml"

projectName = 'maven'
t ='t2'
# os.mkdir('NicadOutputFile_' + t + '_' + projectName)
res = req.urlopen(url)
#詳しくは省略、上のXMLが返ってくるものと思ってください

startlist = [] #コード片の開始行番号を格納
endlist = [] #コード片の修了行番号を格納
startdic = defaultdict(list) #コード片の開始行番号を格納
enddic = defaultdict(list) #コード片の修了行番号を格納
startdicPath = defaultdict(list) #コード片の開始行番号を格納
enddicPath = defaultdict(list) #コード片の修了行番号を格納

allpathlist = []
NotestPath =[] #ファイルパスを格納(同じファイルパスを区別しない)
numNotestPath =[] #ファイルパスを格納(同じファイルパスを区別する)
soup = bs4(res,'lxml-xml')
data = defaultdict(list)
delTestdata = defaultdict(list)
numdelTestdata = defaultdict(list)

filePaths = soup.find('clones')
count = 0
cnt = 1
num = 1
for filePath in filePaths.find_all(['clone','source']):
	 
	if filePath.name == 'clone':
		count+=1
		key = "clone pairs:" + str(count) + ":"+ filePath.get('similarity') + "%"
		# print(key)
	if key and filePath.name == 'source':
		path = filePath.get('file') #例 systems/apache_ant/ant/src/main/org/apache/tools/ant/AntClassLoader.java
		path = path[8:] #例 systems/apache_ant/ant/src/main/org/apache/tools/ant/AntClassLoader.java →　apache_ant/ant/src/main/org/apache/tools/ant/AntClassLoader.java	
		allpathlist.append(path)
		data[key].append(path)
		cnt+=1

		cutFtestpath = path[-9:] #pathの文字列の末尾から９文字を取得 Test.java かどうかを判定に使う
		cutBtestpathnum = path.rfind("/")
		cutBtestpath = path[cutBtestpathnum + 1:]
		if cutFtestpath == 'Test.java':
			pass
		elif cutBtestpath[:4] == 'Test':
			pass
		else:
			registerdPath = str(num) + ':' + path # 3:apache_ant/ant/src/main/org/apache/tools/ant/AntClassLoader.java 同じファイルパスを区別するため
			NotestPath.append(path)
			numNotestPath.append(registerdPath)
			startline = filePath.get('startline') #コード片の開始行番号を取得
			endline = filePath.get('endline') #コード片の修了行番号を取得
			startlist.append(startline)
			endlist.append(endline)
			startdicPath[registerdPath].append(startline)
			enddicPath[registerdPath].append(endline)
			startdic[key].append(startline)
			enddic[key].append(endline)
			delTestdata[key].append(path)
			numdelTestdata[key].append(registerdPath)
			num += 1


production = open(r'C:\Users\ryosuke-ku\Desktop\Path\newProductionPath.txt','r',encoding="utf-8_sig")
ProductionPath = production.readlines()
PPath = [Pline.replace('\n', '') for Pline in ProductionPath]
production.close()

Test = open(r'C:\Users\ryosuke-ku\Desktop\Path\newTestPath.txt','r',encoding="utf-8_sig")
TestPath = Test.readlines()
TPath = [Tline.replace('\n', '') for Tline in TestPath]
Test.close()


dic = dict(zip(PPath,TPath))
data2 = defaultdict(list)



delPairs = []
for t in numdelTestdata:
	for h in numdelTestdata[t]:
		if len(numdelTestdata[t]) != 2: # クローンペアが２つのコード片からならないものを取得する
			delPairs.append(t)
	

for pairs in delPairs:
	startkey = numdelTestdata[pairs]
	startdicPath.pop(startkey[0]) # プロダクションコード片とテストコード片からなるクローンペアのプロダクションコードの開始行を削除
	endkey = numdelTestdata[pairs]
	enddicPath.pop(endkey[0]) # プロダクションコード片とテストコード片からなるクローンペアのプロダクションコードの修了行を削除
	# print(numdelTestdata[pairs])
	numdelTestdata.pop(pairs)

# print(numdelTestdata)
# print(len(numdelTestdata))


onlyhasTestdata = defaultdict(list)
onlyhasTestPdata = defaultdict(list)

for i in numdelTestdata:
	for j in numdelTestdata[i]:
		delnum = re.sub(r".*?:", "", j)
		path = dic.get(delnum)
		data2[i].append(path)
		if path is not None:
			onlyhasTestdata[i].append(path)
			onlyhasTestPdata[i].append(j)


nt = 0
t1 = 0
t2 = 0
has2noMap = defaultdict(list)
no2hasMap =defaultdict(list)

for u in numdelTestdata:
	p1 = numdelTestdata[u][0]
	c1 = re.sub(r".*?:", "", p1)
	path1 = dic.get(c1)

	p2 = numdelTestdata[u][1]
	c2 = re.sub(r".*?:", "", p2)
	path2 =dic.get(c2)

	if path1 is not None and path2 is None:
		# print(u)
		# print('has test : ' + c1)
		# print('No test  : ' + c2)
		has2noMap[p1].append(u + '_t1')
		no2hasMap[u + '_t1'].append(p2)
		cp = has2noMap[p1]
		notestpath = no2hasMap[cp[0]]
		# print(notestpath)
		# print('--------------------------------------------------------------------------------------------------------------------------------------')
		t1 += 1
	if path1 is None and path2 is not None:
		has2noMap[p2].append(u + '_t1')
		no2hasMap[u + '_t1'].append(p1)
		cp = has2noMap[p2]
		notestpath = no2hasMap[cp[0]]
		t1 += 1
	if path1 is not None and path2 is not None:
		t2 += 1
	if path1 is None and path2 is None:
		nt += 1

print('nt : ' + str(nt))
print('t1 : ' + str(t1))
print('t2 : ' + str(t2))
print('total : ' + str(nt + t1 +t2))

def OutputNicadt1File():
	
	t1 = 0
	t1keylist = []
	for h in onlyhasTestPdata:
		if len(onlyhasTestPdata[h]) == 1:
			t1keylist.append(h)
			t1 += 1

	t1mapdic = defaultdict(list)
	t1mapTestcodedic = defaultdict(list)
	for u in t1keylist:
		path = onlyhasTestPdata[u]
		# print(path)
		t1mapdic[u].append(path)
		testpath = onlyhasTestdata[u]
		t1mapTestcodedic[u].append(testpath)

	# print(t1mapTestcodedic)
	print(len(t1mapTestcodedic))


	Slinelist =[]
	Elinelist =[]
	for k in t1mapdic:
		for g in t1mapdic[k]:
			# print(g[0])
			Sline = startdicPath[g[0]]
			Slinelist.append(Sline)
			Eline = enddicPath[g[0]]
			Elinelist.append(Eline)


	num = 0
	filenum = 1
	for k in t1mapdic:
		path = t1mapdic[k][0][0]
		cp = has2noMap[path]
		notestpath = no2hasMap[cp[0]]


		editpath = re.sub(r".*?:", "", path)
		editnotestpath = re.sub(r".*?:", "", notestpath[0])

		# print(editpath)
		
		file = open('NicadOutputFile_t1_' + projectName + '/Nicad_t1_' + projectName + str(filenum) + '.java','w') # Nicad_3.javaのファイルを開く
		f = open("C:/Users/ryosuke-ku/Desktop/NiCad-5.1/systems/" + editpath, "r", encoding="utf-8")
		lines2 = f.readlines() # 1行毎にファイル終端まで全て読む(改行文字も含まれる)
		f.close()


		startline = int(Slinelist[num][0])-1
		endline = int(Elinelist[num][0])
		num +=1

		file.write('//C:/Users/ryosuke-ku/Desktop/NiCad-5.1/systems/' + editnotestpath + '\n')
		file.write('//C:/Users/ryosuke-ku/Desktop/NiCad-5.1/systems/' + editpath + '\n')
		file.write('// ' + k + '\n')
		file.write('// ' + path + '\n')
		file.write('\n')
		file.write('public class Nicad_t1_' + projectName + str(filenum) + '\n')
		file.write('{' + '\n')
		for x in range(startline,endline):
			# print(lines2[x].replace('\n', ''))
			file.write(lines2[x].replace('\n', '') + '\n')
		
		file.write('}')
		filenum += 1

	TestPathfile = open('TestPath_t1_' + projectName + '.txt','w') # Nicad_3.javaのファイルを開く

	for s in t1mapTestcodedic:
		TestPathfile.write(t1mapTestcodedic[s][0][0] + '\n')

# OutputNicadt1File()




def OutputNicadt2File():
	t2 = 0
	t2keylist = []
	for h in onlyhasTestPdata:
		if len(onlyhasTestPdata[h]) == 2:
			t2keylist.append(h)
			t2 += 1

	t2mapdic = defaultdict(list)
	t2mapTestcodedic = defaultdict(list)
	for u in t2keylist:
		path = onlyhasTestPdata[u]
		t2mapdic[u].append(path[0])
		t2mapdic[u].append(path[1])
		testpath = onlyhasTestdata[u]
		t2mapTestcodedic[u].append(testpath[0])
		t2mapTestcodedic[u].append(testpath[1])

	# print(t2mapdic)
	# print(t1mapTestcodedic)
	print(len(t2mapTestcodedic))


	Slinelist =[]
	Elinelist =[]
	for k in t2mapdic:
		for g in t2mapdic[k]:
			# print(g)
			Sline = startdicPath[g]
			Slinelist.append(Sline)
			Eline = enddicPath[g]
			Elinelist.append(Eline)
			# print(g + ':' + str(Sline[0]) + ',' + str(Eline[0]))
	# print(Slinelist)
	# print(t2mapdic)
	
	file = open('NicadOutputFile_t2.html','w') # Nicad_3.javaのファイルを開く
	file.write('<html>' + '\n')
	file.write('<head>' + '\n')
	file.write('<style type="text/css">' + '\n')
	file.write('body {font-family:Arial}' + '\n')
	file.write('table {background-color:white; border:0px solid white; width:95%; margin-left:auto; margin-right: auto}' + '\n')
	file.write('td {background-color:#ff7e75; padding:16px; border:4px solid white}' + '\n')
	file.write('pre {background-color:white; padding:4px}' + '\n')
	file.write('</style>' + '\n')
	file.write('<title>NiCad Clone Report</title>' + '\n')
	file.write('<head>' + '\n')
	file.write('<body>' + '\n')
	file.write('<h2>NiCad Clone Report</h2>' + '\n')
	file.write('System: ' + projectName + '\n')

	num = 0
	filenum = 1
	cc = 0
	for k in t2mapdic:
		# print(k)
		cc += 1
		# os.mkdir('NicadOutputFile_t2_' + projectName + '/Clone Pairs ' + str(cc))
		file.write('<table border="1" width="500" cellspacing="0" cellpadding="5" bordercolor="#333333">' + '\n')
		# file.write('<tr>' + '\n')
		# file.write('<th bgcolor="#bebebe" width="250">コードフラグメント1</th>' + '\n')
		# file.write('<th bgcolor="#bebebe" width="250">コードフラグメント2</th>' + '\n')
		# file.write('</tr>' + '\n')
		file.write('<h3>' + k  + '</h3>' + '\n')
		file.write('<tr>' + '\n')
		for l in t2mapdic[k]:
			# path = t2mapdic[k][0][0]
			# print(path)
			editpath = re.sub(r".*?:", "", l)
			print(editpath)

			
			f = open("C:/Users/ryosuke-ku/Desktop/NiCad-5.1/systems/" + editpath, "r", encoding="utf-8")
			lines2 = f.readlines() # 1行毎にファイル終端まで全て読む(改行文字も含まれる)
			f.close()

			startline = int(Slinelist[num][0])-1
			endline = int(Elinelist[num][0])
			num +=1

			# file.write('//' + k + ':' + 's' +str(startline) + ':' + 'e' + str(endline) + '\n')
			# file.write('//' + l + '\n')
			# file.write('\n')
			# file.write('public class Nicad_t2_' + projectName + str(filenum) + '\n')
			# file.write('{' + '\n')

			file.write('<td>' + '\n')
			file.write(l + '\n')
			file.write("<pre>" + '\n')
			for x in range(startline,endline):
				try:
					print(lines2[x].replace('\n', ''))
					file.write(lines2[x].replace('\n', '') + '\n')
				except UnicodeEncodeError:
					pass
			file.write("</pre>" + '\n')
			file.write('</td>' + '\n')
			file.write('</tr>' + '\n')
			# file.write('}')
			filenum += 1
		
		file.write('</table>' + '\n')

	TestPathfile = open('TestPath_t2_' + projectName + '.txt','w') # Nicad_3.javaのファイルを開く

	for s in t2mapTestcodedic:
		for test in t2mapTestcodedic[s]:
			TestPathfile.write(test + '\n')

OutputNicadt2File()


def ClassifyClonePairs():
	# print(data2)
	# print(len(data2))
	p = 0
	q = 0
	r = 0
	for k in data2:
		n = 0
		for j in data2[k]:
			# print(j)
			if j is not None:
				n += 1
		if n == 0:
			p += 1
		if n == 1:
			q += 1
		if n == 2:
			r += 1

	print('テストコードが見つからないクローンペア : ' + str(p) + '(' + str(round(p/(p+q+r)*100,1)) + ')')
	print('どちらか片方のコードフラグメントにテストコードが存在する : ' + str(q) + '(' + str(round(q/(p+q+r)*100,1)) + ')')
	print('両方のコードフラグメントにテストコードが存在するクローンペア : ' + str(r) + '(' + str(round(r/(p+q+r)*100,1)) + ')')
	print('合計 : '+ str(p+q+r))


ClassifyClonePairs()