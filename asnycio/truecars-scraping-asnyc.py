#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 01 09:31:09 2018

@author: chenchuqiao

asnyc for searching for the cars url on truecars.com

the successful ways, performance: 10mins for 10K urls on static website

possible reason maybe

"""
#import requests
from lxml import etree
import aiohttp
import asyncio
import pandas as pd
import time
from fakeuseragent import Proxy_n_agent
Proxy_class = Proxy_n_agent()


#after asyncio
class AsnycBlindSearch(object):
    #initial part
    def __init__(self, url_list, max_threads):
        '''initial the urllist needs to be feed and thread we will use'''
        self.urls = url_list
        self.results = {}#dictionary
        self.max_threads = max_threads

    def get_onepage_urllist(self, url, html):
        '''given a url get 30 urllink back'''
        try:
            #use sessions to get the
            #r = requests.get(url).text
            s = etree.HTML(html)
            car_vin = s.xpath('//a[@class="vdp-link"]/@href')
            urllist = []
            for vin in car_vin:
                vinclean = vin.split('/listing/')[1].split('/')[0]
                urlclean = 'https://www.truecar.com/used-cars-for-sale/listing/' + str(vinclean)
                urllist.append(urlclean)
            self.results[url] = urllist[::2]
        except Exception as e:
            print(e)
        #we may use set to manipulate it later
        #self.results[url] = urllist[::2]

    #below begins async part
    async def get_body(self, url):
        #set our async ClientSession
        async with aiohttp.ClientSession() as session:

            headers = {'user-agent': Proxy_class.uagt}
            proxy = Proxy_class.proxy
            response = await session.get(url, headers = headers, proxy = proxy, timeout=30)
            assert response.status == 200
            html = await response.read()
        return response.url, html

    async def get_results(self, url):
        url, html = await self.get_body(url)
        self.get_onepage_urllist(url, html)
        return 'Completed'

    async def handle_tasks(self, task_id, work_queue):
        #deal with work_queue
        while not work_queue.empty():
            current_url = await work_queue.get()
            try:
                task_status = await self.get_results(current_url)
            except Exception as e:
                print('Error {} for {} '.format(e, current_url))#,exc_info=True)


    def eventloop(self):
        #define event loops
        q = asyncio.Queue()
        [q.put_nowait(url) for url in self.urls]
        loop = asyncio.new_event_loop()#get_event_loop()#?
        tasks = [self.handle_tasks(task_id, q, ) for task_id in range(self.max_threads)]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

def main():
    #here read in the target url in csv format, the csv url list could be changed based on needs
    readin_df = pd.read_csv('feedin_url.csv',names = ['url'])
    readin_urllist = readin_df.url.tolist()[1:]
    print('Asnyc will process: '+ str(len(readin_urllist)))

    #test this part below
    start_time = time.time()
    sample = readin_urllist[:]
    async_example1 = AsnycBlindSearch(sample, 10)
    a = async_example1.eventloop()
    url_dict = async_example1.results
    print("--- %s seconds ---" % (time.time() - start_time))

    #store the output to csv format
    urloutset = set()
    for key,value in url_dict.items():
        urloutset |= set(value)
    storenum = len(urloutset)#890/900
    print('store num will be '+ str(storenum))

    dfstore = pd.DataFrame({'url':list(urloutset)})
    dfstore.to_csv('blindsearch_truecars_urls.csv')

if __name__ == '__main__':
    main()

#--test result--
len(readin_urllist)
len(url_dict)

for key, items in url_dict.items():
    print(key)
    print(items[0])
