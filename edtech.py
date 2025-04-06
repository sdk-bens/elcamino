import streamlit as st
import json
import os
import base64
import requests
from dotenv import load_dotenv
import pathlib

load_dotenv()



def is_in_scope_question(user_input):
    try:
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('MISTRAL_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistral-tiny",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a strict classifier. Your job is to say whether a question is about "
                            "3rd year Algerian high school Math, Physics, or Science (BAC curriculum). "
                            "Only respond with 'YES' or 'NO'."
                        )
                    },
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0
            }
        )
        result = response.json()
        answer = result['choices'][0]['message']['content'].strip().lower()
        return answer == "yes"
    except Exception as e:
        print(f"[Classifier error]: {e}")
        return False


# ---------- 🎓 Sample Users and Courses ----------


courses_json = '''{
    "Math": {
        "description": "📈 This course focuses on mathematics topics tailored for BAC students in Algeria.",
        "teacher": "Teacher A"
    },
    "Physics": {
        "description": "⚙️ This course covers core physics concepts and problem-solving strategies for high school exams.",
        "teacher": "Teacher B"
    },
    "Science": {
        "description": "🔬 This course provides scientific theory and practical knowledge for final-year students.",
        "teacher": "Teacher C"
    }
}'''


# Load users from file if it exists, otherwise use default JSON
users_file = "users.json"

if os.path.exists(users_file):
    with open(users_file, "r") as f:
        users = json.load(f)
else:
    students_json = '''{
        "rhm": {"name": "Abderrahim", "email": "Abderrahim@student.com", "password": "rhm123", "enrolled_courses": ["Math"]},
        "srn": {"name": "Sirine", "email": "Sirine@student.com", "password": "srn123", "enrolled_courses": ["Physics"]},
        "adm": {"name": "Adam", "email": "Adam@student.com", "password": "adm123", "enrolled_courses": []}
    }'''

    teachers_json = '''{
        "rcm": {"name": "Racim", "email": "Racim@teacher.com", "password": "rcm123", "courses": ["Math"]},
        "amn": {"name": "Amani", "email": "Amani@teacher.com", "password": "amnB123", "courses": ["Physics"]},
        "Teacher": {"name": "Teacher", "email": "Teacher_C@teacher.com", "password": "teacher123", "courses": ["Science"]}
    }'''

    users = {
        "students": json.loads(students_json),
        "teachers": json.loads(teachers_json)
    }

    # Save defaults to file for first-time use
    with open(users_file, "w") as f:
        json.dump(users, f, indent=4)

courses_data = json.loads(courses_json)

# def check_credentials(username, password):
#     return username in users["students"] or username in users["teachers"]
def save_users_to_file():
    with open(users_file, "w") as f:
        json.dump(users, f, indent=4)

def check_credentials(username, password, role):
    if role == "Student":
        student = users["students"].get(username)
        return student and student.get("password") == password
    elif role == "Teacher":
        teacher = users["teachers"].get(username)
        return teacher and teacher.get("password") == password
    return False


def list_directories_and_pdfs(directory):
    directories = {}
    for root, dirs, files in os.walk(directory):
        pdf_files = [file for file in files if file.endswith('.pdf')]
        if pdf_files or dirs:
            directories[root] = {"pdfs": pdf_files, "dirs": dirs}
    return directories


# ---------- 🚀 Streamlit App ----------
st.set_page_config(
    page_title="🎓 EdTech - Algeria",
    page_icon="favicon.ico",  # or emoji like "📘"
    layout="wide"
)
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)




