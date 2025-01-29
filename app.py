import streamlit as st
import pandas as pd
import smtplib
import random
from datetime import datetime, timedelta
from groq import Groq

# Initialize Groq API
groq_client = Groq(api_key="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")  # Replace with your API key

# Load book data
books = pd.read_csv("books.csv")  # Replace with your dataset

# Track the due dates (in reality, this would be handled by a database)
due_dates = {}  # Dictionary to hold book titles and their due dates

# Function to search for books
def search_books(query):
    results = books[books["Title"].str.contains(query, case=False, na=False)]
    return results if not results.empty else "No books found."

# Function to recommend books based on genre/skill level
def recommend_books(genre, skill_level):
    results = books[
        (books["Genre"].str.contains(genre, case=False, na=False)) &
        (books["Skill_Level"].str.contains(skill_level, case=False, na=False))
    ]
    return results if not results.empty else "No recommendations available."

# Function to check availability
def check_availability(title):
    book = books[books["Title"].str.contains(title, case=False, na=False)]
    return f"'{title}' is available!" if not book.empty and book["Available"].values[0] == "Yes" else f"'{title}' is not available."

# Function to send email notifications
def send_email(to_email, subject, message):
    sender_email = "hasan35-923@diu.edu.bd"  # Change this
    app_password = "qbow iqtk ixof dvas"  # Use a Google App Password

    msg = f"Subject: {subject}\n\n{message}"
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, to_email, msg)
        server.quit()
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Error sending email: {e}")

# Function to get AI-generated book suggestions
def get_ai_suggestions(user_input):
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": user_input}],
        temperature=0.7
    )
    return response.choices[0].message.content

# LibraAI response function
def libraAI_response(user_input):
    user_input = user_input.lower()

    # Check if the user asks about the library or registration
    if "library" in user_input or "register" in user_input:
        return """📚 If you're looking to register for the DIU eLibrary, you can do so through the official website. 
        Just click the link below to get started:
        
       https://archives.daffodilvarsity.edu.bd/login
        
        Feel free to ask me anything else about the library, books, or recommendations!"""

    # Check if user asks "Who are you?"
    if "who are you" in user_input:
        return """I am LibraAI, the AI librarian of DIU Library. 📚  
        I can help you with:
        ✅ Personalized book recommendations 📖  
        ✅ AI-powered search engine 🔍  
        ✅ Real-time book availability updates 🏷️  
        ✅ Alternative book suggestions if your desired title is unavailable 🔄  
        ✅ Automated book renewal & smart reminders 📅  
        ✅ New arrival & trending book notifications 🚀  
        ✅ 24/7 AI chatbot for book searches, renewals, and reservations 🤖  
        Just ask me anything about DIU Library, and I’ll assist you!"""

    # Book search by title
    for title in books["Title"]:
        if title.lower() in user_input:
            book_info = books[books["Title"].str.lower() == title.lower()].iloc[0]
            return f"""📖 **{book_info["Title"]}** by {book_info["Author"]}
            📂 Genre: {book_info["Genre"]}
            🎯 Skill Level: {book_info["Skill_Level"]}
            📍 Location: {book_info["Location"]}
            ✅ Available: {book_info["Available"]}"""

    # Recommend books based on genre
    for genre in books["Genre"].unique():
        if genre.lower() in user_input:
            recommended_books = books[books["Genre"].str.lower() == genre.lower()].sample(min(3, len(books)))
            response = f"📚 Here are some **{genre}** books you might like:\n"
            for _, row in recommended_books.iterrows():
                response += f"- **{row['Title']}** by {row['Author']} 📍({row['Location']})\n"
            return response

    return "Sorry, I didn't understand that. You can ask me about books, recommendations, availability, or how I can assist you!"

# Automatically renew books (if not opted out)
def auto_renewal(book_title):
    # Check if the book has a due date
    if book_title in due_dates:
        due_date = due_dates[book_title]
        today = datetime.now()

        # If the due date is within the next 3 days, renew the book automatically
        if due_date <= today + timedelta(days=3):
            new_due_date = today + timedelta(days=30)  # Renew for another 30 days
            due_dates[book_title] = new_due_date
            return f"Book '{book_title}' has been auto-renewed. New due date: {new_due_date.strftime('%Y-%m-%d')}"
        else:
            return f"Book '{book_title}' is not due for renewal yet. Current due date: {due_date.strftime('%Y-%m-%d')}"
    else:
        return f"Book '{book_title}' not found in due dates."

# Function to borrow a book
def borrow_book(book_title, user_email):
    book = books[books["Title"].str.contains(book_title, case=False, na=False)]
    
    if not book.empty and book["Available"].values[0] == "Yes":
        # Update the availability of the book
        books.loc[books["Title"] == book_title, "Available"] = "No"
        
        # Send a confirmation email
        subject = f"Book Borrowed: {book_title}"
        message = f"Dear User,\n\nYou have successfully borrowed the book '{book_title}'.\n\nPlease return it within the due date.\n\nThank you!"
        send_email(user_email, subject, message)
        
        st.success(f"You have successfully borrowed '{book_title}'. A confirmation email has been sent to {user_email}.")
    else:
        st.error(f"Sorry, '{book_title}' is not available for borrowing at the moment.")

# Streamlit UI
st.title("📚 LibraAI: The Agentic AI-Powered Librarian of DIU")

user_input = st.text_input("Ask me anything about books:")
if user_input:
    # AI-powered suggestions
    ai_response = get_ai_suggestions(user_input)
    
    # Book search
    search_result = search_books(user_input)
    
    # Display results
    st.subheader("🔍 AI Suggestion:")
    st.write(ai_response)
    
    st.subheader("📖 Search Results:")
    st.write(search_result)

# Book Recommendation
st.subheader("🔹 Get Book Recommendations")
genre = st.selectbox("Select Genre:", books["Genre"].unique())
skill_level = st.selectbox("Select Skill Level:", books["Skill_Level"].unique())

if st.button("Recommend"):
    recommendations = recommend_books(genre, skill_level)
    st.write(recommendations)

# Check Availability
st.subheader("📌 Check Book Availability")
book_title = st.text_input("Enter Book Title:")

if st.button("Check"):
    availability = check_availability(book_title)
    st.write(availability)

# Email Notification for New Arrivals
st.subheader("📩 Subscribe for New Arrivals")
email = st.text_input("Enter your email:")

if st.button("Subscribe"):
    send_email(email, "Library New Arrivals", "You have been subscribed to book updates! Thank you for subscribing! You will now receive updates on new arrivals.Click here to register for the DIU eLibrary >> https://archives.daffodilvarsity.edu.bd/login")

# Test the chatbot in Streamlit
st.subheader("🤖 Chat with LibraAI")
chat_input = st.text_input("Ask LibraAI anything:")

if chat_input:
    response = libraAI_response(chat_input)
    st.write(response)

# Handle Auto-Renewal
st.subheader("🔄 Automatic Book Renewal")
book_to_renew = st.text_input("Enter Book Title to Auto-Renew:")

if st.button("Renew Book"):
    renewal_response = auto_renewal(book_to_renew)
    st.write(renewal_response)

# Borrow Book Feature
st.subheader("🔹 Borrow a Book")
book_to_borrow = st.selectbox("Select Book to Borrow:", books["Title"].unique())
user_email = st.text_input("Enter your Email:")

if st.button("Borrow Book"):
    borrow_book(book_to_borrow, user_email)
