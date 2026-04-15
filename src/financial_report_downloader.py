#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财务报表 PDF 下载工具
====================
从巨潮资讯网（cninfo.com.cn，证监会指定信息披露平台）下载上市公司财务报表 PDF 文件。

支持：
  - 按股票代码/公司名称下载
  - 按申万行业批量下载
  - 按报告类型筛选（年报 / 半年报 / 季报）
  - 断点续传（跳过已下载文件）
  - 下载限速、自动重试

用法示例：
  # 下载单只股票的最新年报
  python financial_report_downloader.py --stock 600519 --report-type annual

  # 下载银行业所有公司最新年报+半年报
  python financial_report_downloader.py --industry 银行 --report-type annual semi

  # 下载多只股票的所有报告类型
  python financial_report_downloader.py --stock 600519 000001 601318 --report-type all

  # 指定年份范围和输出目录
  python financial_report_downloader.py --stock 600519 --year 2023 2024 --output ./my_reports
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Sequence
from urllib.parse import quote

import requests

# ---------------------------------------------------------------------------
# 日志配置
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
CNINFO_SEARCH_URL = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
CNINFO_PDF_BASE = "http://static.cninfo.com.cn/"
DEFAULT_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "financial_reports"
)
REQUEST_DELAY = 0.6  # 请求间隔（秒），避免被巨潮封 IP
MAX_RETRIES = 3
PAGE_SIZE = 30  # 巨潮 API 单页最大 30 条

# 报告类型 → 巨潮搜索关键字映射
REPORT_TYPE_KEYWORDS: dict[str, list[str]] = {
    "annual": ["年度报告", "年报"],
    "semi": ["半年度报告", "半年报"],
    "q1": ["第一季度报告", "一季报"],
    "q3": ["第三季度报告", "三季报"],
}

# 报告类型 → 文件夹名称
REPORT_TYPE_DIR_NAMES: dict[str, str] = {
    "annual": "年报",
    "semi": "半年报",
    "q1": "一季报",
    "q3": "三季报",
}

# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Announcement:
    """单条公告记录"""

    ann_date: str  # 公告日期 YYYYMMDD
    stock_code: str  # 股票代码（6位纯数字）
    stock_name: str  # 股票简称
    title: str  # 公告标题
    pdf_url: str  # PDF 下载完整 URL
    file_name: str  # 建议保存的文件名


@dataclass
class DownloadResult:
    """下载结果统计"""

    total_found: int = 0
    downloaded: int = 0
    skipped: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 巨潮资讯网 API 客户端
# ---------------------------------------------------------------------------


