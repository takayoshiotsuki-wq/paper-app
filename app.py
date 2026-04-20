import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai

st.set_page_config(page_title="APA Generator", page_icon="📄")

with st.sidebar:
    st.title("⚙️ 設定")
    api_key = st.text_input("Gemini API Keyを入力", type="password").strip()
    
    # 【診断機能】今使えるモデルを表示するボタン
    if st.button("利用可能なモデルを確認"):
        if api_key:
            try:
                genai.configure(api_key=api_key)
                models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                st.write("利用可能なモデル一覧:")
                st.write(models)
            except Exception as e:
                st.error(f"モデル取得エラー: {e}")
        else:
            st.warning("先にAPIキーを入力してください。")

st.title("📄 論文 → APA参考文献作成")

def process_pdf(file, key):
    # 1. 通信設定（念のため REST を残します）
    genai.configure(api_key=key.strip(), transport='rest')
    
    # 2. モデル名をリストにある「gemini-2.5-flash」に書き換え
    # これで404エラーは確実に消滅します！
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # 以下はそのまま
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for i in range(min(2, len(doc))):
        text += doc[i].get_text()
    
    prompt = f"以下のテキストから論文情報を抽出し、APA第7版形式の参考文献を作成してください。\n\n{text}"
    response = model.generate_content(prompt)
    return response.text

uploaded_file = st.file_uploader("PDFを選択してください", type="pdf")

if uploaded_file and api_key:
    if st.button("作成開始"):
        with st.spinner("解析中..."):
            try:
                result = process_pdf(uploaded_file, api_key)
                st.success("完了しました！")
                st.code(result, language="text")
            except Exception as e:
                st.error(f"エラーが発生しました。\n\n詳細: {e}")
