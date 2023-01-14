from .interface import JobDetails, JobSummary
from typing import Tuple
import requests
from bs4 import BeautifulSoup
import json


class GetOnBoardScraper:
    BASE_URL = 'https://www.getonbrd.com/misempleos'
    COOKIE = "_getonboard_session=4d7da4d400f5f3b9defc69c2d1fbf04a; chaskiq_ap_session_ZbJiDh782OenBxQjxdhytQ=eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaDdCem9LWlcxaGFXeEpJaWhrWVc1cFpXeHZjbXhoYm1SdmIzSjBhWHB3WVdOb1pXTnZRR2R0WVdsc0xtTnZiUVk2QmtWVU9nbDBlWEJsTUE9PSIsImV4cCI6bnVsbCwicHVyIjoibG9naW4ifX0=--9215472afd83702497b4b7e35d711e5fe30f7578f169ba86b49af928401f8b0e; chaskiq_session_id_ZbJiDh782OenBxQjxdhytQ=ID5qtfGAEjc4_DOt_aOidg; cookies_privacy_policy_consent=true; lang=es; _ga_QT8F9LD9HL=GS1.1.1668432075.15.1.1668432552.0.0.0; _fbp=fb.1.1667315107795.2014613611; _rdt_uuid=1667315105386.896c2fb3-1393-4712-8288-adead405b9c9; _ga=GA1.1.1628781124.1667315100; _tt_enable_cookie=1; _ttp=13b81a1e-24f8-4e60-b7de-dffa7af8afc6; _gcl_au=1.1.1750219648.1668082407"
    HEADERS = {
        "X-Requested-With": "XMLHttpRequest",
        # "X-CLIENT-ID":"b3fbf163-553b-46d4-88fa-2ba43442a9ed-1668479959826",
        "X-CSRF-Token": "O+r8HuY1q82L8n9evWjFojKs63kh7p1mHvBwGDjTet/6zmFKr41ejCPmchSL03ELoDzk99euk6W8yMFxO+8W1A==",
        # "X-NewRelic-ID":"VQYDU15WCBAGU1ZXBAMD",
        "Content-Length": "0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Pragma": "no-cache",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Accept-Encoding": "gzip, deflate, br",
        "Host": "www.getonbrd.com",
        "User-Agent": "PostmanRuntime/7.29.2",
        "Origin": "https://www.getonbrd.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15",
        "Connection": "keep-alive",
    }

    PARAMS = {
        "tags_criteria": "any",
        # "webpro%5Bcategory_ids%5D%5B%5D":None,
        # "webpro%5Btag_ids%5D%5B%5D":"",
        # "webpro%5Bmodality_ids%5D%5B%5D": "",
        # "webpro%5Btenant_ids%5D%5B%5D": "",
        # "webpro%5Bseniority_ids%5D%5B%5D": "",
        # "webpro%5Bcompanies_blacklist_ids%5D%5B%5D": "",
        # "webpro%5Bremote_jobs%5D":"false",
        "webpro[min_salary]": 0,
        # "webpro%5Btag_ids%5D%5B%5D":"18"
    }

    def __init__(self) -> None:
        cookie = self.COOKIE.split('; ')
        self.cookie = {}
        for c in cookie:
            ccs = c.split('=')
            self.cookie[ccs[0]] = '='.join(ccs[1:])

        self.offset = 0

    def get_many_jobs(self, n) -> Tuple[str, str]:
        result = []
        print(
            f"=========== GetOnBoard Scraper are Finding {n} list of jobs ======================")

        params = self.PARAMS

        for i in range(n):
            params['offset'] = str(i * 25)

            response = requests.post(
                url="http://www.getonbrd.com/webpros/search_jobs.json", params=params, headers=self.HEADERS, cookies=self.cookie)
            try:
                data = json.loads(response.content.decode())
            except:
                self.handler_error(response.content.decode())
            print(
                f"=========== Iter N.{i * 25} is Loading {len(data['jobs'])} jobs ================================")
            result += data['jobs']

        id_map = {}
        print(f"=========== It's Mapping to Summary Jobs ================================")
        for job in result:
            try:
                _ = id_map[job['id']]
            except:
                id_map[job['id']] = JobSummary(
                    name=job['title'],
                    id=job['id'],
                    salary=(job['min_salary'], job['max_salary']),
                    date=job['published_at'],
                    url='https://www.getonbrd.com' + job['url'],
                    seniority=job['seniority'],
                    portal='get_on_board'
                )

        return list(id_map.values())

    def get_details_for_job(self, job: JobSummary) -> JobDetails:
        print(
            f"🪲 GetOnBoard Scraper are Finding Details for {job.id} - {job.url}")

        page = requests.get(job.url).content
        soup = BeautifulSoup(page, 'html.parser')
        body = soup.find("div", {"id": "job-body", "itemprop": 'description'})
        test = [ch for ch in body.get_text().split('\n') if ch != '']

        apply_bottom = soup.find("a", {"id": "apply_bottom"})
        quick_apply_bottom = soup.find("a", {"id": "quick_apply_bottom"})

        info = job.__dict__
        info['body'] = '\n'.join(test)
        info["url_to_apply"] = apply_bottom.get('href')
        info["url_to_apply_quick"] = None if quick_apply_bottom is None else quick_apply_bottom.get(
            'href')

        return JobDetails(**info)

    # TODO: Is possible that the cookie will became to bad credential. I have to change sometimes
    def handler_error(self, text):
        with open('index.html', 'w+') as f:
            f.write(text)
            f.close()

        raise TypeError("Una Mierda")