class CNINFOClient:
    """巨潮资讯网公告查询 & PDF 下载客户端"""

    def __init__(
        self, delay: float = REQUEST_DELAY, max_retries: int = MAX_RETRIES
    ) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json, text/plain, */*",
                "Referer": "http://www.cninfo.com.cn/new/disclosure",
                "X-Requested-With": "XMLHttpRequest",
            }
        )
        self.delay = delay
        self.max_retries = max_retries

    # ----- 公告搜索 -----

    def search_announcements(
        self,
        stock_code: str = "",
        stock_name: str = "",
        search_key: str = "",
        start_date: str = "",
        end_date: str = "",
        category: str = "ndbg_szsh",  # 年度报告/半年度报告/季度报告 的分类代码
        page_num: int = 1,
    ) -> dict:
        """
        调用巨潮公告查询接口。

        注意：巨潮 API 的 stock 参数已失效，改用 searchkey 按公司名称搜索。
        search_key 和 stock_name 不会同时使用：如果有 stock_name 则用它做 searchkey，
        否则用 search_key 做关键词搜索。

        category 参数说明：
          - ndbg_szsh : 年度报告（沪深）
          - bdbg_szsh : 半年度报告
          - jdbg_szsh : 季度报告（一季报/三季报）

        返回巨潮原始 JSON 响应。
        """
        # 巨潮 API 的 stock 参数已失效（返回 0 结果），
        # 改用 searchkey 按公司名称搜索，然后通过返回的 secCode 过滤。
        effective_searchkey = stock_name if stock_name else search_key

        payload: dict[str, str | int] = {
            "pageNum": page_num,
            "pageSize": PAGE_SIZE,
            "column": "",  # 不限定交易所，searchkey 模式下无需
            "tabName": "fulltext",
            "plate": "",
            "stock": "",
            "searchkey": effective_searchkey,
            "secid": "",
            "category": category,
            "trade": "",
            "seDate": f"{start_date}~{end_date}" if start_date or end_date else "",
            "sortName": "",
            "sortType": "",
            "isHLtitle": "true",
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.session.post(CNINFO_SEARCH_URL, data=payload, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                time.sleep(self.delay)
                return data
            except (requests.RequestException, ValueError) as exc:
                logger.warning("巨潮 API 请求失败 (第 %d 次): %s", attempt, exc)
                if attempt < self.max_retries:
                    time.sleep(self.delay * 2 * attempt)
                else:
                    raise

        return {}

    def list_announcements(
        self,
        stock_code: str = "",
        stock_name: str = "",
        search_key: str = "",
        start_date: str = "",
        end_date: str = "",
        category: str = "ndbg_szsh",
    ) -> list[Announcement]:
        """
        获取所有页的公告列表。

        当 stock_name 提供时，使用 searchkey=公司名称 搜索，
        然后按 secCode 过滤仅保留目标公司的公告。
        """
        all_anns: list[Announcement] = []
        page_num = 1

        while True:
            data = self.search_announcements(
                stock_code=stock_code,
                stock_name=stock_name,
                search_key=search_key,
                start_date=start_date,
                end_date=end_date,
                category=category,
                page_num=page_num,
            )
            ann_list = data.get("announcements") or []
            total_ann = data.get("totalAnnouncement", 0)

            if not ann_list:
                break

            for item in ann_list:
                title = self._clean_html(item.get("announcementTitle", ""))
                adj_url = item.get("adjunctUrl", "")
                if not adj_url:
                    continue

                # 按股票代码过滤：当提供 stock_code 时，只保留目标公司的公告
                # （因为 searchkey 按名称搜索可能返回名称包含该关键字的其他公司）
                sec_code = str(item.get("secCode", "")).strip()
                if stock_code and sec_code != stock_code:
                    continue

                # announcementTime 可能是整数（Unix毫秒时间戳）或空字符串
                ann_time_raw = item.get("announcementTime", "")
                if isinstance(ann_time_raw, int):
                    ann_date_str = datetime.fromtimestamp(ann_time_raw / 1000).strftime(
                        "%Y%m%d"
                    )
                else:
                    ann_date_str = str(ann_time_raw)[:8] if ann_time_raw else ""
                ann = Announcement(
                    ann_date=ann_date_str,
                    stock_code=str(item.get("secCode", "")).strip(),
                    stock_name=item.get("secName", "").strip(),
                    title=title,
                    pdf_url=CNINFO_PDF_BASE + adj_url,
                    file_name=self._make_filename(item, title),
                )
                all_anns.append(ann)

            if len(all_anns) >= total_ann or len(ann_list) < PAGE_SIZE:
                break

            page_num += 1

        return all_anns

    # ----- PDF 下载 -----

    def download_pdf(self, url: str, save_path: str) -> bool:
        """下载 PDF 文件，返回是否成功"""
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.session.get(url, timeout=60, stream=True)
                resp.raise_for_status()

                # 检查是否真的是 PDF
                content_type = resp.headers.get("Content-Type", "")
                if "pdf" not in content_type.lower() and not url.endswith(".pdf"):
                    logger.warning("非 PDF 响应 (%s): %s", content_type, url)
                    return False

                tmp_path = save_path + ".tmp"
                with open(tmp_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                # 原子写入：先写临时文件再重命名
                os.replace(tmp_path, save_path)
                return True

            except requests.RequestException as exc:
                logger.warning("下载失败 (第 %d 次) %s: %s", attempt, url, exc)
                if attempt < self.max_retries:
                    time.sleep(self.delay * attempt)

        return False

    # ----- 辅助方法 -----

    @staticmethod
    def _clean_html(text: str) -> str:
        """去除巨潮返回标题中的 HTML 高亮标签"""
        return re.sub(r"<[^>]+>", "", text).strip()

    @staticmethod
    def _make_filename(item: dict, clean_title: str) -> str:
        """根据公告信息生成合理的文件名"""

        # 清理 HTML 高亮标签（如 <em>搜索关键词</em>）
        def clean_text(text: str) -> str:
            return re.sub(r"<[^>]+>", "", text).strip()

        sec_code = clean_text(str(item.get("secCode", ""))).strip()
        sec_name = clean_text(item.get("secName", ""))
        ann_time_raw = item.get("announcementTime", "")
        if isinstance(ann_time_raw, int):
            ann_time = datetime.fromtimestamp(ann_time_raw / 1000).strftime("%Y%m%d")
        else:
            ann_time = str(ann_time_raw)[:8] if ann_time_raw else ""
        # 清理文件名中的非法字符
        safe_title = re.sub(r'[\\/:*?"<>|]', "_", clean_title)
        if safe_title:
            return f"{sec_name}_{sec_code}_{ann_time}_{safe_title}.pdf"
        return f"{sec_name}_{sec_code}_{ann_time}.pdf"


# ---------------------------------------------------------------------------
# Tushare 行业 → 股票映射（可选依赖）
# ---------------------------------------------------------------------------


def get_stocks_by_industry(industry_name: str) -> list[dict[str, str]]:
    """
    通过 Tushare 申万行业分类，获取指定行业下所有上市公司的代码和名称。

    返回: [{"ts_code": "600519.SH", "code": "600519", "name": "贵州茅台"}, ...]
    """
    try:
        import tushare as ts
    except ImportError:
        logger.error("需要安装 tushare: pip install tushare")
        sys.exit(1)

    token = os.getenv("TUSHARE_TOKEN") or ts.get_token()
    if not token:
        logger.error("未检测到 TUSHARE_TOKEN，请设置环境变量或先执行 ts.set_token()")
        sys.exit(1)

    pro = ts.pro_api(token)

    # 1. 查找申万行业分类中匹配的行业
    try:
        classify_df = pro.index_classify(level="L1", src="SW2021")
    except Exception as exc:
        logger.error("获取申万行业分类失败: %s", exc)
        return []

    # 模糊匹配行业名
    match = classify_df[
        classify_df["industry_name"].str.contains(industry_name, na=False)
    ]
    if match.empty:
        logger.error(
            "未找到匹配的行业 '%s'，可选行业: %s",
            industry_name,
            classify_df["industry_name"].tolist(),
        )
        return []

    industry_code = match.iloc[0]["index_code"]
    matched_name = match.iloc[0]["industry_name"]
    logger.info("匹配到申万一级行业: %s (%s)", matched_name, industry_code)

    # 2. 获取该行业成分股（优先 index_member_all，备用 stock_basic）
    stocks: list[dict[str, str]] = []

    # 方案 A: index_member_all
    try:
        member_df = pro.index_member_all(
            index_code=industry_code, level="L1", src="SW2021"
        )
    except Exception as exc:
        logger.warning("index_member_all 查询失败: %s", exc)
        member_df = None

    if member_df is not None and not member_df.empty:
        for _, row in member_df.iterrows():
            ts_code = str(row.get("con_code", "") or row.get("ts_code", ""))
            if not ts_code:
                continue
            code = ts_code.split(".")[0]
            name = str(row.get("con_name", "") or row.get("name", ""))
            stocks.append({"ts_code": ts_code, "code": code, "name": name})
        logger.info(
            "通过 index_member_all 获取 '%s' 成分股: %d 只", matched_name, len(stocks)
        )

    # 方案 B: stock_basic 的 industry 字段（更稳定、权限要求低）
    if not stocks:
        logger.info("index_member_all 无数据，改用 stock_basic 按行业字段查询...")
        try:
            basic_df = pro.stock_basic(
                exchange="",
                list_status="L",
                fields="ts_code,symbol,name,industry",
            )
            matched = basic_df[
                basic_df["industry"].str.contains(industry_name, na=False)
            ]
            for _, row in matched.iterrows():
                ts_code = str(row["ts_code"])
                code = str(row["symbol"])
                name = str(row["name"])
                stocks.append({"ts_code": ts_code, "code": code, "name": name})
            logger.info(
                "通过 stock_basic 获取 '%s' 成分股: %d 只", industry_name, len(stocks)
            )
        except Exception as exc:
            logger.error("stock_basic 查询也失败: %s", exc)
            return []

    if not stocks:
        logger.warning("行业 '%s' 下未找到成分股", matched_name)
        return []

    return stocks


def resolve_stock_codes(
    stock_args: Sequence[str] | None,
    industry_arg: str | None,
) -> list[dict[str, str]]:
    """
    解析用户输入的股票代码/名称/行业，返回标准化的股票列表。

    返回: [{"code": "600519", "name": "贵州茅台"}, ...]
    """
    stocks: list[dict[str, str]] = []

    # 行业模式
    if industry_arg:
        stocks = get_stocks_by_industry(industry_arg)
        return stocks

    # 股票代码/名称模式
    if not stock_args:
        logger.error("请指定 --stock 或 --industry")
        return []

    for arg in stock_args:
        arg = arg.strip()
        # 纯数字 → 当作股票代码
        if arg.isdigit() and len(arg) == 6:
            stocks.append({"code": arg, "name": ""})
        else:
            # 尝试通过 Tushare 解析名称
            try:
                import tushare as ts

                token = os.getenv("TUSHARE_TOKEN") or ts.get_token()
                if token:
                    pro = ts.pro_api(token)
                    df = pro.stock_basic(
                        exchange="",
                        list_status="L",
                        fields="ts_code,symbol,name",
                    )
                    match = df[df["name"].str.contains(arg, na=False)]
                    if not match.empty:
                        for _, row in match.iterrows():
                            stocks.append(
                                {
                                    "code": str(row["symbol"]),
                                    "name": str(row["name"]),
                                }
                            )
                    else:
                        logger.warning("未找到匹配 '%s' 的股票", arg)
                else:
                    logger.warning(
                        "无 TUSHARE_TOKEN，无法按名称 '%s' 查询，请直接输入 6 位股票代码",
                        arg,
                    )
            except ImportError:
                logger.warning(
                    "tushare 未安装，无法按名称查询，请直接输入 6 位股票代码"
                )
                stocks.append({"code": arg, "name": ""})

    return stocks


# ---------------------------------------------------------------------------
# 报告类型 → 巨潮 category 映射
# ---------------------------------------------------------------------------


def report_types_to_categories(
    report_types: Sequence[str],
) -> list[tuple[str, str, list[str], list[str]]]:
    """
    将用户指定的报告类型转换为巨潮查询参数。

    返回: [(category_code, dir_name, filter_keywords, exclude_keywords), ...]
    """
    results: list[tuple[str, str, list[str], list[str]]] = []

    type_map = {
        "annual": ("ndbg_szsh", "年报", REPORT_TYPE_KEYWORDS["annual"], ["半年度"]),
        "semi": ("bdbg_szsh", "半年报", REPORT_TYPE_KEYWORDS["semi"], []),
        "q1": ("jdbg_szsh", "一季报", REPORT_TYPE_KEYWORDS["q1"], []),
        "q3": ("jdbg_szsh", "三季报", REPORT_TYPE_KEYWORDS["q3"], []),
    }

    for rt in report_types:
        if rt in type_map:
            cat, dir_name, keywords, exclude = type_map[rt]
            results.append((cat, dir_name, keywords, exclude))

    return results


# ---------------------------------------------------------------------------
# 核心下载逻辑
# ---------------------------------------------------------------------------


def filter_financial_reports(
    announcements: list[Announcement],
    keywords: list[str],
    year_range: tuple[str, str] | None = None,
    exclude_terms: list[str] | None = None,
) -> list[Announcement]:
    """
    按关键字和年份筛选财务报告公告。

    筛选逻辑：标题中包含任一关键字（且不包含排除关键字），且公告日期在年份范围内。
    """
    filtered: list[Announcement] = []
    for ann in announcements:
        # 关键字匹配（正向）
        if not any(kw in ann.title for kw in keywords):
            continue
        # 排除关键字（反向过滤）
        if exclude_terms and any(ex in ann.title for ex in exclude_terms):
            continue
        # 年份过滤
        if year_range:
            ann_year = ann.ann_date[:4]
            if ann_year < year_range[0] or ann_year > year_range[1]:
                continue
        filtered.append(ann)
    return filtered


def download_reports(
    client: CNINFOClient,
    stocks: list[dict[str, str]],
    report_types: Sequence[str],
    year_range: tuple[str, str] | None,
    output_dir: str,
) -> DownloadResult:
    """
    批量下载指定股票的财务报告 PDF。

    Parameters
    ----------
    client : CNINFOClient
    stocks : [{"code": "600519", "name": "贵州茅台"}, ...]
    report_types : ["annual", "semi", "q1", "q3"] 的子集
    year_range : (start_year, end_year) 如 ("2022", "2024")
    output_dir : 输出根目录
    """
    result = DownloadResult()
    categories = report_types_to_categories(report_types)

    for stock in stocks:
        code = stock["code"]
        name = stock.get("name", "")

        for category_code, dir_name, keywords, exclude_terms in categories:
            # 搜索公告
            logger.info("搜索 %s(%s) 的 %s ...", name or code, code, dir_name)

            try:
                anns = client.list_announcements(
                    stock_code=code,
                    stock_name=name,
                    category=category_code,
                )
            except Exception as exc:
                logger.error("搜索 %s %s 失败: %s", code, dir_name, exc)
                result.errors.append(f"{code} {dir_name}: 搜索失败 {exc}")
                continue

            # 筛选财务报告
            filtered = filter_financial_reports(
                anns, keywords, year_range, exclude_terms
            )
            result.total_found += len(filtered)

            if not filtered:
                logger.info(
                    "  %s(%s) 无符合条件的 %s 公告", name or code, code, dir_name
                )
                continue

            logger.info("  找到 %d 条符合条件的 %s 公告", len(filtered), dir_name)

            # 创建输出目录
            stock_dir_name = f"{name}_{code}" if name else code
            save_dir = os.path.join(output_dir, stock_dir_name, dir_name)
            os.makedirs(save_dir, exist_ok=True)

            # 逐条下载
            for ann in filtered:
                save_path = os.path.join(save_dir, ann.file_name)

                # 跳过已下载
                if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                    logger.debug("  跳过已存在: %s", ann.file_name)
                    result.skipped += 1
                    continue

                logger.info("  下载: %s → %s", ann.title[:50], save_path)

                ok = client.download_pdf(ann.pdf_url, save_path)
                if ok:
                    result.downloaded += 1
                else:
                    result.failed += 1
                    result.errors.append(f"{ann.stock_code} {ann.title}: 下载失败")
                    # 清理失败的临时文件
                    tmp_path = save_path + ".tmp"
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="从巨潮资讯网下载上市公司财务报表 PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 下载贵州茅台最新年报
  python financial_report_downloader.py --stock 600519 --report-type annual

  # 下载招商银行 2023-2024 年报和半年报
  python financial_report_downloader.py --stock 600036 --report-type annual semi --year 2023 2024

  # 下载银行业全部公司的最新年报
  python financial_report_downloader.py --industry 银行 --report-type annual

  # 下载所有类型的报告
  python financial_report_downloader.py --stock 600519 --report-type all
        """,
    )
    parser.add_argument(
        "--stock",
        nargs="+",
        default=None,
        help="股票代码（6 位数字）或公司名称（需 TUSHARE_TOKEN），支持多个",
    )
    parser.add_argument(
        "--industry",
        type=str,
        default=None,
        help="申万一级行业名称（如 银行、电子、医药生物），批量下载该行业所有公司（需 TUSHARE_TOKEN）",
    )
    parser.add_argument(
        "--report-type",
        nargs="+",
        default=["annual"],
        choices=["annual", "semi", "q1", "q3", "all"],
        help="报告类型: annual(年报) semi(半年报) q1(一季报) q3(三季报) all(全部)，默认 annual",
    )
    parser.add_argument(
        "--year",
        nargs="+",
        default=None,
        help="年份范围，如 --year 2023 或 --year 2022 2024，默认不限",
    )
    parser.add_argument(
        "--latest",
        action="store_true",
        default=False,
        help="只下载最近一年的报告（自动计算最新年份）",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help=f"输出目录，默认: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=REQUEST_DELAY,
        help=f"请求间隔秒数，默认: {REQUEST_DELAY}",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # 处理 report-type
    report_types = args.report_type
    if "all" in report_types:
        report_types = ["annual", "semi", "q1", "q3"]

    # 处理年份范围
    year_range: tuple[str, str] | None = None
    if args.latest:
        # 自动计算最新年份
        # 年报在每年4月发布，所以次年5月开始可以下载当年年报
        # 但到次年4月时，当年年报已经完全披露
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        if current_month <= 4:
            # 1-4月：最新可下载是去年年报（如2026年4月时是2025年）
            latest_year = str(current_year - 1)
        else:
            # 5-12月：最新可下载是当年年报（如2026年10月时是2026年）
            latest_year = str(current_year)
        year_range = (latest_year, latest_year)
        logger.info("  自动限定最新年份: %s", latest_year)
    elif args.year:
        years = sorted(args.year)
        year_range = (years[0], years[-1])

    # 解析股票列表
    stocks = resolve_stock_codes(args.stock, args.industry)
    if not stocks:
        logger.error("未找到任何股票，请检查输入参数")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("财务报表 PDF 下载工具")
    logger.info("  股票数量: %d", len(stocks))
    logger.info("  报告类型: %s", ", ".join(report_types))
    if year_range:
        logger.info("  年份范围: %s ~ %s", year_range[0], year_range[1])
    logger.info("  输出目录: %s", os.path.abspath(args.output))
    logger.info("=" * 60)

    # 初始化客户端
    client = CNINFOClient(delay=args.delay)

    # 执行下载
    result = download_reports(
        client=client,
        stocks=stocks,
        report_types=report_types,
        year_range=year_range,
        output_dir=args.output,
    )

    # 输出统计
    logger.info("=" * 60)
    logger.info("下载完成")
    logger.info("  找到公告: %d 条", result.total_found)
    logger.info("  新下载:   %d 个", result.downloaded)
    logger.info("  跳过已有: %d 个", result.skipped)
    logger.info("  失败:     %d 个", result.failed)
    if result.errors:
        logger.info("  错误详情:")
        for err in result.errors[:10]:
            logger.info("    - %s", err)
        if len(result.errors) > 10:
            logger.info("    ... 共 %d 条错误", len(result.errors))
    logger.info("  文件保存: %s", os.path.abspath(args.output))
    logger.info("=" * 60)

    if result.failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
