import re, shlex

__all__ = ['ApacheParser', 'ApacheRoot', 'ApacheSection', 'ApacheStatement', 'ApacheComment', 'ApacheEmptyLine', 'ApacheItem', 'ApacheItemList', 'configBuilder']

if not hasattr(shlex, 'quote'):
	if not hasattr(re, 'ASCII'):
		setattr(re, 'ASCII', 256)
	_find_unsafe = re.compile(r'[^\w@%+=:,./-]', re.ASCII).search

	def quote(s):
		"""Return a shell-escaped version of the string *s*."""
		if not s:
			return "''"
		if _find_unsafe(s) is None:
			return s

		# use single quotes, and put single quotes into double quotes
		# the string $'b is then quoted as '$'"'"'b'
		return "'" + s.replace("'", "'\"'\"'") + "'"
	setattr(shlex, 'quote', quote)

match_comment = re.compile(br'^\s*#\s*(.*)$')
match_statement = re.compile(br'^\s*[^<\s]+\s*.*$')
match_section_start = re.compile(br'^\s*<([^\s]+)(\s+)(.*)>\s*$')
match_section_end = re.compile(br'^\s*<\/([^\s]+).*>\s*$')
match_line_endings = re.compile(br"\r?\n")

class ApacheParseException(Exception): pass

class ApacheItemList(list):

	def find(self, name, *arguments):
		for i in self:
			i_class = i.__class__
			if i.matches(name, *arguments):
				return i

	def findAll(self, name, *arguments):
		found = self.__class__()
		for i in self:
			if i.matches(name, *arguments):
				found.append(i)
		return found

	def findChild(self, name, *arguments):
		for i in self:
			i_class = i.__class__
			if i_class in [ApacheSection, ApacheRoot]:
				return i.children.find(name, *arguments)

	def findChildren(self, name, *arguments):
		found = self.__class__()
		for i in self:
			i_class = i.__class__
			if i_class in [ApacheSection, ApacheRoot]:
				found += i.children.findAll(name, *arguments)
		return found

	def update(self, *values, **kwargs):
		replace_all = kwargs.pop('replace_all', False)
		for i in self:
			i.update(*values, replace_all = replace_all)
		return self

class ApacheItem(object):
	def __init__(self, line = None, parent = None, file = None, index = None):
		self.line = line
		self.parent = parent
		self.file = file
		self.index = index

	def matches(self, name, *arguments):
		return None

	def update(self, *values, **kwargs):
		return self

	def __str__(self):
		return self.line.strip().decode('utf-8') if self.line else ''

	def __repr__(self):
		return '<%s @ Line %d>' % (self.__class__.__name__, self.index if self.index != None else -1)

class ApacheEmptyLine(ApacheItem): pass

class ApacheComment(ApacheItem):
	def __init__(self, line = None, parent = None, file = None, index = None):
		super(self.__class__, self).__init__(line, parent, file, index)
		self.comment = None
		if line:
			self.parse()

	def parse(self):
		parts = re.search(match_comment, self.line)
		if not parts:
			raise ApacheParseException('Failed to parse %s at line %d' % (self.file, self.index))
		self.comment = parts.group(1)

	def matches(self, name, *arguments):
		if self.comment.lower() == name.lower():
			return True

	def update(self, *values, **kwargs):
		self.comment = ' '.join(values)
		return self

	def __str__(self):
		return '# ' + self.comment.decode('utf-8')

