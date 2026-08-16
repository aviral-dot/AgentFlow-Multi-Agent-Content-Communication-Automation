import streamlit as st
import requests
import time




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
                "query": query
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

        st.success("🟢 FastAPI Connected")

    else:

        st.error("🔴 FastAPI Offline")

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

        **Output Guardrail**
        ↓

        **Groq LLM**
        """
    )

    st.markdown("---")

    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = []

        st.rerun()




st.title("🤖 Multi-Agent AI Assistant")

st.markdown(
    "Blog generation and email automation powered by LangGraph."
)

st.markdown("---")




for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])




query = st.chat_input(
    "Ask the AI agent something..."
)




if query:

    

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query
        }
    )

    with st.chat_message("user"):

        st.markdown(query)


    

    with st.chat_message("assistant"):

        start_time = time.time()

        with st.spinner("🤔 Agents are working..."):

            result = send_message(query)

        elapsed_time = time.time() - start_time


        

        if result.get("error"):

            answer = (
                "❌ **Unable to connect to the backend.**\n\n"
                f"`{result['error']}`"
            )

            st.error(answer)


        
        elif result.get("blocked"):

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


            st.warning(answer)


            st.caption(
                f"Security stage: `{stage}`  •  "
                f"Response time: `{elapsed_time:.2f}s`"
            )


        

        elif result.get("success"):

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


            st.markdown(answer)


            st.caption(
                f"🤖 Agent: `{route}`  •  "
                f"⏱️ Response time: `{elapsed_time:.2f}s`"
            )


       

        else:

            answer = (
                "⚠️ **Unexpected response from backend.**"
            )

            st.warning(answer)


    

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