if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.markdown("""
    <h1 style='text-align: center; margin-top: 0;'>
        🎓 EdTech
    </h1>
""", unsafe_allow_html=True)

    st.markdown("<h2 style='text-align: center;'>🔐 Login / 🆕 Sign Up</h2>", unsafe_allow_html=True)
    cols = st.columns([1, 2, 1])  # Side-center-side layout

    with cols[1]:
        mode = st.radio("Choose Mode", ["Login", "Sign Up"], horizontal=True)

        
        username = st.text_input("👤 Username")
        password = st.text_input("🔑 Password", type="password")
        user_role = st.selectbox("🎓 Select your role", ["Student", "Teacher"])

        if mode == "Sign Up":
            full_name = st.text_input("🪪 Full Name")
            email = st.text_input("📧 Email")

        if st.button("🚀 Submit"):
            if mode == "Login":
                if check_credentials(username, password, user_role):
                    st.session_state.logged_in = True
                    st.session_state.user_role = user_role
                    st.session_state.username = username
                    st.session_state.user = users["students"].get(username) or users["teachers"].get(username)
                    st.success("✅ Successfully logged in!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials or role mismatch")
            
            elif mode == "Sign Up":
                if not all([username, password, full_name, email]):
                    st.warning("⚠️ Please fill out all fields.")
                elif username in users["students"] or username in users["teachers"]:
                    st.error("❌ Username already exists.")
                elif any(email == u["email"] for u in list(users["students"].values()) + list(users["teachers"].values())):
                    st.error("❌ An account with this email already exists.")
                else:
                    new_user = {
                        "name": full_name,
                        "email": email,
                        "password": password,
                        "enrolled_courses": [] if user_role == "Student" else [],
                        "courses": [] if user_role == "Teacher" else []
                    }

                    users[user_role.lower() + "s"][username] = new_user

                    # 🔐 Save the updated users to file
                    with open(users_file, "w") as f:
                        json.dump(users, f, indent=4)

                    st.success(f"🎉 Account created successfully, {full_name}! Please switch to the Login tab above and enter your credentials to access your account.")
                    st.stop()
                    
       
else:
    st.title("👋 Welcome to EdTech Education")
    st.markdown(f"#### Hello, `{st.session_state.user['name']}`! You are logged in as a **{st.session_state.user_role}**.")
    st.sidebar.title("🧩 Menu")

    if st.session_state.user_role == "Student":
        choice = st.sidebar.radio("", ["👤 Profile", "📚 Courses", "ℹ️ About", "📞 Contact Us", "🤖 EdTech AI", "🔓 Logout"])

        if choice == "🤖 EdTech AI":
            st.header("🤖 EdTech AI Tutor")
            st.markdown("Ask me anything about **Math, Physics, or Science** from the 3rd year Algerian BAC curriculum!")

            if 'ai_chat_history' not in st.session_state:
                st.session_state.ai_chat_history = [
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful, friendly AI tutor for 3rd year Algerian high school students. "
                            "You only help with topics from the Algerian BAC curriculum for Math, Physics, and Science. "
                            "If a user asks about something else, kindly say so."
                        )
                    }
                ]

            for msg in st.session_state.ai_chat_history[1:]:
                st.chat_message(msg["role"]).markdown(msg["content"])

            user_input = st.chat_input("Type your question here...")

            if user_input:
                st.chat_message("user").markdown(user_input)
                st.session_state.ai_chat_history.append({"role": "user", "content": user_input})

                with st.spinner("Thinking..."):
                    if is_in_scope_question(user_input):
                        try:
                            response = requests.post(
                                "https://api.mistral.ai/v1/chat/completions",
                                headers={
                                    "Authorization": f"Bearer {os.getenv('MISTRAL_API_KEY')}",
                                    "Content-Type": "application/json"
                                },
                                json={
                                    "model": "mistral-medium",
                                    "messages": st.session_state.ai_chat_history,
                                    "temperature": 0.7
                                }
                            )
                            response_data = response.json()
                            if 'choices' in response_data and len(response_data['choices']) > 0:
                                assistant_reply = response_data['choices'][0]['message']['content']
                                st.chat_message("assistant").markdown(assistant_reply)
                                st.session_state.ai_chat_history.append({"role": "assistant", "content": assistant_reply})
                            else:
                                st.error("\u274c No choices found in the response from Mistral API.")
                        except Exception as e:
                            st.error(f"\u274c Failed to get response from Mistral API: {e}")
                    else:
                        try:
                            response = requests.post(
                                "https://api.mistral.ai/v1/chat/completions",
                                headers={
                                    "Authorization": f"Bearer {os.getenv('MISTRAL_API_KEY')}",
                                    "Content-Type": "application/json"
                                },
                                json={
                                    "model": "mistral-medium",
                                    "messages": [
                                        {
                                            "role": "system",
                                            "content": (
                                                "You are a tutor assistant that kindly explains you can only help with the 3rd year Algerian high school BAC curriculum "
                                                "in Math, Physics, or Science. Be polite and helpful."
                                            )
                                        },
                                        {"role": "user", "content": user_input}
                                    ],
                                    "temperature": 0.7
                                }
                            )
                            response_data = response.json()
                            if 'choices' in response_data and len(response_data['choices']) > 0:
                                fallback_reply = response_data['choices'][0]['message']['content']
                                st.chat_message("assistant").markdown(fallback_reply)
                                st.session_state.ai_chat_history.append({"role": "assistant", "content": fallback_reply})
                            else:
                                st.error("\u274c No fallback response returned from Mistral API.")
                        except Exception as e:
                            st.error(f"\u274c Failed to get fallback response: {e}")


