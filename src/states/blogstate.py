from typing import TypedDict
from pydantic import BaseModel,Field

class Blog(BaseModel):
    title:str=Field(description="the title of the blog post")
    content:str=Field(description="The main content of the blog post")

class Email(BaseModel):
    to: str
    subject: str
    body: str

class AgentState(TypedDict):
    query: str              

    route: str              

    blog: Blog

    email: Email

    response: str

    tool_result: dict

    approval: str
