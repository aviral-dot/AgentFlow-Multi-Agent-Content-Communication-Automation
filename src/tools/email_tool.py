# import sys

# from mcp import ClientSession
# from mcp.client.stdio import stdio_client
# from mcp.client.stdio import StdioServerParameters


# class EmailTool:

#     def __init__(self):

#         self.server = StdioServerParameters(
#             command=sys.executable,
#             args=["gmail_mcp_server.py"]
#         )

#     async def send(
#         self,
#         to: str,
#         subject: str,
#         body: str
#     ):

#         async with stdio_client(
#             self.server
#         ) as (read, write):

#             async with ClientSession(
#                 read,
#                 write
#             ) as session:

#                 await session.initialize()

#                 result = await session.call_tool(
#                     "send_email",
#                     {
#                         "to": to,
#                         "subject": subject,
#                         "body": body
#                     }
#                 )

#                 return result

import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import stdio_client
from mcp.client.stdio import StdioServerParameters


class EmailTool:

    def __init__(self):

        base_dir = Path(__file__).resolve().parents[2]

        self.server = StdioServerParameters(
            command=str(Path(sys.executable).resolve()),
            args=[
                str(base_dir / "gmail_mcp_server.py")
            ],
        )

    async def send(
        self,
        to: str,
        subject: str,
        body: str,
    ):

        async with stdio_client(
            self.server
        ) as (read, write):

            async with ClientSession(
                read,
                write
            ) as session:

                await session.initialize()

                result = await session.call_tool(
                    "send_email",
                    {
                        "to": to,
                        "subject": subject,
                        "body": body,
                    },
                )

                return result