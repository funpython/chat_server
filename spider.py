#!/usr/bin/env python
#coding:utf-8

from sys import argv
from os import sep,rmdir,walk,makedirs
from urlparse import urlparse
from os.path import isdir,exists
from htmllib import HTMLParser
from urllib import urlretrieve
from formatter import DumbWriter,AbstractFormatter
from string import replace,find,lower
from urlparse import urlparse,urljoin
from cStringIO import StringIO
import re,os,getopt,sys


''''
opt,args = getopt.getopt(argv[1:],"h:l:v:o:",["help","ip=","port"])
for o,v in opt:
	print o+" "+v
'''

def delDirectory(path):
	try:
		for root,dirs,files in walk(path,topdown=False):
			for name in files:
				os.remove(os.path.join(root,name))

			for name in dirs:
				rmdir(os.path.join(root,name))
		rmdir(path)
	except Exception,e:
		print e




def savePath(url):
	#保存文件的路径为程序的路径，文件夹名为域名
	getDomain = urlparse(url,"http",0)
	dirName = replace(getDomain[1], ".", "_")
	ospath = os.getcwd()
	path = ospath+sep+dirName
	if exists(path):
		if isdir(path):
			delDirectory(path)
	else:
		makedirs(path)

	return path

class Retriever(object):
	def __init__(self,url,path):
		self.url = url
		self.file = self.filename(url,path)

	def filename(self,url,path):
		urlpath = urlparse(url,"http",0)
		paths = str(urlpath[2].split("/"))
		fileName = paths[-1]
		if fileName:
			fileName = "index.html"
		if "#" in fileName:
			fileName = fileName.split("#")[0]

		path += replace(str(urlpath[2][:-len(fileName)]), "/", sep)
		if not exists(path):
			makedirs(path)

		return path+sep+fileName

	def download(self):
		try:
			if not exists(self.file):
				retval = urlretrieve(self.url,self.file)
		except IOError:
			retval =('*** Error:Invaild url "%s"' % self.url)
			return retval

	def parseAndGetLinks(self):
		self.parser = HTMLParser(AbstractFormatter(DumbWriter(StringIO())))
		self.parser.feed(open(self.file).read())
		self.parser.close()
		return self.parser.anchorlist

class Crawler(object):
	count = 0 

	def __init__(self,url):
		self.q = [url]
		self.seen = []
		self.dom = urlparse(url)[1]


	def getPage(self,url,path):
		print path 
		r = Retriever(url, path)
		retval = str(r.download())
		if retval[0] == '*':
			return

		Crawler.count += 1

		self.seen.append(url)

		links = r.parseAndGetLinks()
		for link in links:
			if link[:4] != "http" and find(link,"://") == -1:
				link = urljoin(url, link)

			if find(lower(link),'mailto:') != -1:
				print '....discarded,mailto link'
				continue

			if link not in self.seen:
				if find (link,self.dom) != -1 and link not in self.q:
					self.q.append(link)

	def go(self,path):
		while self.q:
			url = self.q.pop()
			self.getPage(url, path)

		print "ALL Done!!"



def main():
	if len(argv) > 1:
		opts,args = getopt.getopt(argv[1:],"u:v:",["url=","level="])
		for opt,value in opts:
			if opt == '-u':
				spider = Crawler(value)
				path = savePath(value)
				spider.go(path)

	else:
		sys.exit()

if __name__ == '__main__':
	main()