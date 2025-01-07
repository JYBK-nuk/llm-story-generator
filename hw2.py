import os
import re
from datetime import datetime, timedelta
from io import StringIO

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pytz import timezone

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def validate_date(date_text):
    """
    驗證日期格式是否為 YYYY/MM/DD。
    """
    try:
        datetime.strptime(date_text, "%Y/%m/%d")
        return True
    except ValueError:
        return False


def get_date_range(start_date, end_date):
    """
    根據起始日期和結束日期生成日期列表。
    """
    start = datetime.strptime(start_date, "%Y/%m/%d")
    end = datetime.strptime(end_date, "%Y/%m/%d")
    delta = end - start
    return [start + timedelta(days=i) for i in range(delta.days + 1)]


def fetch_day_trading(session, date, commodity_id="TXF") -> str:
    """
    抓取日盤資料。
    """
    url = "https://www.taifex.com.tw/cht/3/futContractsDate"
    payload = {
        "queryType": "3",
        "goDay": "",
        "doQuery": "1",
        "dateaddcnt": "-1",
        "queryDate": date.strftime("%Y/%m/%d"),
        "commodityId": commodity_id,
    }
    response = session.post(url, data=payload)
    response.encoding = "utf-8"
    return response.text


def fetch_night_trading(session, date, commodity_id="EXF") -> str:
    """
    抓取夜盤資料。
    """
    url = "https://www.taifex.com.tw/cht/3/futContractsDateAh"
    payload = {
        "queryType": "3",
        "goDay": "",
        "doQuery": "1",
        "dateaddcnt": "",
        "queryDate": date.strftime("%Y/%m/%d"),
        "commodityId": commodity_id,
    }
    response = session.post(url, data=payload)
    response.encoding = "utf-8"
    return response.text


def parse_day_trading(html):
    """
    解析日盤的 HTML 表格，提取自營商、投信和外資的多方、空方及多空淨額。
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"class": "table_f"})
    data = {}
    if not table:
        return data
    rows = table.find("tbody").find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        cols = cols[-13:]
        # print(F"cols:{" ".join([str(col.text).strip() for col in cols])} len:{len(cols)}")

        identity = cols[0].get_text(strip=True)
        if identity not in ["自營商", "投信", "外資"]:
            continue

        multi_text = cols[3].get_text(strip=True).replace(",", "").replace("X", "0")
        short_text = cols[5].get_text(strip=True).replace(",", "").replace("X", "0")
        net_text = cols[7].get_text(strip=True).replace(",", "").replace("X", "0")
        try:
            multi = int(multi_text) if multi_text else 0
            short = int(short_text) if short_text else 0
            net = int(net_text) if net_text else 0
        except ValueError:
            multi, short, net = 0, 0, 0
        if identity == "自營商":
            data["自營商多"] = multi
            data["自營商空"] = short
            data["自營商多空"] = net
        elif identity == "投信":
            data["投信多"] = multi
            data["投信空"] = short
            data["投信多空"] = net
        elif identity == "外資":
            data["外資多"] = multi
            data["外資空"] = short
            data["外資多空淨額"] = net
        # print(F"identity:{identity}, multi:{multi}, short:{short}, net:{net}")
    return data


def parse_night_trading(html):
    """
    解析夜盤的 HTML 表格，提取自營商、投信和外資的多方、空方及多空淨額。
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"class": "table_f"})
    data = {}
    if not table:
        return data
    rows = table.find("tbody").find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 9:
            continue
        identity = cols[2].get_text(strip=True)
        if identity not in ["自營商", "投信", "外資"]:
            continue
        # 提取多方口數、空方口數及多空淨額
        multi_text = cols[3].get_text(strip=True).replace(",", "").replace("X", "0")
        short_text = cols[5].get_text(strip=True).replace(",", "").replace("X", "0")
        net_text = cols[7].get_text(strip=True).replace(",", "").replace("X", "0")
        try:
            multi = int(multi_text) if multi_text else 0
            short = int(short_text) if short_text else 0
            net = int(net_text) if net_text else 0
        except ValueError:
            multi, short, net = 0, 0, 0
        if identity == "自營商":
            data["自營商夜盤多"] = multi
            data["自營商夜盤空"] = short
            data["自營商夜盤多空"] = net
        elif identity == "投信":
            data["投信夜盤多"] = multi
            data["投信夜盤空"] = short
            data["投信夜盤多空"] = net
        elif identity == "外資":
            data["外資夜盤多"] = multi
            data["外資夜盤空"] = short
            data["外資夜盤多空"] = net
    return data


