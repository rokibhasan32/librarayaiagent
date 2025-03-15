import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from groq import Groq
from fuzzywuzzy import process
from dotenv import load_dotenv

# ----------------------------- #
# Initialization & Configuration
# ----------------------------- #
def load_css():
    """Load external CSS styles"""
    try:
        with open("styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("CSS stylesheet not found!")

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# ----------------------------- #
# Data Loading
# ----------------------------- #
@st.cache_data
def load_books():
    try:
        return pd.read_csv("books.csv")
    except FileNotFoundError:
        st.error("❌ Error: 'books.csv' file not found!")
        return pd.DataFrame()

books = load_books()
due_dates = {}

# ----------------------------- #
# Library Services Configuration
# ----------------------------- #
library_services = {
    # ... [Keep the exact same library_services dictionary from original code] ...
    "research consultation": {
        "url": "https://library.daffodilvarsity.edu.bd/research-consultation",
        "info": "Contact the library for research consultation details.",
        "keywords": ["research", "thesis", "consultation", "academic support"]
    },
    "resources acquisition": {
        "url": "https://docs.google.com/document/d/1j7KyQiI1Fivqzi4MPjKNQeTMWll932xw/edit",
        "info": "Acquire books, journals, and periodicals through the library website.",
        "keywords": ["acquisition", "ordering", "materials request"]
    },
    "catalog search service (opac)": {
        "url": "http://opac.daffodilvarsity.edu.bd/",
        "info": "Search for books using the OPAC system.",
        "keywords": ["catalog", "search", "database", "OPAC"],
        "contact": {
            "Dr. Md. Milan Khan": {
                "email": "librarian@daffodilvarsity.edu.bd",
                "phone": "01713493004",
                "ip_phone": "65266"
            },
            "Md. Rashed Nizami": {
                "email": "library2@daffodilvarsity.edu.bd",
                "phone": "+8801847334849",
                "ip_phone": "65269"
            }
        }
    },
    "library membership": {
        "url": "https://library.daffodilvarsity.edu.bd",
        "info": "Automatic membership for DIU students",
        "keywords": ["membership", "access", "privileges", "registration"]
    },
    "library circulation service": {
        "url": "http://opac.daffodilvarsity.edu.bd/",
        "info": "Issue, return, and renew books and journals.",
        "keywords": ["circulation", "borrowing", "returns", "renewals"]
    },
    "koha": {
        "url": "http://koha.daffodilvarsity.edu.bd/",
        "info": "Integrated library system for circulation.",
        "keywords": ["ILS", "management system", "automation"]
    },
    "e-library": {
        "url": "https://archives.daffodilvarsity.edu.bd/login",
        "info": "Access digital resources through the e-library portal.",
        "keywords": ["digital", "e-resources", "online access", "e-books"]
    },
    "award": {
        "url": "https://archives.daffodilvarsity.edu.bd/login",
        "info": (
            "### *DIU Library Award – Library Excellence Award*  \n\n"
            "Daffodil International University (DIU) *Central Library* recognizes students who actively engage with library resources through the *Library Excellence Award*. "
            "This award encourages students to develop strong reading and research habits.  \n\n"
            "#### *1. Purpose of the Award:*  \n"
            "- To recognize and reward students who make the best use of DIU library resources  \n"
            "- To encourage academic excellence through reading and research  \n"
            "- To create a reading-friendly culture among students  \n\n"
            "#### *2. Award Categories (Past Examples):*  \n"
            "- *Best Reader Award:* Given to students who borrow and read the most books  \n"
            "- *Best Researcher Award:* Awarded to those who utilize the library's research materials effectively  \n"
            "- *Active Library User Award:* For students who engage in various library activities  \n\n"
            "#### *3. How to Qualify for the Award:*  \n"
            "- Frequently borrow and read books from the DIU Central Library  \n"
            "- Participate in library activities and research initiatives  \n"
            "- Maintain a record of active engagement with library resources  \n\n"
            "#### *4. Recent Award Ceremony:*  \n"
            "- Took place on *November 20, 2024* at **Kabi Nazrul Eduplex, DIU Library**  \n\n"
            "#### *5. Benefits of Winning:*  \n"
            "- Official recognition and certificate  \n"
            "- Featured on DIU Library platforms  \n"
            "- Academic motivation boost  \n\n"
            "#### *6. Stay Updated:*  \n"
            "- Visit [DIU Library Website](https://library.daffodilvarsity.edu.bd/)  \n"
            "- Follow [DIU Library Facebook](https://www.facebook.com/DIULIBRARY/)  \n"
            "- Contact library staff for announcements"
        ),
        "keywords": ["awards", "recognition", "achievement", "library excellence"]
    },
    "voice library": {
        "url": "https://voice.library.daffodilvarsity.edu.bd/",
        "info": "Access audio resources and spoken content.",
        "keywords": ["audio", "podcasts", "narration", "accessibility"]
    },
    "item issue, return, renew": {
        "url": "http://koha.daffodilvarsity.edu.bd/",
        "info": "Manage item circulation processes.",
        "keywords": ["circulation", "transactions", "loans", "returns"]
    },
    "resignation/study leave": {
        "url": "https://pd.daffodilvarsity.edu.bd/web#action=2278&cids=1&menu_id=1906&model=clearance.academic&view_type=list",
        "info": "Submit clearance requests for leaves.",
        "keywords": ["clearance", "HR", "administration", "process"]
    },
    "transcript/certificate": {
        "url": "http://192.168.10.14:8090/login",
        "info": "Access academic records and certificates.",
        "keywords": ["documents", "records", "verification", "academia"]
    },
    "library clearance service": {
        "url": None,
        "info": "Contact library staff for clearance services.",
        "keywords": ["clearance", "administration", "process"],
        "contact": {
            "Mr. Md. Abdul Monnaf Sarker": {
                "email": "library7@daffodilvarsity.edu.bd",
                "phone": "01729151416",
                "ip_phone": "65271"
            }
        }
    },
    "plagiarism checking & defense": {
        "url": "https://library.daffodilvarsity.edu.bd/service/internship-portal-guideline",
        "info": "Check academic integrity and submit defenses.",
        "keywords": ["academic integrity", "checking", "originality"]
    },
    "admission cancel": {
        "url": None,
        "info": "Process admission cancellations.",
        "keywords": ["admissions", "cancellation", "process"]
    },
    "library information literacy program": {
        "url": "https://www.appsheet.com/start/67d7805e-e5dd-4008-a849-19e297b3adaa?refresh=1&platform=desktop#viewStack[0][identifier][Type]=Control&viewStack[0][identifier][Name]=Coordination%20Officer&appName=LibraryDashboard-860092393",
        "info": "Participate in information literacy training.",
        "keywords": ["literacy", "training", "education", "skills"]
    },
    "internship portal training": {
        "url": "https://internship.daffodilvarsity.edu.bd/index.php?app=home",
        "info": "Access internship management resources.",
        "keywords": ["internship", "training", "career"]
    },
    "faculty publications": {
        "url": "http://dspace.daffodilvarsity.edu.bd:8080/",
        "info": "Access faculty research publications.",
        "keywords": ["research", "publications", "academia"]
    },
    "institutional repository service": {
        "url": "http://dspace.daffodilvarsity.edu.bd:8080/",
        "info": "Access institutional research repository.",
        "keywords": ["repository", "research", "archives"]
    },
    "student research paper": {
        "url": "https://zenodo.org/me/uploads?q=&l=list&p=1&s=10&sort=newest",
        "info": "Manage student research publications.",
        "keywords": ["research", "publications", "student work"]
    },
    "newspaper & periodical service": {
        "url": None,
        "info": "Access current news and periodicals.",
        "keywords": ["news", "periodicals", "current affairs"]
    },
    "bag counter/locker": {
        "url": "https://library.daffodilvarsity.edu.bd/content/lockers",
        "info": "Access library storage facilities.",
        "keywords": ["storage", "security", "facilities"]
    },
    "lost & found at library": {
        "url": None,
        "info": "Report or retrieve lost items.",
        "keywords": ["lost items", "recovery", "security"]
    },
    "turnitin administrative service": {
        "url": "https://www.turnitin.com/login_page.asp?lang=en_us",
        "info": "Access plagiarism checking services.",
        "keywords": ["plagiarism", "checking", "originality"]
    },
    "remote access using myathens": {
        "url": "https://library.daffodilvarsity.edu.bd/service/remote-access",
        "info": "Access resources remotely.",
        "keywords": ["remote access", "off-campus", "VPN"]
    },
    "e-book": {
        "url": "https://archives.daffodilvarsity.edu.bd/service/ebooks",
        "info": "Access electronic books.",
        "keywords": ["e-books", "digital", "reading"]
    },
    "e-journal": {
        "url": "https://library.daffodilvarsity.edu.bd/public/database",
        "info": "Access electronic journals.",
        "keywords": ["e-journals", "research", "periodicals"]
    },
    "blc for library use": {
        "url": "https://elearn.daffodilvarsity.edu.bd/login/index.php",
        "info": "Access blended learning content.",
        "keywords": ["learning", "online", "education"]
    },
    "cyber zone service": {
        "url": None,
        "info": "Access computer facilities.",
        "keywords": ["computers", "internet", "facilities"]
    },
    "library venue booking": {
        "url": None,
        "info": "Book library spaces.",
        "keywords": ["spaces", "booking", "facilities"]
    },
    "digital object identifier (doi) implementation service": {
        "url": None,
        "info": "Manage digital identifiers.",
        "keywords": ["DOI", "research", "publications"]
    },
    "student management service": {
        "url": "https://ejms.daffodilvarsity.edu.bd/",
        "info": "Manage student services.",
        "keywords": ["administration", "student affairs", "management"]
    }
}

# ----------------------------- #
# Core Functions
# ----------------------------- #
def generate_ai_explanation(service_name):
    """Generate service explanation using Groq AI"""
    if not GROQ_API_KEY:
        return "⚠️ AI explanations require Groq API key"
    
    prompt = f"""As a professional librarian, provide comprehensive details about {service_name} 
    at DIU Library. Include: purpose, benefits, access methods, requirements, and related services."""
    
    try:
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI explanation error: {str(e)}"

def handle_service_query(user_input):
    """Process user query with fuzzy matching"""
    service_terms = []
    for service_name, service_data in library_services.items():
        service_terms.append((service_name, service_name))
        service_terms.extend((keyword, service_name) for keyword in service_data.get('keywords', []))
    
    all_terms = [term for term, _ in service_terms]
    best_term, score = process.extractOne(user_input, all_terms)
    
    if score > 55:
        matched_service = next((s for t, s in service_terms if t == best_term), None)
        if matched_service:
            service = library_services[matched_service]
            response = [
                f"**📚 {matched_service.title()} Service**",
                service['info']
            ]
            
            if service.get('url'):
                response.append(f"**🔗 Access URL:** {service['url']}")
            if GROQ_API_KEY:
                response.append(f"\n**🤖 AI Overview:**\n{generate_ai_explanation(matched_service)}")
            
            return "\n\n".join(response)
    return None

# ----------------------------- #
# Streamlit UI Components
# ----------------------------- #
def chat_interface():
    """Main chat interface"""
    st.title("📚 LibraAI: DIU Smart Library Assistant")
    st.markdown('<div class="header-accent"></div>', unsafe_allow_html=True)
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            css_class = "user-message" if message["role"] == "user" else "assistant-message"
            st.markdown(f'<div class="{css_class}">{message["content"]}</div>', unsafe_allow_html=True)
    
    # Process input
    if user_query := st.chat_input("Ask about library services:"):
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        with st.spinner("🔍 Searching library resources..."):
            response = handle_service_query(user_query) or generate_groq_response(user_query)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Rerun to show new messages
        st.rerun()

def generate_groq_response(query):
    """Fallback to Groq for general queries"""
    try:
        messages = [{
            "role": "system",
            "content": "You are a DIU library assistant. Provide helpful, accurate information."
        }] + st.session_state.chat_history[-5:] + [{"role": "user", "content": query}]
        
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def sidebar_features():
    """All sidebar components"""
    with st.sidebar:
        st.header("Additional Features")
        st.markdown('<div class="header-accent"></div>', unsafe_allow_html=True)
        
        # Book Search
        st.subheader("🔍 Book Search")
        search_term = st.text_input("Search by title/author:")
        if st.button("Search Books") and not books.empty:
            results = books[books["Title"].str.contains(search_term, case=False)]
            st.dataframe(results.style.set_properties(**{
                'background-color': '#fffaf0',
                'border-color': '#8B4513'
            }))
        
        # Recommendation System
        st.subheader("📚 Books Recommendations")
        if GROQ_API_KEY:
            interest = st.text_input("Your interests:")
            if interest and st.button("Get Recommendations"):
                prompt = f"Recommend academic books about {interest} with brief descriptions"
                response = groq_client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5
                )
                st.markdown(response.choices[0].message.content)
        else:
            st.markdown('<div class="warning-box">Enable Groq API for recommendations</div>', 
                       unsafe_allow_html=True)
        
        # Borrowing System
        st.subheader("🔖 Borrow Books")
        if not books.empty:
            selected_book = st.selectbox("Select book", books["Title"].unique())
            user_email = st.text_input("DIU Email")
            if st.button("Borrow"):
                if books.loc[books["Title"] == selected_book, "Available"].values[0] == "Yes":
                    books.loc[books["Title"] == selected_book, "Available"] = "No"
                    due_dates[selected_book] = datetime.now() + timedelta(days=21)
                    st.success(f"✅ Due by {due_dates[selected_book].strftime('%Y-%m-%d')}")
                else:
                    st.error("❌ Book unavailable")
        
        # Session Management
        st.subheader("⚙️ Session")
        st.markdown(f"**Messages:** {len(st.session_state.chat_history)}")
        if st.button("🧹 Clear History"):
            st.session_state.chat_history = []
            st.rerun()

# ----------------------------- #
# Main Application
# ----------------------------- #
def main():
    load_css()
    chat_interface()
    sidebar_features()

if __name__ == "__main__":
    main()