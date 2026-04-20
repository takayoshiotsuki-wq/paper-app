import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai

# ページの設定
st.set_page_config(page_title="APA Generator", page_icon="📄")

# サイドバーの設定
with st.sidebar:
    st.title("⚙️ 設定")
    api_key = st.text_input("Gemini API Keyを入力", type="password")
    st.info("APIキーは Google AI Studio で取得したものを使用してください。")

st.title("📄 論文 → APA参考文献作成")
st.write("PDFをアップロードすると、AIがAPA形式の参考文献リストを作成します。")

# 処理関数
def process_pdf(file, key):
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # PDFからテキスト抽出（最初の2ページ）
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for i in range(min(2, len(doc))):
        text += doc[i].get_text()
    
    # AIへの指示
    prompt = f"以下のテキストから論文情報を抽出し、APA第7版形式の参考文献を1つ作成してください。\n\n{text}"
    response = model.generate_content(prompt)
    return response.text

# 実行部分
uploaded_file = st.file_uploader("PDFを選択してください", type="pdf")

if uploaded_file and api_key:
    if st.button("作成開始"):
        with st.spinner("解析中..."):
            try:
                result = process_pdf(uploaded_file, api_key)
                st.success("完了しました！")
                st.code(result, language="text")
            except Exception as e:
                st.error(f"エラー: {e}")
elif uploaded_file and not api_key:
    st.warning("左側のサイドバーにAPIキーを入力してください。")