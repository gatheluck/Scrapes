"""datacenter_dotcom.py

このモジュールには datacenter.com のページ（https://www.datacenters.com/colocation-providers）から
Beautiful Soup を使用してスクレイピングを行うコードが含まれています。

"""
import re
import logging
import pathlib

from typing import Dict

import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from bs4.element import Tag

logger = logging.getLogger(__name__)


def get_respose(url: pathlib.Path):
    response = requests.get(url)
    if response:
        return response
    else:
        logger.error(f"request is refused: {response}.")

def scrape(elem: Tag) -> Dict:
    return_dict = dict()

    # location数を取得します
    locations_match = elem.find_all(class_="ProviderTile__total__2yS-6")
    return_dict["locations"] = int(locations_match[0].text) if len(locations_match) >= 1 else "-"  # location の次に product の数が来る場合があります。

    # 企業名を取得します
    name_match = elem.find_all("h4")
    return_dict["name"] = str(name_match[0].text) if len(name_match) == 1 else np.nan

    # リンクを取得します
    link_match = elem.find_all(class_="Link__link__1BDeM ProviderTile__logoContainer__1-aJz")
    return_dict["link"] = str(link_match[0].get("href")) if len(link_match) >= 1 else np.nan

    return return_dict


if __name__ == "__main__":
    # datacenter.com のページは動的な要素を含んでいるため、手動で必要な情報を含むページに遷移してそれを保存し、それを読み込むようにします。
    # url = 'https://www.datacenters.com/colocation-providers'
    # response = get_respose(url)
    htmlpath = pathlib.Path("data/datacenter_dotcom/datacenter_dotcom.html")
    with open(str(htmlpath), encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # ページのタイトルを確認のために表示します。
    title_text = soup.find('title').get_text()
    logger.info(f"Target page: {title_text}")

    elems = soup.find_all(class_="ProvidersList__providerTile__3A11V")
    logger.info(f"#Total recodes: {len(elems)}")

    df = pd.DataFrame(columns=["name", "locations", "link"])
    for elem in elems:
        df = df.append(scrape(elem), ignore_index=True)
    logger.info(df)

    # dataframe を保存します。
    savepath = pathlib.Path("output/datacenter_dotcom/datacenter_list.xlsx")
    df.to_excel(str(savepath))
