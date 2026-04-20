import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai

# --- ページ設定 ---
st.set_page_config(page_title="APA Generator", page_icon="📄")

# --- サイドバー設定 ---
with st.sidebar:
    st.title("Settings")
    api_key = st.text_input("Gemini API Key", type="password").strip()

# --- メイン画面 ---
st.title("論文参考文献ジェネレーター")

# --- 処理関数 ---
def process_pdf(file, key):
    genai.configure(api_key=key, transport='rest')
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for i in range(min(2, len(doc))):
        text += doc[i].get_text()
    
    # AIへの指示をより厳格に：余計な文字を一切出さないよう指定
    prompt = f"""
    以下のテキストから論文情報を抽出し、2タイプの参考文献を作成してください。
    
    [出力形式]
    1行目に標準APA形式のみ
    2行目に --- 
    3行目に日本語版APA形式のみ

    [制約事項]
    - 「標準APA形式：」といった見出しや説明、アスタリスク(*)による装飾は一切禁止します。
    - 参考文献の文字列のみを正確に出力してください。

    テキスト:
    {text}
    """
    response = model.generate_content(prompt)
    return response.text

# --- 実行部分 ---
uploaded_file = st.file_uploader("PDFを選択してください", type="pdf")

if uploaded_file and api_key:
    if st.button("生成"):
        with st.spinner("解析中..."):
            try:
                result = process_pdf(uploaded_file, api_key)
                
                # --- 区切り文字で分割 ---
                parts = result.split('---')
                
                st.markdown("---") # 視覚的な区切り線
                
                # 標準APA形式
                st.markdown("### 標準APA形式")
                st.code(parts[0].strip(), language="text")
                
                # 日本語版APA形式
                if len(parts) > 1:
                    st.markdown("### 日本語版APA形式")
                    st.code(parts[1].strip(), language="text")
                
            except Exception as e:
                st.error(f"Error: {e}")
elif uploaded_file and not api_key:
    st.info("サイドバーにAPIキーを入力してください。")
