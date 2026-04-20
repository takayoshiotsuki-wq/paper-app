import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai

# --- ページ設定 ---
st.set_page_config(page_title="APA Generator", page_icon="📄")

# --- 履歴の初期化 ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- サイドバー設定 ---
with st.sidebar:
    st.title("Settings")
    api_key = st.text_input("Gemini API Key", type="password").strip()
    
    st.markdown("---")
    # 履歴リセットボタン
    if st.button("履歴をリセット"):
        st.session_state.history = []
        st.rerun()

# --- メメイン画面 ---
st.title("論文参考文献ジェネレーター")

# --- 処理関数 ---
def process_pdf(file, key):
    genai.configure(api_key=key, transport='rest')
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for i in range(min(2, len(doc))):
        text += doc[i].get_text()
    
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

# --- アップロード・生成部分 ---
uploaded_file = st.file_uploader("PDFを選択してください", type="pdf")

if uploaded_file and api_key:
    if st.button("生成"):
        with st.spinner("解析中..."):
            try:
                result = process_pdf(uploaded_file, api_key)
                parts = result.split('---')
                
                std_citation = parts[0].strip()
                jp_citation = parts[1].strip() if len(parts) > 1 else ""
                
                # --- 履歴に追加 (最新が上に来るように) ---
                st.session_state.history.insert(0, {
                    "filename": uploaded_file.name,
                    "standard": std_citation,
                    "japanese": jp_citation
                })
                
                # 直近の結果を表示
                st.markdown("---")
                st.markdown("### 標準APA形式")
                st.code(std_citation, language="text")
                
                st.markdown("### 日本語版APA形式")
                st.code(jp_citation, language="text")
                
            except Exception as e:
                st.error(f"Error: {e}")

# --- 履歴表示セクション ---
if st.session_state.history:
    st.markdown("---")
    st.title("履歴")
    
    for i, item in enumerate(st.session_state.history):
        # ファイル名を強調
        st.markdown(f"**ファイル: {item['filename']}**")
        
        # 1行でコピーしやすいようにまとめたテキスト
        # 標準形式 [改行] 日本語形式 という構成
        combined_text = f"{item['standard']}\n{item['japanese']}"
        
        # st.code のコピーボタンを利用して「1行（または1ブロック）コピー」を実現
        st.code(combined_text, language="text")
        st.markdown("---")