# Continue your logic for other pages: Profile, Courses, Contact, About, Logout...

        elif choice == "👤 Profile":
            # st.subheader("👨‍🎓 Student Profile")
            # st.write(f"**Name:** {st.session_state.user['name']}")
            # st.write(f"**Email:** {st.session_state.user['email']}")
            st.subheader("👨‍🎓 Student Profile")

            if "edit_mode" not in st.session_state:
                st.session_state.edit_mode = False

            current_username = st.session_state.username

            if not st.session_state.edit_mode:
                st.write(f"**Name:** {st.session_state.user['name']}")
                st.write(f"**Email:** {st.session_state.user['email']}")
                st.write("**Password:** 🔒 (hidden)")

                if st.button("✏️ Edit Profile"):
                    st.session_state.edit_mode = True
                    st.rerun()

            else:
                st.text("✏️ Editing Profile Info")
                new_name = st.text_input("🪪 Full Name", value=st.session_state.user["name"])
                new_email = st.text_input("📧 Email", value=st.session_state.user["email"])
                new_password = st.text_input("🔑 Password", value=st.session_state.user["password"], type="password")

                col1, col2 = st.columns(2)

                # if col1.button("💾 Save Changes"):
                #     # Check for duplicate email
                #     all_other_emails = [
                #         u["email"] for uname, u in users["students"].items() if uname != current_username
                #     ] + [u["email"] for u in users["teachers"].values()]
                    
                #     if new_email in all_other_emails:
                #         st.error("❌ This email is already used by another user.")
                #     else:
                #         user_data = users["students"][current_username]
                #         user_data["name"] = new_name
                #         user_data["email"] = new_email
                #         user_data["password"] = new_password

                #         with open(users_file, "w") as f:
                #             json.dump(users, f, indent=4)

                #         st.session_state.user = user_data
                #         st.session_state.edit_mode = False  # 🔁 Go back to normal view
                #         st.success("✅ Profile updated successfully!")
                #         st.rerun()
                if col1.button("💾 Save Changes"):
                    # Check for duplicate email
                    all_other_emails = [
                        u["email"] for uname, u in users["students"].items() if uname != current_username
                    ] + [u["email"] for u in users["teachers"].values()]

                    if new_email in all_other_emails:
                        st.error("❌ This email is already used by another user.")
                    else:
                        user_data = users["students"][current_username]
                        user_data["name"] = new_name
                        user_data["email"] = new_email
                        user_data["password"] = new_password

                        st.session_state.user = user_data
                        st.session_state.edit_mode = False

                        save_users_to_file()

                        st.success("✅ Profile updated successfully!")
                        st.rerun()


                if col2.button("❌ Cancel"):
                    st.session_state.edit_mode = False
                    st.rerun()

            
        


            # st.write("**Enrolled Courses:**")
            # st.success(", ".join(st.session_state.user["enrolled_courses"]) or "No courses enrolled.")

            # st.markdown("---")
            # st.subheader("🆕 Enroll in a New Course")
            # available_courses = [c for c in courses_data.keys() if c not in st.session_state.user["enrolled_courses"]]
            # if available_courses:
            #     selected_new_course = st.selectbox("📘 Available Courses", available_courses)
            #     # if st.button("✅ Enroll"):
            #     #     st.session_state.user["enrolled_courses"].append(selected_new_course)
            #     #     st.success(f"Enrolled in {selected_new_course}!")
            #     #     st.rerun()
            #     if st.button("✅ Enroll"):
            #         st.session_state.user["enrolled_courses"].append(selected_new_course)
                    
            #         # 🛠️ Update the users dictionary
            #         users["students"][st.session_state.username]["enrolled_courses"] = st.session_state.user["enrolled_courses"]

            #         # 💾 Save to file
            #         with open(users_file, "w") as f:
            #             json.dump(users, f, indent=4)

            #         st.success(f"Enrolled in {selected_new_course}!")
            #         st.rerun()

            # else:
            #     st.info("🎉 You're enrolled in all available courses!")
            # st.write("**Enrolled Courses:**")
            # st.success(", ".join(st.session_state.user["enrolled_courses"]) or "No courses enrolled.")
            st.write("**Enrolled Courses:**")

            if st.session_state.user["enrolled_courses"]:
                for course in st.session_state.user["enrolled_courses"]:
                    col1, col2 = st.columns([5, 1])
                    col1.success(course)
                    if col2.button(f"❌ Unenroll", key=f"unenroll-{course}"):
                        st.session_state.user["enrolled_courses"].remove(course)
                        users["students"][st.session_state.username]["enrolled_courses"] = st.session_state.user["enrolled_courses"]
                        save_users_to_file()
                        st.success(f"Unenrolled from {course}")
                        st.rerun()
            else:
                st.info("You are not enrolled in any courses.")


            st.markdown("---")
            st.subheader("🆕 Enroll in a New Course")

            available_courses = [c for c in courses_data.keys() if c not in st.session_state.user["enrolled_courses"]]

            if available_courses:
                selected_new_course = st.selectbox("📘 Available Courses", available_courses)

                if st.button("✅ Enroll"):
                    # ✅ Update session
                    st.session_state.user["enrolled_courses"].append(selected_new_course)

                    # ✅ Update users dictionary
                    users["students"][st.session_state.username]["enrolled_courses"] = st.session_state.user["enrolled_courses"]

                    # ✅ Save to file
                    save_users_to_file()

                    st.success(f"✅ Successfully enrolled in {selected_new_course}!")
                    st.rerun()
            else:
                st.info("🎉 You're enrolled in all available courses!")

        elif choice == "📚 Courses":
            enrolled_courses = st.session_state.user["enrolled_courses"]
            if not enrolled_courses:
                st.warning("⚠️ You're not enrolled in any courses yet. Please go to the Profile tab to enroll.")
            else:
                st.header("📘 Your Enrolled Courses")
                course_selection = st.selectbox("🗂 Select a course", enrolled_courses)
                # directory_map = {
                #     "Math": "/Users/seddik/edtech/MATHS",
                #     "Physics": "/Users/seddik/edtech/PHYSICS",
                #     "Science": "/Users/seddik/edtech/SCIENCES"
                # }

                BASE_DIR = pathlib.Path(__file__).parent

                directory_map = {
                    "Math": str(BASE_DIR / "MATHS"),
                    "Physics": str(BASE_DIR / "PHYSICS"),
                    "Science": str(BASE_DIR / "SCIENCES")
                }
                course_directory = directory_map[course_selection]
                st.markdown(f"### 📚 {course_selection}")
                st.markdown(courses_data[course_selection]["description"])

                contents = list_directories_and_pdfs(course_directory)
                for folder, data in contents.items():
                    with st.expander(f"📂 {os.path.basename(folder)}"):
                        for pdf in data["pdfs"]:
                            pdf_path = os.path.join(folder, pdf)
                            if st.button(f"📄 {pdf}", key=pdf_path):
                                st.markdown(f'<iframe src="data:application/pdf;base64,{base64.b64encode(open(pdf_path, "rb").read()).decode()}" width="700" height="500"></iframe>', unsafe_allow_html=True)
                        for subdir in data["dirs"]:
                            st.markdown(f"📁 Subfolder: `{subdir}`")
        elif choice == "📞 Contact Us":
            st.header("📞 Get in Touch")
            st.markdown("""
            We're here to help! If you have any questions, suggestions, or need support, feel free to reach out.

            **📧 Email:** [support@EdTech.dz](mailto:support@EdTech.dz)  
            **📍 Address:** Algiers, Algeria  

            You can also use the form below to send us a message directly:
            """)

            name = st.text_input("👤 Your Name")
            email = st.text_input("📧 Your Email")
            message = st.text_area("✉️ Your Message", height=150)

            if st.button("📨 Send Message"):
                if name and email and message:
                    st.success("✅ Thank you! Your message has been sent.")
                else:
                    st.warning("⚠️ Please fill out all fields before submitting.")

        elif choice == "ℹ️ About":
            st.header("ℹ️ About EdTech ")
            st.markdown("""
            **EdTech** is a student-focused platform designed to support high school learners in Algeria, especially those preparing for the **BAC exams**.

            🌟 **Our Mission**  
            To provide accessible, high-quality, and organized educational resources that help students thrive in subjects like **Math**, **Physics**, and **Science**.

            👨‍🏫 **For Teachers**  
            We empower educators to share materials, manage content, and connect with students efficiently.

            👨‍🎓 **For Students**  
            Get direct access to handpicked PDFs, structured by course and topic, and stay on top of your studies at your own pace.

            🚀 **Built With Love**  
            EdTech is built using [Streamlit](https://streamlit.io) and open-source tools by educators who care about modern, accessible education.

            💡 Have ideas to improve EdTech? Let us know in the Contact Us section!
        """)

    # Teacher view
    elif st.session_state.user_role == "Teacher":
        choice = st.sidebar.radio("", ["👤 Profile", "📚 Courses", "ℹ️ About", "📞 Contact Us", "🔓 Logout"])

        if choice == "👤 Profile":
            st.subheader("👨🏻‍💼Teacher Profile")
  

            if "edit_mode" not in st.session_state:
                st.session_state.edit_mode = False

            current_username = st.session_state.username

            if not st.session_state.edit_mode:
                st.write(f"**Name:** {st.session_state.user['name']}")
                st.write(f"**Email:** {st.session_state.user['email']}")
                st.write("**Password:** 🔒 (hidden)")

                if st.button("✏️ Edit Profile"):
                    st.session_state.edit_mode = True
                    st.rerun()

            else:
                st.text("✏️ Editing Profile Info")
                new_name = st.text_input("🪪 Full Name", value=st.session_state.user["name"])
                new_email = st.text_input("📧 Email", value=st.session_state.user["email"])
                new_password = st.text_input("🔑 Password", value=st.session_state.user["password"], type="password")

                col1, col2 = st.columns(2)

                # if col1.button("💾 Save Changes"):
                #     # Check for duplicate email
                #     all_other_emails = [
                #         u["email"] for uname, u in users["students"].items() if uname != current_username
                #     ] + [u["email"] for u in users["teachers"].values()]
                    
                #     if new_email in all_other_emails:
                #         st.error("❌ This email is already used by another user.")
                #     else:
                #         user_data = users["teachers"][current_username]

                #         user_data["name"] = new_name
                #         user_data["email"] = new_email
                #         user_data["password"] = new_password

                #         with open(users_file, "w") as f:
                #             json.dump(users, f, indent=4)

                #         st.session_state.user = user_data
                #         st.session_state.edit_mode = False  # 🔁 Go back to normal view
                #         st.success("✅ Profile updated successfully!")
                #         st.rerun()
                if col1.button("💾 Save Changes"):
                    # Check for duplicate email
                    all_other_emails = [
                        u["email"] for uname, u in users["students"].items() if uname != current_username
                    ] + [u["email"] for u in users["teachers"].values()]

                    if new_email in all_other_emails:
                        st.error("❌ This email is already used by another user.")
                    else:
                        user_data = users["teachers"][current_username]
                        user_data["name"] = new_name
                        user_data["email"] = new_email
                        user_data["password"] = new_password

                        st.session_state.user = user_data
                        st.session_state.edit_mode = False

                        save_users_to_file()

                        st.success("✅ Profile updated successfully!")
                        st.rerun()



                if col2.button("❌ Cancel"):
                    st.session_state.edit_mode = False
                    st.rerun()
       
            st.write("**Courses Taught:**")
            st.success(", ".join(st.session_state.user["courses"]))

        elif choice == "📚 Courses":
            st.header("📝 Manage Your Courses")
            # base_dir_map = {
            #     "Math": "/Users/seddik/edtech/MATHS",
            #     "Physics": "/Users/seddik/edtech/PHYSICS",
            #     "Science": "/Users/seddik/edtech/SCIENCES"
            # }
            base_dir_map = {
                "Math": str(BASE_DIR / "MATHS"),
                "Physics": str(BASE_DIR / "PHYSICS"),
                "Science": str(BASE_DIR / "SCIENCES")
            }


            for course in st.session_state.user["courses"]:
                st.subheader(f"📘 {course}")
                st.markdown("**Current Description:**")
                st.info(courses_data[course]["description"])
                new_desc = st.text_area(f"✏️ Edit Description for {course}", value=courses_data[course]["description"])
                if st.button(f"📂 Update {course}"):
                    courses_data[course]["description"] = new_desc
                    st.success(f"✅ Description updated for {course}!")

                course_dir = base_dir_map.get(course)
                if not course_dir:
                    st.warning(f"No directory found for {course}")
                    continue

                st.markdown("### 📂 Manage Course Files")
                contents = list_directories_and_pdfs(course_dir)

                for folder, data in contents.items():
                    with st.expander(f"📁 {os.path.basename(folder)}"):
                        for pdf in data["pdfs"]:
                            col1, col2 = st.columns([5, 1])
                            with col1:
                                st.markdown(f"- 📄 {pdf}")
                            with col2:
                                if st.button("🗑️ Delete", key=f"del-{folder}-{pdf}"):
                                    try:
                                        os.remove(os.path.join(folder, pdf))
                                        st.success(f"{pdf} deleted.")
                                    except Exception as e:
                                        st.error(f"Error deleting {pdf}: {e}")

                        uploaded_pdf = st.file_uploader(f"📄 Upload new PDF to `{os.path.basename(folder)}`", type="pdf", key=f"upload-{folder}")
                        if uploaded_pdf:
                            save_path = os.path.join(folder, uploaded_pdf.name)
                            with open(save_path, "wb") as f:
                                f.write(uploaded_pdf.read())
                            st.success(f"{uploaded_pdf.name} uploaded to {os.path.basename(folder)}.")

        elif choice == "📞 Contact Us":
            st.header("📞 Get in Touch")
            st.markdown("""
            We're here to help! If you have any questions, suggestions, or need support, feel free to reach out.

            **📧 Email:** [support@edtech.com](mailto:support@edtech.com)  
            **📍 Address:** Algiers, Algeria  

            You can also use the form below to send us a message directly:
            """)

            name = st.text_input("👤 Your Name")
            email = st.text_input("📧 Your Email")
            message = st.text_area("✉️ Your Message", height=150)

            if st.button("📨 Send Message"):
                if name and email and message:
                    st.success("✅ Thank you! Your message has been sent.")
                else:
                    st.warning("⚠️ Please fill out all fields before submitting.")

        elif choice == "ℹ️ About":
            st.header("ℹ️ About EdTech")
            st.markdown("""
            **EdTech** is a student-focused platform designed to support high school learners in Algeria, especially those preparing for the **BAC exams**.

            🌟 **Our Mission**  
            To provide accessible, high-quality, and organized educational resources that help students thrive in subjects like **Math**, **Physics**, and **Science**.

            👨‍🏫 **For Teachers**  
            We empower educators to share materials, manage content, and connect with students efficiently.

            👨‍🎓 **For Students**  
            Get direct access to handpicked PDFs, structured by course and topic, and stay on top of your studies at your own pace.

            🚀 **Built With Love**  
            EdTech is built using [Streamlit](https://streamlit.io) and open-source tools by educators who care about modern, accessible education.

            💡 Have ideas to improve EdTech? Let us know in the Contact Us section!
            """)

    # Logout
    if choice == "🔓 Logout":
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.username = None
        st.session_state.name = None
        st.session_state.user = None
        st.rerun()


if 'logged_in' in st.session_state and st.session_state.logged_in:
    # Logged-in users: show in sidebar bottom
    for _ in range(10):  # Spacer to push it to bottom — adjust as needed
        st.sidebar.markdown("&nbsp;")

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "<div style='text-align: center; font-size: 0.85rem; color: gray;'>"
        "Made with ❤️ somewhere on 🌎"
        "</div>",
        unsafe_allow_html=True
    )
else:
    # Not logged in: show centered sticky footer on bottom of page
    st.markdown("""
        <style>
        .footer-login {
            position: fixed;
            bottom: 1rem;
            left: 50%;
            transform: translateX(-50%);
            color: gray;
            font-size: 0.85rem;
            text-align: center;
            z-index: 9999;
        }
        </style>

        <div class="footer-login">
            Made with ❤️ somewhere on 🌎
        </div>
    """, unsafe_allow_html=True)


