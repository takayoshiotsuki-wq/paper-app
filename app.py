import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai

# --- ページ設定 ---
st.set_page_config(page_title="APA Citation Generator", page_icon="📄")

# --- サイドバー設定 ---
with st.sidebar:
    st.title("⚙️ 設定")
    api_key = st.text_input("Gemini API Keyを入力", type="password").strip()
    st.info("APIキーは Google AI Studio で取得したものを使用してください。")

# --- メイン画面 ---
st.title("📄 論文参考文献ジェネレーター")
st.write("PDFをアップロードすると、標準APA形式と日本語版APA形式の2種類を作成します。")

# --- 処理関数 ---
def process_pdf(file, key):
    # 通信設定と最新モデルの指定
    genai.configure(api_key=key, transport='rest')
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # PDFからテキスト抽出（最初の2ページ）
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for i in range(min(2, len(doc))):
        text += doc[i].get_text()
    
    # AIへの詳細な指示（プロンプト）
    # アスタリスクの禁止と、区切り文字の指定を追加
    prompt = f"""
    以下の論文テキストから情報を抽出し、2つの形式で参考文献リストを作成してください。

    1. 【標準APA形式】（英語論文用：日本語著者はローマ字表記、タイトルに英訳を付記）
    2. 【日本語版APA形式】（日本語論文用：漢字表記を維持）

    [制約事項]
    - アスタリスク（*）を使用したイタリック体や太字の装飾は、コピー時の邪魔になるため一切行わないでください。
    - 各形式の間に '---' という文字列を入れて区切ってください。

    テキスト:
    {text}
    """
    response = model.generate_content(prompt)
    return response.text

# --- 実行部分 ---
uploaded_file = st.file_uploader("PDFを選択してください", type="pdf")

if uploaded_file and api_key:
    if st.button("参考文献を生成"):
        with st.spinner("AIが解析中..."):
            try:
                result = process_pdf(uploaded_file, api_key)
                
                # AIの回答を区切り文字で分割
                parts = result.split('---')
                
                st.success("生成が完了しました！")
                
                # --- 標準APA形式の表示 ---
                st.subheader("🌐 標準APA形式 (English/Romanized)")
                st.write("英語論文に引用する場合はこちら:")
                # st.code を使うと、マウスオーバーで右上にコピーボタンが出ます
                st.code(parts[0].replace('1.', '').strip(), language="text")
                
                # --- 日本語版APA形式の表示 ---
                st.subheader("🇯🇵 日本語版APA形式 (Kanji)")
                st.write("日本語論文に引用する場合はこちら:")
                if len(parts) > 1:
                    st.code(parts[1].replace('2.', '').strip(), language="text")
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
elif uploaded_file and not api_key:
    st.warning("左側のサイドバーにAPIキーを入力してください。")