class ApacheStatement(ApacheItem):
	def __init__(self, line = None, parent = None, file = None, index = None):
		super(self.__class__, self).__init__(line, parent, file, index)
		self.module = None
		self.arguments = []
		if line:
			self.parse()

	def parse(self):
		parts = shlex.split(self.line.decode('utf-8'))
		if not parts:
			raise ApacheParseException('Failed to parse %s at line %d' % (self.file, self.index))
		self.module = parts[0]
		self.arguments = parts[1:]

	def matches(self, name, *arguments):
		if self.module.lower() == name.lower() and self.arguments[:len(arguments)] == list(arguments):
			return True

	def update(self, *values, **kwargs):
		replace_all = kwargs.pop('replace_all', False)
		if not self.arguments or replace_all:
			self.arguments = values
		elif self.arguments:
			self.arguments = list(values) + self.arguments[len(values):]
		return self

	def __str__(self):
		quoted_args = [shlex.quote(x) for x in self.arguments]
		return '%s %s' % (self.module, ' '.join(quoted_args))

	def __repr__(self):
		return "<%s '%s' @ Line %d>" % (self.__class__.__name__, self.module, self.index if self.index != None else -1)

class ApacheSection(ApacheItem):
	def __init__(self, line = None, parent = None, file = None, index = None):
		super(ApacheSection, self).__init__(line, parent, file, index)
		self.name = None
		self.arguments = None
		self.children = ApacheItemList()
		if line:
			self.parse()

	def parse(self):
		if self.line:
			parts = re.search(match_section_start, self.line)
			if not parts:
				raise ApacheParseException('Failed to parse %s at line %d' % (self.file, self.index))
			self.name = parts.group(1).decode('utf-8')
			if parts.group(3):
				self.arguments = shlex.split(parts.group(3).decode('utf-8'))

	def matches(self, name, *arguments):
		if self.name.lower() == name.lower() and self.arguments[:len(arguments)] == list(arguments):
			return True

	def update(self, *values, **kwargs):
		replace_all = kwargs.pop('replace_all', False)
		if not self.arguments or replace_all:
			self.arguments = values
		elif self.arguments:
			self.arguments = list(values) + self.arguments[len(values):]
		return self

	def find(self, name, *arguments):
		return self.children.find(name, *arguments)

	def findAll(self, name, *arguments):
		return self.children.findAll(name, *arguments)

	def appendChild(self, i):
		self.children.append(i)
		i.parent = self

	def insertBefore(self, n, o):
		for j in range(len(self.children)):
			if self.children[j] is o:
				self.children.insert(j, n)
				n.parent = self
				return self

	def renderIndent(self, indent, indent_size = 4, indent_char = ' '):
		return (indent_char * indent_size) * indent

	def renderLines(self, item, indent = 4, indent_char = ' ', indent_index = 0):
		item_class = item.__class__
		isRoot = item_class == ApacheRoot
		output_lines = []
		if isRoot or item_class == ApacheSection:
			if not isRoot:
				output_lines.append(self.renderIndent(indent_index, indent, indent_char) + str(item))
			else:
				indent_index -= 1
			for child in item.children:
				output_lines += self.renderLines(child, indent, indent_char, indent_index + 1)
			if not isRoot:
				output_lines.append(self.renderIndent(indent_index, indent, indent_char) + item.renderEndOfSection())
		elif item.__class__ in [ApacheStatement, ApacheComment, ApacheEmptyLine]:
			output_lines.append(self.renderIndent(indent_index, indent, indent_char) + str(item))
		return output_lines

	def render(self, item = None, indent = 4, indent_char = ' '):
		item = self if not item else item
		return "\n".join(self.renderLines(item, indent, indent_char)).encode('utf-8')

	def renderEndOfSection(self):
		return '</%s>' % (self.name,)

	def __str__(self):
		quoted_args = [shlex.quote(x) for x in self.arguments] if self.arguments else []
		return '<%s %s>' % (self.name, ' '.join(quoted_args))

	def __repr__(self):
		return "<%s '%s' @ Line %d>" % (self.__class__.__name__, self.name, self.index if self.index != None else -1)

class ApacheRoot(ApacheSection):
	def __repr__(self):
		return "<%s>" % (self.__class__.__name__,)

