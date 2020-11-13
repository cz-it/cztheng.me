#!/usr/bin/python2.7 
from lxml.etree import HTML
from lxml import etree, html
from lxml.html.clean import Cleaner
import os

in_file = open(os.path.abspath("../www/about_cz/index.html"),"r")
html_text = in_file.read()
dom= html.fromstring(html_text)
pc_divs=dom.xpath('.//div[@class="post-copyright"]')
pm_divs=dom.xpath('.//div[@class="post-meta"]')
pc_divs[0].getparent().remove(pc_divs[0])
pm_divs[0].getparent().remove(pm_divs[0])
out_file = open(os.path.abspath("../www/about/index.html"),"w")
out_file.write(html.tostring(dom))

