def approve_email(self, state: AgentState):

        email = state["email"]

        decision = interrupt(
            {
                "type": "email_approval",
                "message": "Please approve or reject this email before sending.",
                "email": {
                    "to": email["to"],
                    "subject": email["subject"],
                    "body": email["body"]
                }
            }
        )

        return {
            "approval": decision
        }