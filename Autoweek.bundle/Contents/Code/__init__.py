#Autoweek.nl VideoPlugin v1.2.4
#Created by Matthijs Drenth

import sys
import urllib 
import re

####################################################################################################

VIDEO_PREFIX = "/video/autoweek"

NAME = L('Title')

ART  = 'art-default.jpg'
ICON = 'icon-default.png'

####################################################################################################

def Start():

    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, NAME, ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    MediaContainer.title1 = NAME
    MediaContainer.viewGroup = "List"
    MediaContainer.art = R(ART)
    DirectoryItem.thumb = R(ICON)
    VideoItem.thumb = R(ICON)
    
    HTTP.CacheTime = 1
	

####################################################################################################

def VideoMainMenu():

	dir = MediaContainer(viewGroup="List")
	dir.Append(Function(DirectoryItem(ShowLatest, 'Nieuwste video\'s', None)))
	dir.Append(Function(DirectoryItem(ShowTop10, 'Top 10 meest bekeken afgelopen maand', None)))
	dir.Append(Function(DirectoryItem(empty, None, None)))
	dir.Append(Function(DirectoryItem(ShowSubCats, 'Video\'s per Categorie', None)))
	dir.Append(Function(DirectoryItem(ShowSubBrands, 'Video\'s per Automerk', None)))
	
	return dir

####################################################################################################

def ShowSubCats(sender):

	dir = MediaContainer(viewGroup="List")
	dir.Append(Function(DirectoryItem(ShowNews, 'Nieuws videos', None),offset='1',cat='1', brand='0', sender=''))
	dir.Append(Function(DirectoryItem(ShowNews, 'Videospecials', None),offset='1',cat='2', brand='0', sender=''))
	dir.Append(Function(DirectoryItem(ShowNews, 'Occasion video\'s', None),offset='1',cat='4', brand='0', sender=''))
	dir.Append(Function(DirectoryItem(ShowNews, 'Autotest video\'s', None),offset='1',cat='5', brand='0', sender=''))
	dir.Append(Function(DirectoryItem(ShowNews, 'Injection TV', None),offset='1',cat='7', brand='0', sender=''))

	return dir

####################################################################################################

def ShowSubBrands(sender):
	dir = MediaContainer(viewGroup="List")
	url ='http://www.autoweek.nl/videoindex.php'
	itemnr = 00
	for item in HTML.ElementFromURL(url).xpath("//select[@name=\"merk\"]/option"):
		try:
			itemnr = itemnr + 01
			nr = str(itemnr) + '. '
			title = item.text
			brand = item.get('value')
			dir.Append(Function(DirectoryItem(ShowNews, title, None),offset='1',cat='', brand=brand, sender=''))
		
		except:
			return MessageContainer("Helaas", "Geen Video's gevonden")
    
	return dir
	
####################################################################################################

def ShowLatest(sender):

    dir = MediaContainer(viewGroup="InfoList")
   
    page = XML.ElementFromURL("http://www.autoweek.nl/rss/video")
    for item in page.getiterator('item'):
    	link=item.findtext("link")
        title=item.findtext("title").encode("latin1")
        pubDate=item.findtext("pubDate")
        description=remove_html_tags(item.findtext("description"))
        description=description.encode("utf-8").encode('ascii', 'xmlcharrefreplace').encode('ascii', 'xmlcharrefreplace')
        dir.Append(Function(VideoItem(GetUrl, title=title, summary=description, subtitle=pubDate, thumb=Function(GetThumb, vl=link)), url=link, title=title))
    return dir

####################################################################################################

