import base64
from pathlib import Path
from email.mime.text import MIMEText

from mcp.server.mcpserver import MCPServer
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build




mcp = MCPServer("gmail-server")




SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]



BASE_DIR = Path(__file__).resolve().parent


TOKEN_FILE = BASE_DIR / "token.json"




def get_gmail_service():
    """
    Load OAuth credentials from token.json
    and create a Gmail API service.
    """

  
    if not TOKEN_FILE.exists():
        raise FileNotFoundError(
            f"token.json not found at: {TOKEN_FILE}. "
            "Run gmail_Auth.py first."
        )

  

    credentials = Credentials.from_authorized_user_file(
        str(TOKEN_FILE),
        SCOPES,
    )

   
    service = build(
        "gmail",
        "v1",
        credentials=credentials,
    )

    return service




@mcp.tool()
def send_email(
    to: str,
    subject: str,
    body: str,
) -> dict:
    """
    Send an email through Gmail.
    """

    try:

      

        gmail = get_gmail_service()

       

        message = MIMEText(
            body,
            "plain",
            "utf-8",
        )

        message["To"] = to
        message["Subject"] = subject

       

        raw_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()

        gmail_message = {
            "raw": raw_message
        }

        
        result = (
            gmail.users()
            .messages()
            .send(
                userId="me",
                body=gmail_message,
            )
            .execute()
        )

     
        return {
            "success": True,
            "message": "Email sent successfully",
            "message_id": result.get("id"),
        }

    except Exception as e:

       

        return {
            "success": False,
            "message": str(e),
        }




if __name__ == "__main__":

    mcp.run(
        transport="stdio"
    )