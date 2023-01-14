from scrapers.interface import JobDetails


class MongoJob(JobDetails):
    """
        I'll validate the required properties 
    """

    def __init__(self,
                 name='', url='', url_to_apply='',
                 body='', apply_account=-1, id='',
                 date='', salary=(-1, -1), seniority='',
                 portal='', url_to_apply_quick=''
                 ) -> None:

        assert id != None and id != ''
        assert type(url) == str and len(url) != 0
        assert type(body) == str and len(body) != 0

        super().__init__(
            name, url, url_to_apply,
            body, apply_account, id,
            date, salary, seniority,
            portal, url_to_apply_quick
        )


class MongoTokens:
    def __init__(self, name: str, doc_list: set, current_value: None) -> None:
        assert name != ''
        assert len(doc_list) != 0

        self.name = name

        if current_value:
            for doc in current_value['docList']:
                doc_list.add(doc)

        self.docList = list(doc_list)
