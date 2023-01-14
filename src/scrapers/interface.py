from typing import Protocol, Tuple, List


class JobDetails:
    def __init__(
        self, name='', url='',
        url_to_apply='', body='',
        apply_account=-1, id='',
        date='', salary=(-1, -1),
        seniority='', portal='',
        url_to_apply_quick=''
    ) -> None:

        self.name = name
        self.url = url
        self.id = id
        self.date = date
        self.salary = salary
        self.seniority = seniority
        self.portal = portal
        self.url_to_apply = url_to_apply
        self.url_to_apply_quick = url_to_apply_quick
        self.body = body
        self.apply_account = apply_account


class JobSummary:
    def __init__(self, name='', url='', id='', date='', salary=(-1, -1), seniority='', portal='') -> None:
        self.name = name
        self.url = url
        self.id = id
        self.date = date
        self.salary = salary
        self.seniority = seniority
        self.portal = portal


class Scraper(Protocol):
    def get_many_jobs(self, n) -> List[JobSummary]:
        pass

    def get_details_for_job(self, url) -> JobDetails:
        pass