def main():
    import sys

    print("請輸入日期區間（格式：YYYY/MM/DD - YYYY/MM/DD）。如果只輸入一個日期，則抓取該日資料。")
    date_input = input("請輸入日期區間（例如 2024/08/12 - 2024/08/20）：").strip()
    dates = re.split(r"\s*-\s*", date_input)
    if len(dates) == 1:
        start_date = dates[0]
        end_date = dates[0]
    elif len(dates) == 2:
        start_date, end_date = dates
    else:
        print("日期格式不正確。請使用 YYYY/MM/DD - YYYY/MM/DD 格式。")
        sys.exit(1)

    if not validate_date(start_date):
        print("開始日期格式不正確。請使用 YYYY/MM/DD 格式。")
        sys.exit(1)

    if not validate_date(end_date):
        print("結束日期格式不正確。請使用 YYYY/MM/DD 格式。")
        sys.exit(1)

    date_list = get_date_range(start_date, end_date)

    session = requests.Session()
    all_data = []
    for date in date_list:
        date_str = date.strftime("%Y/%m/%d")
        print(f"處理日期: {date_str}")
        day_html = fetch_day_trading(session, date)
        day_data = parse_day_trading(day_html)
        if not day_data:
            print(f"{date_str} 的日盤資料未找到或解析失敗。")
            continue
        night_html = fetch_night_trading(session, date)
        night_data = parse_night_trading(night_html)
        # 計算夜盤的多空淨額
        night_row = {
            "DATE": date_str,
            "自營商多": "X",
            "自營商空": "X",
            "自營商多空": day_data.get("自營商多空", 0)
            + (night_data.get("自營商夜盤多", 0) - night_data.get("自營商夜盤空", 0)),
            "投信多": "X",
            "投信空": "X",
            "投信多空": day_data.get("投信多空", 0) + (night_data.get("投信夜盤多", 0) - night_data.get("投信夜盤空", 0)),
            "外資多": "X",
            "外資空": "X",
            "外資多空淨額": day_data.get("外資多空淨額", 0)
            + (night_data.get("外資夜盤多", 0) - night_data.get("外資夜盤空", 0)),
        }
        # 日盤資料行
        day_row = {
            "DATE": date_str,
            "自營商多": day_data.get("自營商多", 0),
            "自營商空": day_data.get("自營商空", 0),
            "自營商多空": day_data.get("自營商多空", 0),
            "投信多": day_data.get("投信多", 0),
            "投信空": day_data.get("投信空", 0),
            "投信多空": day_data.get("投信多空", 0),
            "外資多": day_data.get("外資多", 0),
            "外資空": day_data.get("外資空", 0),
            "外資多空淨額": day_data.get("外資多空淨額", 0),
        }
        all_data.append(day_row)
        all_data.append(night_row)

    # 轉換為 DataFrame
    df = pd.DataFrame(all_data)
    # 儲存為 CSV
    df.to_csv("taifex_futures_data.csv", index=False, encoding="utf-8-sig")
    print("資料已儲存到 taifex_futures_data.csv")


def test():
    tz = timezone("Asia/Taipei")
    day_trading_df = pd.read_html(StringIO(fetch_day_trading(requests.Session(), datetime.now(tz))))[0]
    night_trading_df = pd.read_html(StringIO(fetch_night_trading(requests.Session(), datetime.now(tz))))[0]
    day_trade_csv = day_trading_df.to_csv()
    night_trade_csv = night_trading_df.to_csv()

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        openai_api_key=OPENAI_API_KEY,
    )
    data_view_prompt = "\n\n".join(
        [
            f"{table['name']} (in CSV format):\n```\n{table['csv']}\n```"
            for table in [
                {"name": "Day Trading DataFrame", "csv": day_trade_csv},
                {"name": "Night Trading DataFrame", "csv": night_trade_csv},
            ]
        ],
    )
    user_requirement = input("請輸入您的需求，例如需要提取哪些欄位或進行何種轉換：")

    prompt_template = PromptTemplate(
        input_variables=["raw_csv", "user_requirement"],
        template=(
            "You are a Python expert. Your task is to extract the required data "
            "from the provided CSV content and format it as specified by the user. "
            "Below is the data:\n\n{raw_csv}\n\n"
            "The user has the following requirement:\n{user_requirement}\n\n"
            "Write Python code to achieve this, starting directly with the logic. "
            "Do not include imports or function definitions. Ensure the code is "
            "clear, concise, and outputs the transformed data in the required format."
        ),
    )
    agent = prompt_template | llm
    # print(agent.invoke({"raw_csv": data_view_prompt, "user_requirement": user_requirement}).content)

    # Extracting the relevant columns for "未平倉餘額"
    print(day_trading_df.columns)
    day_trading_data = day_trading_df.xs("未平倉餘額", axis=1, level=1)

    # Calculate the total "未平倉餘額" (Open Interest)
    total_open_interest = day_trading_data.sum(axis=0)

    # Formatting the result as required
    result = total_open_interest.reset_index()
    result.columns = ["身份別", "未平倉餘額"]
    print(result)


if __name__ == "__main__":
    # main()
    test()
