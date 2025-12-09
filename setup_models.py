import os
from huggingface_hub import hf_hub_download

def download_models():
    models_dir = "models"
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    print("🚀 Memulai download model AI (Proses ini bergantung kecepatan internet)...")

    # 1. Main LLM (Brain) - Qwen2.5-1.5B-Instruct-GGUF
    # This is a very capable small model, perfect for i3 CPU.
    repo_id = "Qwen/Qwen2.5-1.5B-Instruct-GGUF"
    filename = "qwen2.5-1.5b-instruct-q4_k_m.gguf"

    print(f"\n⬇️ Downloading {filename} from {repo_id}...")
    try:
        hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=models_dir,
            local_dir_use_symlinks=False
        )
        print(f"✅ Berhasil: {filename}")
    except Exception as e:
        print(f"❌ Gagal download {filename}: {e}")

    # Optional: Vision Model (if we want separate vision, but for now we rely on the main one if it supports it,
    # or users can download Qwen2-VL manually. Qwen2.5 is text only.)
    # Note: Using Qwen2.5-1.5B (Text) with Image input will technically fail to "see" the image content
    # unless we use a VLM.
    # Let's also download a small VLM: Qwen2-VL-2B-Instruct-GGUF.
    # This might be slightly heavier but necessary for the "Vision" requirement.

    repo_id_vl = "Qwen/Qwen2-VL-2B-Instruct-GGUF"
    filename_vl = "qwen2-vl-2b-instruct-q4_k_m.gguf"

    print(f"\n⬇️ Downloading {filename_vl} (Model Vision) from {repo_id_vl}...")
    try:
        hf_hub_download(
            repo_id=repo_id_vl,
            filename=filename_vl,
            local_dir=models_dir,
            local_dir_use_symlinks=False
        )
        print(f"✅ Berhasil: {filename_vl}")
    except Exception as e:
        print(f"❌ Gagal download {filename_vl}: {e}")

    print("\n🎉 Semua download selesai! Model tersimpan di folder 'models/'.")
    print("Sekarang kamu bisa menjalankan aplikasi dengan: streamlit run main.py")

if __name__ == "__main__":
    download_models()
