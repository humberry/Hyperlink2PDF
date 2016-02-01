# coding: utf-8
from bs4 import BeautifulSoup
import urllib2, dialogs
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import Paragraph, SimpleDocTemplate, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

#ext, domain, page links
field_url=[{'type':'url', 'key':'url', 'value':'http://', 'title':'URL:'}]
field_pdf=[{'type':'switch', 'key':'htmltitle', 'value':True, 'title':'Use HTML title (or filename)'},
    {'type':'text', 'key':'filename', 'value':'urls.pdf', 'title':'Filename:'},
    {'type':'switch', 'key':'format', 'value':True, 'title':'A4 (or Letter)'}]
fields_hl=[{'type':'switch', 'key':'extlink', 'value':True, 'title':'External Hyperlinks'},
    {'type':'switch', 'key':'domainlink', 'value':True, 'title':'Domain Hyperlinks'},
    {'type':'switch', 'key':'imagelink', 'value':True, 'title':'Image Hyperlinks'},
    {'type':'switch', 'key':'qmlink', 'value':True, 'title':'??? Hyperlinks'}]
sections=[('',field_url),('PDF',field_pdf),('Hyperlinks',fields_hl)]
items = dialogs.form_dialog(title='Hyperlink2PDF', fields=None, sections=sections)
if items:
	url = items.get('url')
	htmltitle = items.get('htmltitle')
	filename = items.get('filename')
	format = items.get('format')	# True = A4 / False = letter
	extlink = items.get('extlink')
	ext = 0
	domainlink = items.get('domainlink')
	dom = 0
	imagelink = items.get('imagelink')
	qmlink = items.get('qmlink')
	if url == 'http://' or url == '':
		print 'Please type in a valid website!'
	elif htmltitle == False and filename == '':
		print 'Please type in a valid filename!'
	else:
		urlcontent = urllib2.urlopen(url).read()
		start = url.find('://') + 3
		domain = ''
		end = url.find('/', start)
		if end == -1:
			domain = url
		else:
			domain = url[:end]
		soup = BeautifulSoup(urlcontent)
		
		if htmltitle:
			title = soup.title.string
			if len(title) > 0:
				filename = title + '.pdf'
		
		links = soup.find_all('a')
		hl = []
		s = ''
		for link in links:
			text = link.get_text(" | ", strip=True)
			hlurl = link.get('href')
			hlurl = hlurl.strip()
			if not text:
				if link.find('img') != None:
					if imagelink:
						text = '[image]'
					else:
						continue
				else:
					if qmlink:
						text = '[???]'
					else:
						continue
			if '#' in hlurl and not '.' in hlurl:
				continue	#only shortcuts to other websites
			if hlurl:
				if len(hlurl) > 1:
					if hlurl[1] == '/':
						hlurl = 'http:' + hlurl
					elif hlurl[0] == '/':
						hlurl = domain + hlurl
				else:
					hlurl = domain + hlurl
			else:
				continue	#no hlurl => no link
			dhp = hlurl.find(domain[start-2:])
			if dhp == -1:	#external
				ext += 1
				if not extlink:
					continue
			else:					#domain
				dom += 1
				if not domainlink:
					continue
			print hlurl
			hl.append([text, hlurl])
		
		l = dialogs.edit_list_dialog('Hyperlinks', hl)
		heading3 = getSampleStyleSheet()['Heading3']
		fmt = '<link href="{1}" color="blue">{0}</link>'
		items = [Paragraph(fmt.format(*i), heading3) for i in l]
		pdf = SimpleDocTemplate(filename, pagesize=(A4 if format else letter))
		hls = len(items)
		if items:
			pdf.build(items)
			print 'PDF is created with ' + str(hls) + ' hyperlinks.'
			print str(ext) + ' external, ' + str(dom) + ' and domain links.'
		else:
			print 'Nothing to create :(.'
