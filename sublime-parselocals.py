import sublime, sublime_plugin, re

class ParselocalsCommand(sublime_plugin.TextCommand):

	def init(self):
		self.active_class = 0
		self.active_line = 0
		self.active_method = 0
		self.datas = []

	def output(self, message):
		print(message)

	def run(self, view):
		# we initialize global variables
		self.init()
		sels = self.view.sel()
		# loop through selections
		for sel in sels:
			text = self.view.substr(sel)
			# parse each line
			for line in text.split('\n'):
				self.active_line = self.active_line + 1
				self.parse(line.strip())
		self.report()

	def parse(self, line):
		rule = "^(\&&)|(\*)"
		match = re.match(rule, line)
		if match:
			# this is a comment
			return

		rule = "(?i)(^DEFINE +CLASS)\s"
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

		rule = "(?i)^(PROTECTED )?(HIDDEN )?(PROC(?:EDURE)?)\s"
		match = re.search(rule, line)
		if match:
			# we get rid of procedure declaration
			string = re.sub(rule, "", line)
			# we create a new procedure object
			procObj = Procedure()
			# we save begin line number
			procObj.beginLine = self.active_line
			# we look for the name of the procedure
			match = re.match("\w*", string.strip())
			if match:
				procObj.name = match.group(0)
			# we push our procedure object and save the index
			self.datas.append(procObj)
			self.active_method = len(self.datas) - 1
			return

		rule = "(?i)^(PROTECTED )?(HIDDEN )?(FUNC(?:TION)?)\s"
		match = re.search(rule, line)
		if match:
			# we get rid of function declaration
			string = re.sub(rule, "", line)
			# we create a new function object
			funcObj = Function()
			# we save begin line number
			funcObj.beginLine = self.active_line
			# we look for the name of the function
			match = re.match("\w*", string.strip())
			if match:
				funcObj.name = match.group(0)
			# we push our function object and save the index
			self.datas.append(funcObj)
			self.active_method = len(self.datas) - 1
			return

		rule = "(?i)^ENDPROC"
		match = re.search(rule, line)
		if match:
			# we get our active procedure object
			procObj = self.datas[self.active_method]
			# we save end line number
			procObj.endLine = self.active_line
			return

		rule = "(?i)^ENDFUNC"
		match = re.search(rule, line)
		if match:
			# we get our active function object
			funcObj = self.datas[self.active_method]
			# we save end line number
			funcObj.endLine = self.active_line
			return

		rule = "(?i)^(?:L)?PARAMETERS"
		match = re.search(rule, line)
		if match:
			# we get our active method object
			methObj = self.datas[self.active_method]
			# we get rid of parameters declaration
			string = re.sub(rule, "", line)
			params = string.strip()
			# we split each parameter
			params = string.split(', ')
			for param in params:
				methObj.parameters.append(param.strip())
			return

		rule = "(?i)^LOCAL (?:ARRAY )?"
		match = re.search(rule, line)
		if match:
			# we get our active method object
			methObj = self.datas[self.active_method]
			# we get rid of local declaration
			string = re.sub(rule, "", line)
			variables = string.strip()
			# we split each variable
			variables = string.split(', ')
			for variable in variables:
				methObj.variables.append(variable.strip())
			return

	def report(self):
		classes = 0
		procs = 0
		funcs = 0
		for item in self.datas:
			itemClassName = item.__class__.__name__
			if itemClassName == "Class":
				classes = classes + 1
				self.output("@class : " + item.name)
				self.output("@parent : " + item.parent)
				self.output("@length : " + str(item.endLine - item.beginLine))
			elif itemClassName == "Procedure":
				procs = procs + 1
				self.output("@proc : " + item.name)
				self.output("@length : " + str(item.endLine - item.beginLine))
				self.output("@params : " + str(len(item.parameters)))
				self.output("@variables : " + str(len(item.variables)))
				for param in item.parameters:
					self.output("@param : " + param)
				for variable in item.variables:
					self.output("@variable : " + variable)
			elif itemClassName == "Function":
				funcs = funcs + 1
				self.output("@func : " + item.name)
				self.output("@length : " + str(item.endLine - item.beginLine))
				self.output("@params : " + str(len(item.parameters)))
				self.output("@variables : " + str(len(item.variables)))
				for param in item.parameters:
					self.output("@param : " + param)
				for variable in item.variables:
					self.output("@variable : " + variable)
		# self.output(str(classes) + " classes")
		# self.output(str(procs) + " procs")
		# self.output(str(funcs) + " funcs")
		# # self.output(((classes == 2) and (procs == 16) and (funcs == 0)))

class Class:
	def __init__(self):
		self.name = ""
		self.parent = ""
		self.beginLine = 0
		self.endLine = 0
		self.properties = []

class Procedure:
	def __init__(self):
		self.name = ""
		self.beginLine = 0
		self.endLine = 0
		self.variables = []
		self.parameters = []

class Function:
	def __init__(self):
		self.name = ""
		self.beginLine = 0
		self.endLine = 0
		self.variables = []
		self.parameters = []