def configBuilder(config, parent = None):
	parent = ApacheRoot() if parent == None else parent
	if config['type'] == 'root' and parent.__class__ == ApacheRoot:
		for child in config['children']:
			configBuilder(child, parent)
	elif config['type'] == 'section':
		new_section = ApacheSection()
		new_section.name = config['name']
		new_section.update(*config['args'])
		for child in config['children']:
			configBuilder(child, new_section)
		parent.appendChild(new_section)
	elif config['type'] == 'statement':
		new_statement = ApacheStatement()
		new_statement.module = config['module']
		new_statement.update(*config['args'])
		parent.appendChild(new_statement)
	elif config['type'] == 'comment':
		new_comment = ApacheComment()
		new_comment.comment = config['comment']
		parent.appendChild(new_comment)
	elif config['type'] == 'emptyline':
		parent.appendChild(ApacheEmptyLine())
	else:
		raise ValueError('Invalid Type %s' % (config['type'],))
	return parent

class ApacheParser:
	def __init__(self, file, indent=4):
		self.file = file
		self.index = 0
		self.indent_size = indent
		self.root = ApacheRoot(None, None, self.file, self.index)
		self.path = [self.root]
		self.parse()

	def parseLine(self, line):
		if re.match(match_comment, line):
			return ApacheComment(line, self.path[-1], self.file, self.index)
		elif re.match(match_statement, line):
			return ApacheStatement(line, self.path[-1], self.file, self.index)
		elif re.match(match_section_start, line):
			return ApacheSection(line, self.path[-1], self.file, self.index)
		elif re.match(match_section_end, line):
			return None
		elif not line.strip():
			return ApacheEmptyLine(line, self.path[-1], self.file, self.index)
		else:
			raise ApacheParseException('Failed to parse %s at line %d' % (self.file, self.index))

	def parseFile(self):
		line = self.file.readline()
		while line:
			self.index += 1
			parsed = self.parseLine(line)
			if parsed == None:
				self.path.pop()
			else:
				self.path[-1].appendChild(parsed)
				if parsed.__class__ == ApacheSection:
					self.path.append(parsed)
			line = self.file.readline()
		return self.root

	def appendChild(self, i):
		return self.root.appendChild(i)

	def insertBefore(self, n, o):
		return self.root.insertBefore(n, o)

	def find(self, name, *arguments):
		return self.root.find(name, *arguments)

	def findAll(self, name, *arguments):
		return self.root.findAll(name, *arguments)

	def render(self, item = None, indent = 4, indent_char = ' '):
		item = self.root if not item else item
		return self.root.render(item, indent = indent, indent_char = indent_char)

	def parse(self):
		return self.parseFile()

if __name__ == '__main__':
	import sys
	if len(sys.argv) > 1 and len(sys.argv) <= 5:
		input_file = open(sys.argv[1], 'rb')
		parsed = ApacheParser(input_file)
		input_file.close()
		search_items = []
		last_items = [parsed.root]
		current_value = None
		new_value = None
		if len(sys.argv) > 2:
			search_items = sys.argv[2].split('.')
			last_item_name = search_items[-1]
			current_value = sys.argv[3] if len(sys.argv) >= 4 else None
			new_value = sys.argv[4] if len(sys.argv) == 5 else None
			last_items = parsed.findAll(search_items[0])
			del search_items[0]
		for item in search_items:
			last_items = last_items.findChildren(item)
		if current_value:
			last_items = last_items.findAll(last_item_name, *shlex.split(current_value))
		if last_items:
			for item in last_items:
				render_item = item
				if new_value != None:
					item.update(*shlex.split(new_value), replace_all = True)
					render_item = item.parent
				print(parsed.render(render_item).decode('utf-8'))
		else:
			print('Failed to find any items')
			sys.exit(1)
	else:
		print(sys.argv[0] + ' FILE VARIABLE1.VARIABLE2 [CURRENT_VALUE [NEW_VALUE]]')
		sys.exit(1)