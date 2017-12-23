import navegador5 as nv
import navegador5.url_tool as nvurl
import navegador5.head as nvhead
import navegador5.body as nvbody
import navegador5.cookie
import navegador5.cookie.cookie as nvcookie
import navegador5.cookie.rfc6265 as nvrfc6265
import navegador5.jq as nvjq
import navegador5.js_random as nvjr
import navegador5.file_toolset as nvft
import navegador5.shell_cmd as nvsh
import navegador5.html_tool as nvhtml
import navegador5.solicitud as nvsoli
import navegador5.content_parser
import navegador5.content_parser.amf0_decode as nvamf0
import navegador5.content_parser.amf3_decode as nvamf3

from lxml import etree
import lxml.html
import collections
import copy
import re
import urllib
import os
import json
import sys
import time


from xdict.jprint import  pobj
from xdict.jprint import  print_j_str
from xdict import cmdline
from xdict.jprint import pdir

import hashlib




#
photosdir = sys.argv[2]
#-photosdir /media/root/6d1de738-2a56-4564-ab92-0401c7fe0f68/Images
ryan_base_url = 'http://www.ryanphotographic.com/'
ryan_url = 'http://www.ryanphotographic.com/gastropoda.htm'
#ryan_init
def ryan_init(base_url='http://www.ryanphotographic.com/'):
    info_container = nvsoli.new_info_container()
    info_container['base_url'] = base_url
    info_container['method'] = 'GET'
    req_head_str = '''User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2\r\nAccept-Encoding: gzip, deflate'''
    info_container['req_head'] = nvhead.build_headers_dict_from_str(req_head_str,'\r\n')
    info_container['req_head']['Connection'] = 'close'
    #### init records_container
    records_container = nvsoli.new_records_container()
    return((info_container,records_container))

################################################################################
###############################################################################
def get_etree_root(info_container):
    html_text = info_container['resp_body_bytes'].decode('utf-8')
    root = etree.HTML(html_text)
    return(root)

####################################

####################################


def get_species(root):
    eles_sps= root.xpath('//tr/td/span/a  | //tr/td/em/strong/a | //tr/td/a | //tr/td/strong/a | //tr/td/em/a | //tr/td/a | //tr/td/strong/em/a')
    new_eles_sps = []
    for i in range(0,eles_sps.__len__()):
        if(('#' in eles_sps[i].attrib['href']) | ('strombidae' in eles_sps[i].attrib['href']) | ('images' in eles_sps[i].attrib['href'])):
            new_eles_sps.append(eles_sps[i])
        else:
           pass
    del new_eles_sps[-1]
    #####################
    ele_cnames = []
    for i in range(0,new_eles_sps.__len__()):
        td_parent = new_eles_sps[i].getparent()
        while(td_parent.tag != 'td'):
            td_parent = td_parent.getparent()
        td_next = td_parent.getnext()
        ele_cnames.append(td_next) 
    #####################
    urls = []
    for i in range(0,new_eles_sps.__len__()):
        urls.append(ryan_base_url + new_eles_sps[i].attrib['href'])
    #####################
    dir_names = []
    for i in range(0,new_eles_sps.__len__()):
        dir_names.append(new_eles_sps[i].attrib['href'].replace('.htm','').replace('#',' '))
    ####################
    new_urls_set = set({})
    for i in range(0,urls.__len__()):
        url = urls[i]
        url = url.split('#')[0]
        new_urls_set.add(url)           
    ####################
    image_urls = []
    for url in new_urls_set:
        info_container['url'] = url
        info_container = nvsoli.walkon(info_container,records_container=records_container)
        root = get_etree_root(info_container)
        eles= root.xpath('//tr/td/div/img')
        for j in range(0,eles.__len__()):
            image_urls.append((ryan_base_url + eles[j].attrib['src']).replace(' ','%20'))
    #####################
    mirror_indexes = {}
    image_names = []
    info_names = []
    infos = []
    for i in range(0,image_urls.__len__()):
        suffix = image_urls[i].split('.')[-1]
        arr  = os.path.basename(image_urls[i]).split('%20')
        name = arr[0]+' '+arr[1].rstrip(',').rstrip('.').rstrip(' ')+'_' 
        name = name + hashlib.sha1(image_urls[i].encode('utf-8')).hexdigest()
        name = name+'.'+suffix
        image_names.append(name)
        info_names.append(name+'.'+'info')
        info = {}
        info['origin'] = image_urls[i]
        info['path'] = ''
        info['details'] = {}
        infos.append(info)
        mirror_indexes[name] = image_urls[i]
        mirror_indexes[image_urls[i]] = name
        info_container['url'] = image_urls[i]
        info_container = nvsoli.walkon(info_container,records_container=records_container)
        nvft.write_to_file(fn=photosdir+'/'+image_names[i],op='wb',content=info_container['resp_body_bytes'])
    nvft.write_to_file(fn=photosdir+'/'+'indexes.dict',op='w',content=json.dumps(mirror_indexes))
    ##################### 


#################################################
info_container,records_container = ryan_init()
info_container['url'] = ryan_url
info_container = nvsoli.walkon(info_container,records_container=records_container)
info_container = nvsoli.auto_redireced(info_container,records_container)
root = get_etree_root(info_container)
get_species(root)
