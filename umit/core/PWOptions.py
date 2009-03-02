
from xml.dom import minidom



class PWOptions: 
	"""
	This works with profile and wizard options xml files 
	Read and write
	"""


	def __init__(self, filename):
		#xml_desc = open(filename)
		self.filename=filename
		self.doc = minidom.parse(filename)
		#xml_desc.close()
	def read(self,tag="option",name="name",option="option"):
		#print tag, name, option	
		result = []
		for node in self.doc.getElementsByTagName(tag):
			tmp_name= node.getAttribute(name)
			tmp_option = node.getAttribute(option)
			#print option
			result.append((tmp_name,tmp_option))
		return result
	

if __name__ == '__main__':
	p = PWOptions("/home/kop/.umit/wizard.xml")
	print p.read()
	print p.read("group", "name", "group")

