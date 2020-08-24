from datetime import date, timedelta
import re

from bs4 import BeautifulSoup
import requests


class Job(object):
    '''Stores per job data.

    Attributes:
        position: Position title.
        description_link: Description link.
        company_name: Company name.
        company_url: Company URL.
        job_type: Job type.
        location: Location name.
    '''

    def __init__(self, position, description_link, company_name, company_url, job_type, location, published):
        self._position = position
        self._desc_link = description_link
        self._name = company_name
        self._url = company_url
        self._job_type = job_type
        self._location = location
        self._published = published

    def __str__(self) -> str:
        return self.detailed_string()

    def __repr__(self) -> str:
        return self.detailed_string()

    def detailed_string(self) -> str:
        return ('Job(\n'
            f'\tPosition: {self._position},\n'
            f'\tDescription link: {self._desc_link},\n'
            f'\tCompany name: {self._name},\n'
            f'\tCompany URL: {self._url},\n'
            f'\tJob type: {self._job_type},\n'
            f'\tLocation: {self._location},\n'
            f'\tPublished: {self._published}\n'
            ')')


class GitHubJob(Job):
    '''Stores per data from GitHub Jobs (https://jobs.github.com/).

    Attributes:
        position: Position title.
        description_link: Description link.
        company_name: Company name.
        company_url: Company URL.
        job_type: Job type.
        location: Location name.
    '''

    def __init__(self, position, description_link, company_name, company_url, job_type, location, published):
        Job.__init__(self,
                     position=position,
                     description_link=description_link,
                     company_name=company_name,
                     company_url=company_url,
                     job_type=job_type,
                     location=location,
                     published=published)

    def detailed_string(self) -> str:
        return ('GitHub Job(\n'
            f'\tPosition: {self._position},\n'
            f'\tDescription link: {self._desc_link},\n'
            f'\tCompany name: {self._name},\n'
            f'\tCompany URL: {self._url},\n'
            f'\tJob type: {self._job_type},\n'
            f'\tLocation: {self._location},\n'
            f'\tPublished: {self._published}\n'
            ')')


def entry_point():
    '''Entry point.'''

    url = 'https://jobs.github.com/positions?description=Python'
    request = requests.get(url)
    bs = BeautifulSoup(request.text, 'html.parser')

    for tr in bs.find_all('tr', class_='job'):
        position = tr.td.h4.text
        description_link = tr.td.h4.a.attrs['href']
        company_name = tr.find('a', class_='company').text
        company_url = tr.find('a', class_='company').attrs['href']
        job_type = tr.find('strong').text
        location = tr.find('span', class_='location').text
        when_relaitze_relatized \
            = tr.find('span', class_='when relatize relatized').text
        published_days_ago \
            = int(re.search(r'\d+', when_relaitze_relatized).group())
        published = date.today() - timedelta(days=published_days_ago)

        _ \
            = GitHubJob(position=position,
                        description_link=description_link,
                        company_name=company_name,
                        company_url=company_url,
                        job_type=job_type,
                        location=location,
                        published=published)


if __name__ == '__main__':
    '''Local development'''

    entry_point()
