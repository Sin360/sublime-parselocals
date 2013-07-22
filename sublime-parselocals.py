import sublime, sublime_plugin, re

class ParselocalsCommand(sublime_plugin.TextCommand):
	
	active_class = 0
	active_line = 0
	active_method = 0
	datas = []

	def output(self, message):
		print(message)

	def run(self, view):
		sels = self.view.sel()
		# loop through selections
		for sel in sels:
			text = self.view.substr(sel)
			# parse each line
			for line in text.split('\n'):
				self.active_line = self.active_line + 1
				self.parse(line)
		for item in self.datas:
			itemClassName = item.__class__.__name__
			self.output("##############################")
			if itemClassName == "Class":
				self.output("@class : " + item.name)
				self.output("@parent : " + item.parent)
				self.output("@length : " + str(item.endLine - item.beginLine))
			elif itemClassName == "Procedure":
				self.output("@proc : " + item.name)
				self.output("@length : " + str(item.endLine - item.beginLine))

	def parse(self, line):
		rule = "(?i)^DEFINE CLASS\s"
		match = re.match(rule, line)
		if match:
			# we get rid of class declaration
			string = re.sub(rule, "", line)
			# we create a new class object
			classObj = Class()
			# we save begin line number
			classObj.beginLine = self.active_line
			# we look for the name of the class
			match = re.match("\w*", string)
			if match:
				classObj.name = match.group(0)
				# we look for parent
				match = re.search("\w*$", string)
				if match:
					classObj.parent = match.group(0)
			# we push our class object and save the index
			self.datas.append(classObj)
			self.active_class = len(self.datas) - 1
			return

		rule = "(?i)^ENDDEFINE$"
		match = re.match(rule, line)
		if match:
			# we get our active class object
			classObj = self.datas[self.active_class]
			# we save end line number
			classObj.endLine = self.active_line
			return

		rule = "(?i)^PROCEDURE\s"
		match = re.match(rule, line)
		if match:
			# we get rid of procedure declaration
			string = re.sub(rule, "", line)
			# we create a new procedure object
			procObj = Procedure()
			# we save begin line number
			procObj.beginLine = self.active_line
			# we look for the name of the procedure
			match = re.match("\w*", string)
			if match:
				procObj.name = match.group(0)
			# we push our procedure object and save the index
			self.datas.append(procObj)
			self.active_method = len(self.datas) - 1
			return

		rule = "(?i)^ENDPROC$"
		match = re.match(rule, line)
		if match:
			# we get our active procedure object
			procObj = self.datas[self.active_method]
			# we save end line number
			procObj.endLine = self.active_line
			return

class Class:
	name = ""
	parent = ""
	beginLine = 0
	endLine = 0
	properties = []

class Procedure:
	name = ""
	beginLine = 0
	endLine = 0
	parameters = []