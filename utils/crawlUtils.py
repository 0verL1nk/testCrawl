import os

from crawl4ai import BrowserConfig, LLMExtractionStrategy, LLMConfig, CrawlerRunConfig
from model import resultModel


def get_browser_config() -> BrowserConfig:
    return BrowserConfig(
        headless=True,
        verbose=True,
        user_agent_mode="random"
    )


def get_llm_config() -> LLMExtractionStrategy:
    llm_config = LLMConfig(base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                           provider="openai/qwen-flash",
                           api_token=os.getenv("DASHSCOPE_API_KEY"),
                           )
    return LLMExtractionStrategy(
        llm_config=llm_config,
        schema=resultModel.NewsResult.model_json_schema(),
        extraction_type="schema",
        input_format="markdown",
        instruction=("""
        Extract all the news with 'Title','Time','Link'.
        """),
        verbose=True,
    )


def get_crawler_config(css_selector: str, llm: LLMExtractionStrategy) -> CrawlerRunConfig:
    return CrawlerRunConfig(
        verbose=True,
        css_selector=css_selector,
        extraction_strategy=llm
    )
