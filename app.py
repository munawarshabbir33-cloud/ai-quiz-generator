import streamlit as st
from openai import OpenAI

# 1. Grab the secret token from Streamlit's cloud encrypted vault
api_token = st.secrets["DEEPSEEK_API_KEY"]

# 2. Instantiate the communication client pointing to DeepSeek's servers
client = OpenAI(
    api_key=api_token,
    base_url="https://api.deepseek.com"
)

# 3. Application User Interface Design (Streamlit Frontend)
st.set_page_config(page_title="AI Quiz Generator", page_icon="🎯", layout="centered")

st.title("🎯 Advanced AI Quiz Generator")
st.write("Generate academic testing materials across subject matters instantly.")

# Data capture block for inputs
with st.container():
    grade_level = st.selectbox("Target Grade Level:", ["Grade 9", "Grade 10", "AS Level", "A Level"])
    subject = st.text_input("Academic Subject:", placeholder="e.g., Physics, Computer Science")
    topic = st.text_input("Curriculum Topic Area:", placeholder="e.g., Stationary Waves, Arrays")

# Initialize persistent session states so data doesn't wipe when pages reload
if "generated_question" not in st.session_state:
    st.session_state.generated_question = None
if "evaluation_results" not in st.session_state:
    st.session_state.evaluation_results = None

# 4. Question Generation Pipeline
if st.button("Generate Original Question"):
    if subject.strip() == "" or topic.strip() == "":
        st.warning("Please fill in both the Subject and Topic boxes before proceeding.")
    else:
        st.write("Communicating with DeepSeek AI network... generating problem.")
        
        generation_prompt = f"""
        You are an elite academic professor constructing test items for {grade_level} {subject}.
        Generate exactly ONE highly analytical short-answer question testing knowledge on: {topic}.
        Do not make it multiple choice. Output ONLY the raw question text. No introductory filler text.
        """
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": generation_prompt}],
            temperature=0.7
        )
        
        st.session_state.generated_question = response.choices[0].message.content
        st.session_state.evaluation_results = None  # Clear past grading values

# 5. Student Interaction & Automated Evaluation Loop
if st.session_state.generated_question:
    st.markdown("---")
    st.subheader("📋 Assessment Problem:")
    st.info(st.session_state.generated_question)
    
    # Provision a clean text input workspace acting as the space for typing the answer
    student_answer = st.text_input("Type your formal answer submission below:", key="student_input_box")
    
    if st.button("Submit Assessment Answer"):
        if student_answer.strip() == "":
            st.error("Please enter text into the answer space before submitting evaluation requests.")
        else:
            st.write("Evaluating submission metrics...")
            
            grading_prompt = f"""
            You are a rigorous exam evaluator. Review the problem context and evaluate the student response.
            Question: {st.session_state.generated_question}
            Student Response: {student_answer}
            
            You must output your reply strictly in this identical format structure:
            VERDICT: [CORRECT or INCORRECT]
            EXPLANATION: [Provide a precise 1-sentence analytical review of the concept.]
            """
            
            grading_call = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": grading_prompt}],
                temperature=0.1
            )
            
            st.session_state.evaluation_results = grading_call.choices[0].message.content

# Display results container dynamically to the user if present
if st.session_state.evaluation_results:
    st.markdown("---")
    st.subheader("📊 Performance Diagnostics Feedback:")
    
    if "VERDICT: CORRECT" in st.session_state.evaluation_results:
        st.success(st.session_state.evaluation_results)
    else:
        st.error(st.session_state.evaluation_results)
