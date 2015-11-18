#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
№10. 
Входной язык содержит операторы цикла типа 
for (…; …; …) do done
разделенные символом ; (точка с запятой).
Операторы цикла содержат идентификаторы,
знаки сравнения <, >, =,
римские числа (Римскими числами считать X, V и I)
знак присваивания (:=).
комментарий будет (многострочный: Начало '#*' конец: '*#', однострочный ##)
"""
import sys, string, re, tabulate

class switch(object):
	def __init__(self, value):
		self.value = value
		self.fall = False

	def __iter__(self):
		"""Return the match method once, then stop"""
		yield self.match
		raise StopIteration

	def match(self, *args):
		"""Indicate whether or not to enter a case suite"""
		#print self.value, args
		if self.fall or not args:
			return False
		elif isinstance(args[0], re._pattern_type):
			#print args[0].pattern
			if re.match(args[0], self.value):
				#print "match"
				self.fall = True
				return True
			else:
				#print "not match"
				return False
		elif self.value in args: # changed for v1.5, see below
			self.fall = True
			return True
		else:
			return False

class Compiler:

	Table = []
	
	debug = False
	
	fileName = None

	isVar = ""

	isComment = False
	isMultiLineComment = False
	isCommentStarting = False
	isCommentEnding = False
	
	isAssignment = False

	def __init__(self, filename):
		self.fileName = filename


	def LexicalAnalyzerStart(self):
		inputFile = open(self.fileName,'r')
		lines = inputFile.readlines()
		inputFile.close()
		lineNumber = 0
		for line in lines:
			line = line.strip()
			charNumber = 0
			for char in line:
				kchar = filter(lambda x: x in string.printable, char)
				if kchar:
					try:
						self._updateState(char)
					except Exception as ex:
						firpart = line[0:charNumber]
						secpart = line[charNumber:]
						errorMessage = "{} at line #{} at '{}^{}'".format(ex.message,lineNumber,firpart,secpart)
						raise Exception(errorMessage)
				charNumber += 1
			lineNumber += 1
			self._updateState("return")

	def lprint(self, string):
		if self.debug:
			print string

	def _nexty(self, char):
		if self.isCommentStarting:
			raise Exception("Wrong starting of comment")
		if self.isCommentEnding:
			self.isCommentEnding = False
		if self.isAssignment and char != "=":
			raise Exception("Wrong assigment sign ':'")
		if self.isComment or self.isMultiLineComment:
			if char:
				self.lprint("Char is comment: '{}'".format(char))
				return True

	def _AnalyzeVar(self):
		if self.isVar:
			self.lprint("Found some var {}".format(self.isVar))
			vartype = "variable"
			if re.match('[XIV*]',self.isVar):
				vartype = "roman"
			elif self.isVar in ("for", "do" , "done"):
				vartype = "reserved"
			self.Table.append([self.isVar, vartype])
			self.isVar = ""
			


	def _appendDelimiter(self, char):
		if len(self.Table) > 0:
			if char == " " and self.Table[-1][0] != " ":
				self.Table.append([char, 'delimiter'])
			else:
				self.Table.append([char, 'delimiter'])

	def _updateState(self, char):
		for case in switch(char):
			if case('#'):
				if self.isCommentEnding:
					self.isCommentEnding = False
					self.isMultiLineComment = False
					self.lprint("#002 ending comment")
					break
				if self.isCommentStarting:
					self.isCommentStarting = False
					self.isComment = True
					self.lprint("#003 starting oneline comment")
					break
				if self._nexty(char): break
				self._AnalyzeVar()
				self.isCommentStarting = True
				break
			if case('*'):
				if self.isMultiLineComment:
					self.isCommentEnding = True
					break
				if self.isCommentStarting:
					self.isCommentStarting = False
					self.isMultiLineComment = True
					self.lprint("#001 starting comment")
					break
				if self._nexty(char): break
				self.Table.append(["*", "operator"])
				break
			if case(re.compile("[\+\-\/]")):
				if self._nexty(char): break
				self._AnalyzeVar()
				self.Table.append([char, "operator"])
				break
			if case('return'):
				if self.isComment:
					self.lprint("#004 end oneline comment by return")
					self.isComment = False
				self._AnalyzeVar()
				if self._nexty(char): break
				self.lprint("Return")
				self._appendDelimiter("return")
				break
			if case(':'):
				if self._nexty(char): break
				self._AnalyzeVar()
				self.lprint("#006 : assingment first part")
				if not self.isAssignment:
					self.isAssignment = True
				else:
					raise Exception("Wrong start of identifier")
				break
			if case('='):
				if self._nexty(char): break
				self.lprint("#007 = second part of assigment")
				if self.isAssignment:
					self.isAssignment = False
					self.Table.append([":=", "assigment"])
				else:
					self.isAssignment = False
					self.Table.append(["=", "equality"])
				break
			if case(';'):
				if self._nexty(char): break
				self._AnalyzeVar()
				self.lprint("#005 ; delimeter")
				self._appendDelimiter(";")
				break
			if case(re.compile('[\(\)]')):
				if self._nexty(char): break
				self._AnalyzeVar()
				if char == "(":
					self.Table.append(["(", "bracket"])
				else:
					self.Table.append([")", "bracket"])
				break
			if case(re.compile('[0-9]')):
				if self._nexty(char): break
				if self.isVar:
					self.isVar += char
					break
				else:
					raise Exception("Wrong start of identifier")
			if case(re.compile('[a-zA-Z_]')):
				if self._nexty(char): break
				self.isVar += char
				break
			if case(' '):
				if self._nexty(char): break
				self._AnalyzeVar()
				break
			if case(): # default, could also just omit condition or 'if True'
				if self._nexty(char): break
				self._AnalyzeVar()
				self.lprint("other char {}".format(char))
				break

compiler = Compiler("code.txt")
compiler.LexicalAnalyzerStart()
print tabulate.tabulate(compiler.Table)
	#print "'{}'\t:\t{}".format(line[0],line[1])
