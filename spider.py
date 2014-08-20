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
import sched,time


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


def print_progress_bar(total_url_num,seen_url_num):
	schedule = sched.scheduler(time.time, time.sleep)

	def preform_cmd(total,seen):
		schedule.enter(1, 0, preform_cmd, (total,seen))
		rate = seen/total * 100
		print "The spider had scaned %s" % rate

	def timming_exec(total,seen):
		schedule.enter(1, 0, preform_cmd, (total,seen))
		schedule.run()

	timming_exec(total_url_num, seen_url_num)


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

	return path+sep

class Retriever(object):
	def __init__(self,url,path):
		self.url = url
		self.file = self.filename(url,path)

	def filename(self,url,path):
		urlpath = urlparse(url,"http",0)
		paths = urlpath[2].split("/")
		fileName = paths[-1]

		if fileName == '':
			path += replace(str(urlpath[2][1:]), "/", os.sep)
			fileName = "index.html"

		else:
			path += replace(str(urlpath[2][1:-len(fileName)]), "/", os.sep)
			if "#" in fileName:
				fileName = fileName.split("#")[0]


		if not exists(path):
			makedirs(path)

		return path+fileName

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
	count = 1

	def __init__(self,url,deep):
		self.q = [url]
		self.seen = []
		self.dom = urlparse(url)[1]
		self.deep = deep


	def filterLink(self,link):
		if self.deep == 0:
			return link
		else:
			deep = 2+int(self.deep)
			count = link.count("/")

			if 2< count <= deep:
				return link
			else:
				return ""

	def getPage(self,url,path):
		r = Retriever(url, path)
		retval = str(r.download())
		if retval[0] == '*':
			return

		

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
					if self.filterLink(link) == "":
						continue
					else:
						#print link
						Crawler.count += 1
						self.q.append(link)

	def go(self,path):
		print_progress_bar(len(self.q), len(self.seen))
		while self.q:
			url = self.q.pop()
			self.getPage(url, path)

		print "The total of page is ",Crawler.count
		print "ALL Done!!"



def main():
	if len(argv) > 1:
		DEEP = 0
		opts,args = getopt.getopt(argv[1:],"u:v:d:",["url=","deep="])
		for opt,value in opts:
			if opt == '-u' or opt == 'url':
				URL = value

			if opt == '-d' or opt == 'deep':
				DEEP = value

		spider = Crawler(URL,DEEP)
		PATH =savePath(URL)
		spider.go(PATH)

	else:
		sys.exit()

if __name__ == '__main__':
	main()