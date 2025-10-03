import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
import traceback
from chains import Chain
from portfolio import Portfolio
from utils import clean_text

# ----------------------
# Main Streamlit App
# ----------------------
def create_streamlit_app():
    st.title("📧 Cold Mail Generator")
    st.write("App loaded ✅")  # Immediate debug/UI feedback

    url_input = st.text_input(
        "Enter a Job Posting URL:",
        value="https://careers.nike.com/senior-aiml-engineer/job/R-66196"
    )
    submit_button = st.button("Submit")

    # Lazy initialization placeholders
    llm = None
    portfolio = None

    if submit_button:
        with st.spinner("Initializing LLM and Portfolio…"):
            try:
                # Initialize heavy objects only when needed
                llm = Chain()
                portfolio = Portfolio()
            except Exception as e:
                st.error(f"Failed to initialize Chain/Portfolio: {e}")
                st.text(traceback.format_exc())

                # Fallbacks
                class DummyLLM:
                    def extract_jobs(self, data):
                        return [{"role": "Test Role", "skills": ["Python"], "description": "Test job"}]

                    def write_mail(self, job, links):
                        return f"Hello, this is a test email for {job['role']}. Portfolio: {links}"

                class DummyPortfolio:
                    def load_portfolio(self): pass
                    def query_links(self, skills): return ["https://example.com"]

                llm = DummyLLM()
                portfolio = DummyPortfolio()

        # Processing the URL
        with st.spinner("Processing the URL…"):
            try:
                
                loader = WebBaseLoader(url_input)
                docs = loader.load()
                
                if not docs:
                    st.error("No document loaded by WebBaseLoader.")
                    return

                document = docs[0]
                
                data = clean_text(document.page_content)
                

                portfolio.load_portfolio()
                

                jobs = llm.extract_jobs(data)
                st.write("Jobs extracted:", len(jobs))
                if not jobs:
                    st.warning("No jobs extracted from the URL.")
                    return

                for job in jobs:
                    skills = job.get('skills', [])
                    links = portfolio.query_links(skills)
                    email = llm.write_mail(job, links)

                    st.subheader(f"Generated Email for {job.get('role', 'Unknown Role')}")
                    st.markdown(email, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"An Error Occurred: {e}")
                st.text(traceback.format_exc())

# ----------------------
# Entry point
# ----------------------
if __name__ == "__main__":
    create_streamlit_app()
