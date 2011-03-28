text="""
id="Very Destructive Script %(num)d"
description="This is description for destructive script %(num)d"
author = "max@max"
license = "GPL of course"
categories = {"destructive"}
"""

for num in range(10000):
	f = open("script%.5d.nse" % num, "w")
	f.write(text % {"num" : num})
	f.close()
	

