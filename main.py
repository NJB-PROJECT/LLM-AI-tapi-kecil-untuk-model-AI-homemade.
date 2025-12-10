import streamlit as st
import os
import tempfile
import time
from app.llm_engine import LLMEngine
from app.voice import transcribe_audio, run_tts
from utils.file_handler import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt, encode_image_to_base64
from audiocorder import audiorecorder

# Page Config
st.set_page_config(page_title="My Private AI", page_icon="🤖", layout="wide")

# Custom CSS for chat bubbles
st.markdown("""
<style>
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}
.chat-message.user {
    background-color: #2b313e
}
.chat-message.bot {
    background-color: #475063
}
.chat-message .avatar {
  width: 20%;
}
.chat-message .message {
  width: 80%;
}
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "llm" not in st.session_state:
    st.session_state.llm = None
if "model_name" not in st.session_state:
    st.session_state.model_name = ""

# Sidebar - Configuration
with st.sidebar:
    st.title("🤖 Pengaturan AI")

    # Model Selection
    models_dir = "models"
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    model_files = [f for f in os.listdir(models_dir) if f.endswith(".gguf")]

    if not model_files:
        st.warning("⚠️ Belum ada model di folder 'models/'. Silakan jalankan script download dulu!")
        selected_model = None
    else:
        selected_model = st.selectbox("Pilih Model:", model_files, index=0)

    # Load Model Button
    if selected_model and selected_model != st.session_state.model_name:
        if st.button("Muat Model"):
            with st.spinner("Memuat model... (bisa agak lama di awal)"):
                model_path = os.path.join(models_dir, selected_model)
                st.session_state.llm = LLMEngine(model_path)
                st.session_state.model_name = selected_model
            st.success("Model berhasil dimuat!")

    st.divider()

    # File Upload
    st.subheader("📄 Upload Dokumen")
    uploaded_file = st.file_uploader("Upload PDF/DOCX/TXT", type=["pdf", "docx", "txt"])
    file_context = ""
    if uploaded_file:
        with st.spinner("Membaca file..."):
            if uploaded_file.type == "application/pdf":
                file_text = extract_text_from_pdf(uploaded_file.getvalue())
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                file_text = extract_text_from_docx(uploaded_file.getvalue())
            else:
                file_text = extract_text_from_txt(uploaded_file.getvalue())

            if file_text:
                file_context = f"\n\n[Isi Dokumen '{uploaded_file.name}':]\n{file_text[:5000]}..." # Limit context to avoid overflow
                st.success(f"File '{uploaded_file.name}' terbaca!")

    st.divider()

    # Voice Input
    st.subheader("🎤 Voice Chat")
    audio = audiorecorder("Klik untuk rekam", "Merekam...")

    voice_text = ""
    if len(audio) > 0:
        # Save temporary audio file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as fp:
            audio.export(fp.name, format="wav")
            with st.spinner("Mendengarkan..."):
                voice_text = transcribe_audio(fp.name)
            os.remove(fp.name)
        st.info(f"Terdeteksi: {voice_text}")

# Main Chat Area
st.title("💬 AI Asisten Pribadi (Offline)")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image" in message:
            st.image(message["image"], width=300)
        if "audio" in message:
            st.audio(message["audio"])

# Chat Input Logic
prompt = st.chat_input("Ketik pesan kamu di sini...")

# Handle Voice Input auto-submission
if voice_text and not prompt:
    prompt = voice_text

# Image Input (Placed in expander to keep UI clean)
with st.expander("📷 Upload Gambar untuk AI"):
    uploaded_image = st.file_uploader("Pilih gambar...", type=["jpg", "png", "jpeg"])

if prompt:
    # 1. Display User Message
    with st.chat_message("user"):
        st.markdown(prompt)
        image_data = None
        if uploaded_image:
            st.image(uploaded_image, width=300)
            # Encode image
            image_b64 = encode_image_to_base64(uploaded_image)
            image_data = f"data:image/png;base64,{image_b64}"

    # Prepare message for history
    user_msg = {"role": "user", "content": prompt}
    if uploaded_image:
        user_msg["image"] = uploaded_image # Store for display
    st.session_state.messages.append(user_msg)

    # 2. Generate AI Response
    if st.session_state.llm:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            # Construct messages for LLM
            llm_messages = []

            # System Prompt (Optional: You can add a default personality)
            system_prompt = "Kamu adalah asisten AI yang cerdas, membantu, dan berbahasa Indonesia dengan baik."
            if file_context:
                system_prompt += f" Berikut adalah informasi tambahan dari dokumen yang diupload user: {file_context}"

            llm_messages.append({"role": "system", "content": system_prompt})

            # Add History (Limit to last 5 turns to save context)
            for msg in st.session_state.messages[-10:-1]: # Exclude current one first
                content = msg["content"]
                # Note: We are simplifying history. Complex multimodal history requires handling image urls in history.
                # For this MVP, we might only send text history + current image.
                llm_messages.append({"role": msg["role"], "content": content})

            # Add Current Message
            current_content = [{"type": "text", "text": prompt}]
            if image_data:
                current_content.append({"type": "image_url", "image_url": {"url": image_data}})

            llm_messages.append({"role": "user", "content": current_content})

            # Stream Response
            try:
                stream_response = st.session_state.llm.create_chat_completion(
                    messages=llm_messages,
                    stream=True
                )

                for chunk in stream_response:
                    if "choices" in chunk:
                        delta = chunk["choices"][0]["delta"]
                        if "content" in delta:
                            full_response += delta["content"]
                            message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)

                # Generate Audio Response (Optional - Toggle in real app, but here we do it automatically if voice was used?)
                # Let's do it if the prompt was short (likely voice) or add a button?
                # For simplicity: always generate TTS if user used voice?
                # Let's just generate it if it's not too long to keep it snappy, or add a 'Play' button logic is hard in Streamlit streaming.
                # We will just generate it.

                audio_file = run_tts(full_response)
                if audio_file:
                    st.audio(audio_file)
                    st.session_state.messages.append({"role": "assistant", "content": full_response, "audio": audio_file})
                else:
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"Error generating response: {e}")
    else:
        st.warning("⚠️ Model belum dimuat. Silakan pilih dan muat model di sidebar kiri.")