def ShowTop10(sender):
	dir = MediaContainer(viewGroup="List")
	url ='http://www.autoweek.nl/videoindex.php'
	itemnr = 00
	for item in HTML.ElementFromURL(url).xpath("//li[@class=\"smallindexitem\"]/div"):
		try:
			itemnr = itemnr + 01
			nr = str(itemnr) + '. '
			name = nr + item.xpath("a")[0].text
			pubdate = item.xpath("div[@class=\"itemdate\"]")[0].text
			link = 'http://www.autoweek.nl' + item.xpath("a")[0].get('href')
			title = name + ' - ' + pubdate
			dir.Append(Function(VideoItem(GetUrl, title=title, summary=None, subtitle=None, thumb=Function(GetThumb, vl=link)), url=link, title=title))
			#Function(GetThumb, vl=link)
		except:
			return MessageContainer("Helaas", "Geen video's gevonden")
    
	return dir

####################################################################################################

def ShowNews(sender, offset, cat,brand):
	this_offset= int(offset)
	next_offset= this_offset + 1 
	prev_offset= this_offset - 1 
	
	dir = MediaContainer(viewGroup="List")
	url ='http://www.autoweek.nl/videoindex.php?merk=' + brand + '&model=0&cat=' + cat + '&offset=' + str(offset)
	itemnr = 00
	if this_offset > 1:
		dir.Append(Function(DirectoryItem(ShowNews, '<-- Vorige Pagina <--', None),offset=prev_offset,cat=cat,band=brand,sender=''))
		
	for item in HTML.ElementFromURL(url).xpath("//td[@class=\"thumbviewitem\"]/div[@style=\"width:120px\"]"):
		try:
			itemnr = itemnr + 01
			nr = str(itemnr) + '. '
			#src = item.xpath('img')[0].get('src')
			title = item.xpath("a")[0].get('title')
			#title = itemnr + ". " + title
			#title = nr
			link = 'http://www.autoweek.nl' + item.xpath("a")[0].get('href')
			
    		#subtitle = item.xpath("//div[@class=\"tekst\"]")[0].text
			dir.Append(Function(VideoItem(GetUrl, title=title, summary=None, subtitle=None, thumb=Function(GetThumb, vl=link)), url=link, title=title))
			#Function(GetThumb, vl=link)
		except:
			return MessageContainer("Helaas", "Geen Video's gevonden")
		
	if itemnr == 16:
		dir.Append(Function(DirectoryItem(ShowNews, '--> Volgende Pagina -->', None),offset=next_offset,cat=cat,brand=brand,sender=''))
	return dir

####################################################################################################

def GetUrl(sender, url, title):
	sock = urllib.urlopen(url) 
	sdpagecontent = sock.read()                            
	sock.close()
	#m1 = re.search('mp4_file=(.{0,})(_ipad.mp4\")', sdpagecontent)
	m1 = re.search('flv_file=(.{0,})(.flv)', sdpagecontent)
	Log(m1.group(2))
	#try:
	#	VideoLinkHD = "http://media.autoweek.nl/m/" + m1.group(1) + "_hd.mp4"
	#	return Redirect(VideoItem(VideoLinkHD))	
	#except:
	#	VideoLinkSD = "http://media.autoweek.nl/m/" + m1.group(1) + "_ipad.mp4"
	#	return Redirect(VideoItem(VideoLinkSD))
	VideoLinkFLV = "http://media.autoweek.nl/m/" + m1.group(1) + ".flv"
	return Redirect(VideoLinkFLV)
		
####################################################################################################

def GetThumb(vl):
	sock = urllib.urlopen(vl) 
	pagecontent = sock.read()                            
	sock.close()
	
	m2 = re.search('mp4_file=(.{0,})(_ipad.mp4\")', pagecontent)
	thumb = m2.group(1)
	thumb = "http://media.autoweek.nl/m/" + thumb + "_m.jpg"
	try:
		image = HTTP.Request(thumb, cacheTime=CACHE_1MONTH).content
		return DataObject(image, 'image/jpeg')
	except:
		return Redirect(R(PLUGIN_ICON_DEFAULT))
		
####################################################################################################

def remove_html_tags(data):
    p = re.compile('<.*?>|&nbsp;|Lezersreacties(.{0,})|Uw reactie plaatsen|\s\s')
    return p.sub('', data)

def empty(sender):
	sys.exit()
	return sender