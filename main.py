import asyncio
import json
import csv
from pathlib import Path

import utils.crawlUtils as utils
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

BASE_URL = "http://opinion.people.com.cn/GB/8213/353915/353916/index"
CSS_SELECTOR = "[class='t11']"


async def crawl_single_page(crawler, url: str, css_selector: str, llm_strategy) -> tuple:
    """
    爬取单个页面并返回数据
    返回: (data_list, success, is_404)
    """
    try:
        result = await crawler.arun(
            url=url,
            config=utils.get_crawler_config(css_selector, llm_strategy)
        )
        if result.success:
            data = json.loads(result.extracted_content)
            return data, True, False
        else:
            # 检查是否是404错误
            error_msg = str(result.error_message).lower()
            is_404 = '404' in error_msg or 'not found' in error_msg
            return [], False, is_404
    except Exception as e:
        error_msg = str(e).lower()
        is_404 = '404' in error_msg or 'not found' in error_msg
        return [], False, is_404


async def crawl_all_pages():
    """动态爬取所有页面，直到遇到404为止"""
    browser_config = utils.get_browser_config()
    llm_strategy = utils.get_llm_config()
    
    all_data = []
    page_num = 1  # 从0开始，0对应index.html，1对应index1.html
    consecutive_failures = 0  # 连续失败次数
    max_consecutive_failures = 3  # 最多允许连续失败3次
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        while True:
            # 生成URL
            url = f"{BASE_URL}{page_num}.html"
            
            # 爬取页面
            page_data, success, is_404 = await crawl_single_page(
                crawler, url, CSS_SELECTOR, llm_strategy
            )
            
            # 如果遇到404，停止爬取
            if is_404:
                break
            
            # 如果成功，重置失败计数器
            if success and page_data:
                all_data.extend(page_data)
                consecutive_failures = 0
                print(f"页面 {page_num}: {len(page_data)} 条")
            else:
                consecutive_failures += 1
                if consecutive_failures >= max_consecutive_failures:
                    break
            
            page_num += 1
            await asyncio.sleep(1)
        
        print(f"完成！共 {page_num-1} 页，{len(all_data)} 条数据")
        llm_strategy.show_usage()
    
    return all_data


def save_to_csv(data: list, filename: str = "news_data.csv"):
    """将数据保存为CSV文件"""
    if not data:
        print("没有数据可保存！")
        return
    
    output_path = Path(filename)
    
    # 只保存Title和Time字段
    fieldnames = ['Title', 'Time', 'Link']
    
    # 过滤数据，只保留需要的字段
    filtered_data = []
    for item in data:
        filtered_item = {key: item.get(key, '') for key in fieldnames}
        filtered_data.append(filtered_item)
    
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_data)
    
    print(f"已保存到: {output_path.absolute()}")


async def main():
    all_data = await crawl_all_pages()
    
    if all_data:
        save_to_csv(all_data, "news_data.csv")


if __name__ == "__main__":
    asyncio.run(main())
