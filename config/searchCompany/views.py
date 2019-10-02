from django.shortcuts import render
from django.http import HttpResponse
from searchCompany import search

from django.urls import reverse_lazy
# Create your views here.
def searchCompany(request):
    company = request.GET.get('companyName')
    if company:
        d = search.main(company)
        data = {
            'searchWord':d['searchWord'],
            'vname':d['vorkers'][0],
            'vpoint':d['vorkers'][1],
            'vsiteUrl':d['vorkers'][2],
            'hname':d['hyoban'][0],
            'hpoint':d['hyoban'][1],
            'hsiteUrl':d['hyoban'][2],
            'industry':d['jyoujyou'][0],
            'investment':d['jyoujyou'][1],
            'employees':d['jyoujyou'][2],
            'averageYears':d['jyoujyou'][3],
            'averageTerms':d['jyoujyou'][4],
            'averageSalary':d['jyoujyou'][5],
            'jname':d['jyoujyou'][6],
        }  
        return render(request, 'searchCompany/search.html', data)
    else:
        return render(request, 'searchCompany/search.html')