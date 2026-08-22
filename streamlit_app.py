import streamlit as st
import requests
import time
import uuid


FASTAPI_URL = "http://localhost:8000"


st.set_page_config(
    page_title="Multi-Agent AI Assistant",
    page_icon="🤖",
    layout="centered"
)


st.markdown(
    """
    <style>

    .stButton > button {
        width: 100%;
        font-weight: bold;
    }

    </style>
    """,
    unsafe_allow_html=True
)




if "messages" not in st.session_state:

    st.session_state.messages = []


if "pending_approval" not in st.session_state:

    st.session_state.pending_approval = None


# Create ONE thread ID for the current conversation.
# It survives Streamlit reruns.
if "thread_id" not in st.session_state:

    st.session_state.thread_id = str(uuid.uuid4())




def check_backend():
    """Check whether FastAPI backend is running."""

    try:

        response = requests.get(
            FASTAPI_URL,
            timeout=5
        )

        return response.status_code == 200

    except requests.exceptions.RequestException:

        return False




def send_message(query):
    """Send user query to FastAPI backend."""

    try:

        response = requests.post(
            f"{FASTAPI_URL}/chat",
            json={
                "query": query,
                "thread_id": st.session_state.thread_id
            },
            timeout=120
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:

        return {
            "success": False,
            "blocked": False,
            "error": str(e)
        }



def send_email_decision(
    thread_id,
    decision
):
    """Resume the paused LangGraph email workflow."""

    try:

        response = requests.post(
            f"{FASTAPI_URL}/email/approval",
            json={
                "thread_id": thread_id,
                "decision": decision
            },
            timeout=120
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:

        return {
            "success": False,
            "blocked": False,
            "error": str(e)
        }




with st.sidebar:

    st.title("⚙️ System")

    if check_backend():

        st.success(
            "🟢 FastAPI Connected"
        )

    else:

        st.error(
            "🔴 FastAPI Offline"
        )


    st.markdown("---")


    st.markdown("### Architecture")


    st.markdown(
        """
        **Streamlit**
        ↓

        **FastAPI**
        ↓

        **Input Guardrail**
        ↓

        **LangGraph**
        ↓

        **Multi-Agent System**
        ↓

        **Human Approval**
        ↓

        **Gmail MCP**
        ↓

        **Gmail**
        """
    )


    st.markdown("---")


    # Display current conversation/thread ID
    st.caption(
        f"Conversation ID: `{st.session_state.thread_id}`"
    )


    st.markdown("---")


    if st.button(
        "🗑️ Clear Chat"
    ):

        st.session_state.messages = []

        st.session_state.pending_approval = None

        # Start a completely new conversation
        st.session_state.thread_id = str(uuid.uuid4())

        st.rerun()




st.title(
    "🤖 Multi-Agent AI Assistant"
)


st.markdown(
    "Blog generation and email automation powered by LangGraph."
)


st.markdown("---")




for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# HUMAN APPROVAL UI
# ============================================================

if st.session_state.pending_approval:

    approval_data = (
        st.session_state.pending_approval
    )

    approval = approval_data.get(
        "approval",
        {}
    )

    email = approval.get(
        "email",
        {}
    )

    thread_id = approval_data.get(
        "thread_id"
    )


    st.markdown("---")


    st.warning(
        "⚠️ Human approval required before sending this email."
    )


    st.markdown(
        "### 📧 Email Preview"
    )


    st.markdown(
        f"**To:** `{email.get('to', '')}`"
    )


    st.markdown(
        f"**Subject:** {email.get('subject', '')}"
    )


    st.markdown(
        "**Body:**"
    )


    st.text_area(
        "Email Body",
        value=email.get(
            "body",
            ""
        ),
        height=200,
        disabled=True,
        label_visibility="collapsed"
    )


    st.caption(
        "Review the email carefully before approving."
    )


    st.markdown("---")


    col1, col2 = st.columns(2)


    with col1:

        approve_clicked = st.button(
            "✅ Approve",
            key=f"approve_{thread_id}",
            use_container_width=True
        )


    with col2:

        reject_clicked = st.button(
            "❌ Reject",
            key=f"reject_{thread_id}",
            use_container_width=True
        )


   

    if approve_clicked:

        with st.spinner(
            "Sending approved email..."
        ):

            decision_result = send_email_decision(
                thread_id,
                "approve"
            )


        if decision_result.get(
            "success"
        ):

            st.success(
                "✅ Email approved and sent successfully."
            )


            st.session_state.pending_approval = None


            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": (
                        "✅ **Email approved and sent successfully.**"
                    )
                }
            )


            st.rerun()


        else:

            error_message = decision_result.get(
                "error",
                "Failed to approve the email."
            )


            st.error(
                f"❌ {error_message}"
            )


    

    if reject_clicked:

        with st.spinner(
            "Rejecting email..."
        ):

            decision_result = send_email_decision(
                thread_id,
                "reject"
            )


        if decision_result.get(
            "success"
        ):

            st.info(
                "❌ Email rejected. Nothing was sent."
            )


            st.session_state.pending_approval = None


            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": (
                        "❌ **Email rejected. Nothing was sent.**"
                    )
                }
            )


            st.rerun()


        else:

            error_message = decision_result.get(
                "error",
                "Failed to reject the email."
            )


            st.error(
                f"❌ {error_message}"
            )




