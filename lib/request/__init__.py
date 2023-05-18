import logging
import requests
from scrapy import Selector

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/80.0.3987.149 Safari/537.36",

}


class RequestsWithRetry:
    def __init__(self, log_filename: str = 'requests.log', log_level: int = logging.INFO, retry_times: int = 5):
        self.retry_times = retry_times
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler(log_filename)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def request_with_retry(self, method: str, url: str, **kwargs) -> requests.Response:
        for retry_count in range(self.retry_times):
            try:
                response = self.session.request(method=method.upper(), url=url, **kwargs)
                response.encoding = 'gbk'
                response.raise_for_status()  # 如果响应状态码不是 200，就主动抛出异常
                return response
            except requests.exceptions.RequestException as e:
                if retry_count > 2:
                    self.logger.error(f'Request to {url} failed: {str(e)}')
                if retry_count == self.retry_times - 1:
                    raise e

    def get(self, url: str, params=None, **kwargs) -> requests.Response:
        return self.request_with_retry('get', url, params=params, **kwargs, headers=headers)

    def post(self, url: str, data=None, **kwargs) -> requests.Response:
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        return self.request_with_retry('post', url, data=data, **kwargs, headers=headers)

    def get_book_info(self, book_id) -> Selector:
        response = self.get('http://www.huanxiangji.com/book/{}/'.format(book_id))
        if response.status_code == 200:
            return Selector(text=str(response.text))

    def get_chapter(self, book_id: str, chapter_id: str) -> str:
        response = self.get("http://www.huanxiangji.com/book/{}/{}".format(book_id, chapter_id))
        if response.status_code == 200:
            return Selector(text=str(response.text)).xpath('//*[@id="content"]').get()

    def post_search(self, search_key: str):
        response = self.post('http://www.huanxiangji.com/modules/article/search.php', data={'searchkey': search_key})
        return response.text
