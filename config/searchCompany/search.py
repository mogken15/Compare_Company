from django.http import HttpResponse
from django.views import generic

from django.test import TestCase

import requests
import bs4
from operator import itemgetter
import mojimoji


#パース対象サイトをここに追加
targetSite =['vorkers', 'hyoban', 'jyoujyou']

class GetHtml:
    """
    GetHtml as text
    """
    # 検索サイトのURL登録
    def __init__(self, company):
        self.headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0",}
        self.urls = {
            targetSite[0]:'https://www.vorkers.com/company_list?field=&pref=&src_str={}&sort=1&ct=top'.format(company), 
            targetSite[1]:'https://en-hyouban.com/search/?SearchWords={}'.format(company),
            targetSite[2]:'https://上場企業サーチ.com/searches/result?utf8=✓&search_query={}'.format(company)
        }

    # 対象ページのHtml全文を取得
    def getText(self):
        textList = {}
        for url in self.urls:
            res = requests.get(self.urls[url], headers=self.headers)
            text = bs4.BeautifulSoup(res.text, "html.parser")
            textList.setdefault(url, text)
        return textList


class ParseHtml:
    """
    ParseHtmlHtml to get required values
    """
    # 企業名と評価ポイントの取得
    def parseNamePoint(self, textList):
        #パース用のタグ登録
        nameTag =  {
            targetSite[0]:["h3", "fs-18 lh-1o3 p-r"],
            targetSite[1]:["h2", "companyName"],
        }
        pointTag = {
            targetSite[0]:["p", "totalEvaluation_item fs-15 fw-b"],
            targetSite[1]:["span", "point"],
        } 

        comNamePoint = {}
        for site in targetSite[:2]:
            try:
                #会社名の取得
                parseCname =  textList[site].find(nameTag[site][0], class_=nameTag[site][1])
                cname = parseCname.getText().replace('\n','').replace(' ', '')

                #会社評価ポイントの取得
                parseCpoint = textList[site].find(pointTag[site][0], class_=pointTag[site][1])              
                cpoint = parseCpoint.getText().replace('\n','').replace(' ', '')
        
            # 検索結果が無かった場合の処理
            except AttributeError:
                comNamePoint.setdefault(site, ['結果なし','結果なし'])
               
            # 検索結果が有った場合の処理
            else:
                comNamePoint.setdefault(site, [cname, cpoint])

        return comNamePoint

    # 上々企業である場合、企業詳細の取得
    def parseInfo(self, textList):
        #パース用のタグ登録
        cnumberTag = {
            targetSite[2]:['dl', 'well'],
        }
        cinfoTag = {
            targetSite[2]:['dd', 'companies_data']
        }
        
        comInfo = {}

        #企業名から企業詳細URLの取得        
        try:
            parseCnumber =  textList[targetSite[2]].find(cnumberTag[targetSite[2]][0], class_=cnumberTag[targetSite[2]][1])
            cnumber = parseCnumber.getText()
            cname = mojimoji.han_to_zen(cnumber[5:].replace('\n', '').replace(' ', ''))
            detail = 'https://xn--vckya7nx51ik9ay55a3l3a.com/companies/{}'.format(cnumber[:5])
        # 検索結果が無かった場合の処理
        except AttributeError:
            comInfo.setdefault(targetSite[2], ['データ無し','','','','','',''])
        # 検索結果が有った場合の処理
        else:
            #企業詳細ページのHtml取得
            res = requests.get(detail)
            text = bs4.BeautifulSoup(res.text, "html.parser")

            #企業詳細ページのパース
            parseCinfo =  text.find_all(cinfoTag[targetSite[2]][0], class_=cinfoTag[targetSite[2]][1])
            cinfo = parseCinfo

            #パースした内容の取得
            cinfoList = []
            for info in cinfo:
                infoText = info.getText().replace('\n', '').replace('\t', '')
                cinfoList.append(infoText)
            #企業名の追加
            cinfoList.append(cname)

            if len(cinfoList) <= 18:
                cinfoList.append('')
            
            #必要情報の成形
            useList = itemgetter(0,10,14,15,16,17,18)(cinfoList)
            comInfo.setdefault(targetSite[2], useList)
            
        return comInfo
        
def main(company):
    aboutCompany = {}

    #URLとHtmlの取得
    getHtml = GetHtml(company)
    text = getHtml.getText()
    urls = getHtml.urls

    #htmlのパース
    parseHtml = ParseHtml()
    comNamePoint = parseHtml.parseNamePoint(text)
    comInfo = parseHtml.parseInfo(text)
    
    #出力データの成形
    #企業名と評価ポイント
    for site in targetSite[:2]:
         comNamePoint[site].append(urls[site])
    aboutCompany.update(comNamePoint)
    
    #企業詳細情報
    for info in comInfo:
        aboutCompany.setdefault(info, comInfo[info])
    
    #検索ワード
    words = mojimoji.han_to_zen(company)
    aboutCompany['searchWord'] = words


    return aboutCompany

if __name__ =="__main__":
    print(main('ソフトバンク'))