query = st.chat_input(
    "Ask assisstant something..."
)


if query:

    

    if st.session_state.pending_approval:

        st.warning(
            "⚠️ Please approve or reject the pending email first."
        )

        st.stop()


    
    st.session_state.messages.append(
        {
            "role": "user",
            "content": query
        }
    )


    with st.chat_message(
        "user"
    ):

        st.markdown(
            query
        )


    

    with st.chat_message(
        "assistant"
    ):

        start_time = time.time()


        with st.spinner(
            "🤔 Agents are working..."
        ):

            result = send_message(
                query
            )


        elapsed_time = (
            time.time() - start_time
        )


        

        if result.get(
            "error"
        ):

            answer = (
                "❌ **Unable to connect to the backend.**\n\n"
                f"`{result['error']}`"
            )


            st.error(
                answer
            )


        
        elif result.get(
            "blocked"
        ):

            stage = result.get(
                "stage",
                "security"
            )


            reason = result.get(
                "reason",
                "Request blocked by security guardrail."
            )


            if stage == "input":

                answer = (
                    "🛡️ **Request blocked**\n\n"
                    "Your request was blocked by the "
                    "**input security guardrail**."
                )


            elif stage == "output":

                answer = (
                    "🛡️ **Response blocked**\n\n"
                    "The generated response was blocked by "
                    "the **output security guardrail**."
                )


            else:

                answer = (
                    "🛡️ **Request blocked**\n\n"
                    f"{reason}"
                )


            st.warning(
                answer
            )


            st.caption(
                f"Security stage: `{stage}`  •  "
                f"Response time: `{elapsed_time:.2f}s`"
            )


        
        elif (
            result.get("success")
            and
            result.get("status")
            == "approval_required"
        ):

            st.session_state.pending_approval = result


            answer = (
                "⚠️ **Email generated. "
                "Human approval is required before sending.**"
            )


            st.warning(
                answer
            )


            st.caption(
                f"👤 Human approval required  •  "
                f"⏱️ Response time: `{elapsed_time:.2f}s`"
            )


       
        elif result.get(
            "success"
        ):

            data = result.get(
                "data",
                {}
            )


            answer = data.get(
                "response",
                "Request completed successfully."
            )


            route = data.get(
                "route",
                "unknown"
            )


            st.markdown(
                answer
            )


            st.caption(
                f"🤖 Agent: `{route}`  •  "
                f"⏱️ Response time: `{elapsed_time:.2f}s`"
            )


        

        else:

            answer = (
                "⚠️ **Unexpected response from backend.**"
            )


            st.warning(
                answer
            )


   

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


    

    if result.get(
        "status"
    ) == "approval_required":

        st.rerun()