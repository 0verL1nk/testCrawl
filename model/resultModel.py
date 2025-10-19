from pydantic import BaseModel

import pydantic
class NewsResult(BaseModel):
    Title: str=pydantic.Field(default="",description="The title of the news")
    Time: str=pydantic.Field(default="",description="The time of the news")
    Link: str=pydantic.Field(default="",description="The link of the news,the base url is http://opinion.people.com.cn")

