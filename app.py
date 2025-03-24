import google.generativeai as genai
import os
from dotenv import load_dotenv
import tempfile
import PyPDF2
import docx
import pandas as pd
import time
from datetime import datetime
import uuid
from supabase import create_client, Client
import json
import traceback
import streamlit as st

# 環境変数の読み込み
load_dotenv()

# ページ設定
st.set_page_config(
    page_title="AI自動要約ツール",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    /* 全体のフォント設定 */
    * {
        font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
    }
    
    /* メインタイトル */
    .main-title {
        color: #1E88E5;
        font-size: 2.2rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid #f0f0f0;
    }
    
    /* サブタイトル */
    .subtitle {
        color: #424242;
        font-size: 1.4rem;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding-left: 0.5rem;
        border-left: 4px solid #1E88E5;
    }
    
    /* Streamlitの要素をカスタマイズ */
    div.stButton > button {
        border-radius: 6px;
        font-weight: 600;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* カード */
    .card {
        background-color: #fff;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        padding: 15px;
        margin-bottom: 15px;
        border-left: 3px solid #1E88E5;
    }
    
    /* タブのスタイリング */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-radius: 6px;
        background-color: #f5f7f9;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        border-radius: 6px;
        margin: 0 2px;
        gap: 5px;
        padding: 8px 16px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #e3f2fd;
        border-bottom: 2px solid #1976D2;
    }
    
    /* サイドバー調整 */
    section[data-testid="stSidebar"] {
        background-color: #fafafa;
    }
    
    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    
    /* 結果カード */
    .result-box {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 16px;
        margin: 16px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* プログレスバー */
    div.stProgress > div > div > div {
        background-color: #1E88E5;
    }
    
    /* ファイルアップローダー */
    .file-uploader {
        border: 2px dashed #bdbdbd;
        border-radius: 6px;
        padding: 20px;
        text-align: center;
        background-color: #fafafa;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .file-uploader:hover {
        border-color: #1E88E5;
        background-color: #f5f9ff;
    }
    
    /* モード選択 */
    .mode-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 12px;
        margin-bottom: 20px;
    }
    
    .mode-item {
        background-color: #f8f9fa;
        border-radius: 6px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        cursor: pointer;
        position: relative;
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid #e0e0e0;
    }
    
    .mode-item:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-color: #90CAF9;
    }
    
    .mode-item-selected {
        background-color: #e3f2fd;
        border: 1px solid #1976D2;
        box-shadow: 0 2px 5px rgba(0,0,0,0.08);
    }
    
    .mode-icon {
        font-size: 2rem;
        margin-bottom: 10px;
        display: block;
    }
    
    /* 履歴アイテム */
    .history-item {
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        margin-bottom: 10px;
        overflow: hidden;
        background-color: white;
    }
    
    .history-header {
        background-color: #f5f7f9;
        padding: 10px 15px;
        border-bottom: 1px solid #e0e0e0;
        font-weight: 600;
    }
    
    .history-content {
        padding: 15px;
    }
    
    .history-date {
        color: #757575;
        font-size: 0.85rem;
    }
    
    /* ボタンスタイル */
    .primary-button {
        background-color: #1976D2;
        color: white;
    }
    
    .secondary-button {
        background-color: #f5f5f5;
        color: #333;
        border: 1px solid #ddd;
    }
    
    /* テキストエリア */
    .stTextArea textarea {
        border-radius: 6px;
        border: 1px solid #e0e0e0;
        min-height: 180px;
        padding: 10px;
    }
    
    /* フッター */
    .footer {
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #f0f0f0;
        text-align: center;
        color: #9e9e9e;
        font-size: 0.9rem;
    }
    
    /* 空の表示エリア */
    .empty-state {
        text-align: center;
        padding: 40px;
        color: #9e9e9e;
    }
    
    .empty-state-icon {
        font-size: 3rem;
        margin-bottom: 15px;
        color: #bdbdbd;
    }
    
    /* アラート・通知 */
    div[data-baseweb="notification"] {
        border-radius: 6px;
    }
    
    /* 設定グループ */
    .settings-group {
        background-color: #f9f9f9;
        border-radius: 6px;
        padding: 15px;
        margin-bottom: 20px;
    }
    
    .settings-label {
        font-weight: 600;
        margin-bottom: 10px;
        color: #424242;
    }
    
    /* デバッグ情報 */
    .debug-info {
        background-color: #f5f5f5;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 10px;
        font-family: monospace;
        font-size: 0.8rem;
        overflow-x: auto;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Gemini API キーの設定
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("GEMINI_API_KEYが設定されていません。.envファイルを確認してください。")
    st.stop()

# ユーザーIDの取得または生成
def get_or_create_user_id():
    # クッキーを使用してユーザーIDを管理
    import streamlit as st
    import uuid

    # クッキーからユーザーIDを取得
    user_id = st.session_state.get('persistent_user_id')
    
    # クッキーにユーザーIDが存在しない場合は新規作成
    if not user_id:
        user_id = str(uuid.uuid4())
        st.session_state['persistent_user_id'] = user_id
    
    return user_id

# セッション状態の初期化
if 'user_id' not in st.session_state:
    st.session_state.user_id = "shared_user"  # 全ユーザーで共通のID

if 'history' not in st.session_state:
    st.session_state.history = []

if 'selected_mode' not in st.session_state:
    st.session_state.selected_mode = "general_summary"

if 'max_chars' not in st.session_state:
    st.session_state.max_chars = 30000

if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

# Supabase 設定
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = None

# Supabaseクライアントの初期化
if supabase_url and supabase_key:
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # 接続テスト
        try:
            response = supabase.table('summaries').select('*').execute()
            record_count = len(response.data) if hasattr(response, 'data') else 0
            
            st.sidebar.success(f"Supabaseに接続しました (レコード数: {record_count})", icon="✅")
        except Exception as count_error:
            st.sidebar.error(f"レコード数の取得に失敗しました: {str(count_error)}")
            supabase = None
            
    except Exception as e:
        st.sidebar.error(f"Supabase接続エラー: {str(e)}")
        if st.session_state.get('debug_mode', False):
            st.sidebar.error(traceback.format_exc())
        supabase = None
else:
    st.sidebar.warning("Supabase認証情報が設定されていません。ローカルモードで動作します。", icon="⚠️")

# Gemini API の設定
genai.configure(api_key=api_key)

# モデルの設定
try:
    # 最新のモデル名で試行
    model = genai.GenerativeModel('gemini-1.5-pro')
except Exception as e:
    try:
        # 旧モデル名でも試行
        model = genai.GenerativeModel('gemini-pro')
    except Exception as inner_e:
        st.error(f"モデル初期化エラー: {str(inner_e)}")
        st.info("利用可能なモデルを確認しています...")
        try:
            # 利用可能なモデルのリストを取得
            available_models = genai.list_models()
            model_names = [model.name for model in available_models]
            st.info(f"利用可能なモデル: {', '.join(model_names)}")
            
            # テキスト生成をサポートするモデルを探す
            text_models = [model for model in available_models if "generateContent" in model.supported_generation_methods]
            if text_models:
                model = genai.GenerativeModel(text_models[0].name)
                st.success(f"モデル '{text_models[0].name}' を使用します")
            else:
                st.error("テキスト生成に対応したモデルが見つかりませんでした")
                st.stop()
        except Exception as list_e:
            st.error(f"利用可能なモデルを取得できませんでした: {str(list_e)}")
            st.stop()

# プロンプトテンプレート
PROMPT_TEMPLATES = {
    "general_summary": "以下の文章を読み、内容を3〜5点に簡潔に日本語で要約してください。 ・簡潔な文章 ・分かりやすく要点を箇条書き ・一般的な読者が理解できる表現 文章: {text}",
    "business_summary": "以下のビジネス文書を読み、上司や同僚がすぐに内容を理解できるように、重要な要点を日本語で3点に要約してください。 ・ビジネス文書にふさわしい文体 ・客観的かつ明確な表現 ・箇条書きで簡潔に 文書: {text}",
    "single_sentence": "以下の文章を読み、全体の内容を一文で簡潔に日本語で要約してください。 ・わかりやすく一文で ・日本語で自然な表現 文章: {text}",
    "keyword_extraction": "以下の文章から、特に重要なキーワードを日本語で5つ抽出してください。 ・専門用語や話題の中心となる語を優先 ・キーワードのみカンマ区切りで出力 文章: {text}",
    "sentiment_analysis": "以下の文章の感情傾向を分析してください。 ・ポジティブ / ネガティブ / 中立 の3分類 ・分類理由を簡潔に説明 ・日本語で出力 文章: {text}"
}

# モード設定
MODES = {
    "general_summary": {
        "name": "📋 一般要約モード", 
        "description": "ざっくり内容を掴みたいときに使用。内容を3〜5点に簡潔に要約します。",
        "icon": "📋"
    },
    "business_summary": {
        "name": "🧑‍💼 ビジネス要約モード", 
        "description": "会議メモや報告書の要点をすぐ掴みたいとき。重要な要点を3点に要約します。",
        "icon": "🧑‍💼"
    },
    "single_sentence": {
        "name": "✏️ 一文要約モード", 
        "description": "全体を一言で掴みたいとき。内容を一文で簡潔に要約します。",
        "icon": "✏️"
    },
    "keyword_extraction": {
        "name": "📊 キーワード抽出モード", 
        "description": "文章のキモとなる単語を抽出。重要なキーワードを5つ抽出します。",
        "icon": "📊"
    },
    "sentiment_analysis": {
        "name": "🧠 感情分析モード", 
        "description": "文章の感情傾向を知る。ポジティブ/ネガティブ/中立で分類します。",
        "icon": "🧠"
    }
}

# 履歴読み込み関数の修正
def load_history_from_supabase():
    if not supabase:
        return []
    
    try:
        # 全ユーザーの履歴を取得
        response = supabase.table('summaries').select('*').order('created_at', desc=True).execute()
        
        if st.session_state.debug_mode:
            st.sidebar.write(f"取得レコード数: {len(response.data) if hasattr(response, 'data') else 0}")
        
        if hasattr(response, 'data'):
            return response.data
        return []
    except Exception as e:
        st.error(f"履歴の取得に失敗しました: {str(e)}")
        if st.session_state.debug_mode:
            st.error(traceback.format_exc())
        return []

# 他の関数からuser_idの条件を削除
def save_to_supabase(history_item):
    if not supabase:
        return False
    
    try:
        timestamp = datetime.now().isoformat()
        
        supabase_data = {
            'id': history_item['id'],
            'user_id': 'shared_user',  # 固定のユーザーID
            'mode': history_item['mode'],
            'input_preview': history_item['input'][:500],
            'result': history_item['result'],
            'file_name': history_item.get('file_name', ''),
            'created_at': timestamp
        }
        
        
        if st.session_state.debug_mode:
            st.write("### デバッグ: 保存するデータ")
            st.json(supabase_data)
        
        # データを挿入
        response = supabase.table('summaries').insert(supabase_data).execute()
        
        return True
    except Exception as e:
        st.error(f"保存に失敗しました: {str(e)}")
        if st.session_state.debug_mode:
            st.error(traceback.format_exc())
        return False

# その他の関連する関数も同様に修正
def delete_from_supabase(history_id):
    if not supabase:
        return False
    
    try:
        response = supabase.table('summaries').delete().eq('id', history_id).eq('user_id', st.session_state.persistent_user_id).execute()
        return True
    except Exception as e:
        st.error(f"削除に失敗しました: {str(e)}")
        if st.session_state.debug_mode:
            st.error(traceback.format_exc())
        return False

def delete_all_history_from_supabase():
    if not supabase:
        return False
    
    try:
        response = supabase.table('summaries').delete().eq('user_id', st.session_state.persistent_user_id).execute()
        return True
    except Exception as e:
        st.error(f"全履歴の削除に失敗しました: {str(e)}")
        if st.session_state.debug_mode:
            st.error(traceback.format_exc())
        return False

# ファイルからテキストを抽出する関数
def extract_text_from_file(uploaded_file):
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension == 'txt':
        # テキストファイルの場合
        return uploaded_file.getvalue().decode('utf-8')
    
    elif file_extension == 'pdf':
        # PDFファイルの場合
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_file_path = temp_file.name
        
        text = ""
        try:
            with open(temp_file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            st.error(f"PDFの読み込みエラー: {str(e)}")
            text = ""
        finally:
            os.unlink(temp_file_path)  # 一時ファイルを削除
        
        return text
    
    elif file_extension in ['docx', 'doc']:
        # Word文書の場合
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_file_path = temp_file.name
        
        text = ""
        try:
            doc = docx.Document(temp_file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            st.error(f"Word文書の読み込みエラー: {str(e)}")
            text = ""
        finally:
            os.unlink(temp_file_path)  # 一時ファイルを削除
        
        return text
    
    elif file_extension in ['csv', 'xlsx', 'xls']:
        # CSVまたはExcelファイルの場合
        try:
            if file_extension == 'csv':
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # データフレームをテキストに変換
            return df.to_string()
        except Exception as e:
            st.error(f"表計算ファイルの読み込みエラー: {str(e)}")
            return ""
    
    else:
        st.error(f"サポートされていないファイル形式です: {file_extension}")
        return None

# テキストを要約する関数
def summarize_text(text, mode):
    if not text:
        return "テキストが提供されていません。"
    
    # 文字数制限（Gemini APIの上限に合わせて調整）
    max_chars = st.session_state.max_chars
    if len(text) > max_chars:
        text = text[:max_chars] + "..."
        st.warning(f"テキストが長すぎるため、最初の{max_chars:,}文字のみを使用します。")
    
    # プロンプトを準備
    prompt = PROMPT_TEMPLATES[mode].format(text=text)
    
    try:
        # Gemini APIを呼び出し
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"APIエラーが発生しました: {str(e)}")
        if st.session_state.debug_mode:
            st.error(traceback.format_exc())
        return None

# サイドバー要素を描画する関数
def render_sidebar():
    st.sidebar.markdown(f"<h1 style='font-size: 1.5rem; color: #1E88E5;'>📝 AI自動要約ツール</h1>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    # ナビゲーション
    pages = {
        "🏠 ホーム": home_page,
        "📚 履歴": history_page,
        "⚙️ 設定": settings_page,
        "❓ ヘルプ": help_page
    }
    
    selected_page = st.sidebar.radio("ページ選択", list(pages.keys()), label_visibility="collapsed")
    
    st.sidebar.markdown("---")
    
    # 使用中のモデル情報
    st.sidebar.markdown("### 使用中のモデル")
    st.sidebar.info(f"Gemini API: {model.model_name}")
    
    # ユーザー情報
    st.sidebar.markdown("### ユーザー情報")
    st.sidebar.info(f"ユーザーID: {st.session_state.user_id[:8]}...")
    
    # デバッグモード切替
    st.sidebar.markdown("### デバッグ設定")
    debug_mode = st.sidebar.checkbox("デバッグモードを有効にする", value=st.session_state.debug_mode)
    if debug_mode != st.session_state.debug_mode:
        st.session_state.debug_mode = debug_mode
        st.experimental_rerun()
    
    # 統計情報
    if st.session_state.history:
        st.sidebar.markdown("### 統計")
        history_count = len(st.session_state.history)
        st.sidebar.markdown(f"📊 履歴数: {history_count}")
        
        # 各モードの使用回数をカウント
        mode_counts = {}
        for item in st.session_state.history:
            mode = item.get("mode", "general_summary")
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
        
        # 最も使用されたモード
        if mode_counts:
            most_used_mode = max(mode_counts.items(), key=lambda x: x[1])[0]
            if most_used_mode in MODES:
                st.sidebar.markdown(f"👑 よく使うモード: {MODES[most_used_mode]['name']}")
    
    # フッター
    st.sidebar.markdown("---")
    st.sidebar.markdown("<div style='text-align: center; color: #9e9e9e; font-size: 0.8rem;'>© 2025 AI自動要約ツール<br>Powered by Gemini API & Supabase</div>", unsafe_allow_html=True)
    
    # 選択したページの関数を返す
    return pages[selected_page]

# モード選択用UI
def mode_selector():
    st.markdown('<div class="subtitle">要約モードを選択</div>', unsafe_allow_html=True)
    
    # 選択中のモードを取得
    selected_mode = st.session_state.get('selected_mode', 'general_summary')
    
    # モード選択をカスタムUIで実装
    st.markdown('<div class="mode-container">', unsafe_allow_html=True)
    
    cols = st.columns(len(MODES))
    for i, (mode_key, mode_info) in enumerate(MODES.items()):
        with cols[i]:
            is_selected = mode_key == selected_mode
            select_style = "mode-item mode-item-selected" if is_selected else "mode-item"
            
            st.markdown(f"""
            <div class="{select_style}">
                <div class="mode-icon">{mode_info['icon']}</div>
                <div style="font-weight: bold; margin-bottom: 5px;">{mode_info['name'].split(' ')[1]}</div>
                <div style="font-size: 0.8rem; color: #666;">{mode_info['description']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 選択ボタン
            if st.button(f"選択" if not is_selected else "✓ 選択中", 
                        key=f"select_{mode_key}", 
                        use_container_width=True):
                st.session_state.selected_mode = mode_key
                st.experimental_rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 選択中のモードのバッジを表示
    st.markdown(f"""
    <div style="display: inline-block; background-color: #e3f2fd; color: #1565C0; padding: 5px 10px; 
         border-radius: 20px; font-size: 0.9rem; margin-top: 10px;">
        {MODES[selected_mode]['icon']} {MODES[selected_mode]['name']}
    </div>
    """, unsafe_allow_html=True)
    
    return selected_mode

# ホームページの実装
def home_page():
    st.markdown('<h1 class="main-title">📝 AI自動要約ツール</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    テキスト、PDF、Word、CSV/Excelファイルを自動で要約・分析するツールです。
    モードを選択して、文章を要約しましょう。
    """)
    
    # テキスト入力とファイルアップロードのタブ
    input_tab1, input_tab2 = st.tabs(["📄 テキスト入力", "📁 ファイルアップロード"])
    
    input_text = ""
    file_name = None
    
    with input_tab1:
        input_text = st.text_area(
            "テキストを入力してください:", 
            height=200, 
            help=f"要約したいテキストを入力してください。最大{st.session_state.max_chars:,}文字まで処理できます。"
        )
        
    with input_tab2:
        st.markdown('<div class="file-uploader">', unsafe_allow_html=True)
        st.markdown("📂 ファイルをドラッグ＆ドロップまたは選択してください")
        st.markdown("**サポート形式:** .txt, .pdf, .docx, .doc, .csv, .xlsx, .xls")
        uploaded_file = st.file_uploader("ファイルをアップロード", 
                                         type=["txt", "pdf", "docx", "doc", "csv", "xlsx", "xls"],
                                         label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file is not None:
            file_name = uploaded_file.name
            with st.spinner("ファイルを読み込んでいます..."):
                input_text = extract_text_from_file(uploaded_file)
            
            if input_text:
                st.success(f"📄 '{file_name}' の読み込みが完了しました。")
                with st.expander("抽出されたテキスト（プレビュー）"):
                    preview_text = input_text[:500] + ("..." if len(input_text) > 500 else "")
                    st.text_area("プレビュー", preview_text, height=150, disabled=True)
    
    # モード選択
    selected_mode = mode_selector()
    
    # 要約ボタン
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 4])
    with col1:
        summarize_button = st.button("🚀 要約開始", type="primary", use_container_width=True)
    
    # 結果表示
    if summarize_button:
        if not input_text:
            st.error("テキストが入力されていないか、ファイルから読み込まれていません。")
        else:
            with st.spinner(f"{MODES[selected_mode]['name']}で処理中..."):
                # プログレスバーを表示
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)  # 実際の処理時間に合わせて調整
                    progress_bar.progress(i + 1)
                
                # 要約実行
                result = summarize_text(input_text, selected_mode)
            
            if result:
                # 履歴アイテムを作成
                timestamp = datetime.now().isoformat()
                history_id = str(uuid.uuid4())
                
                history_item = {
                    "id": history_id,
                    "timestamp": timestamp,
                    "mode": selected_mode,
                    "input": input_text[:150] + "..." if len(input_text) > 150 else input_text,
                    "result": result,
                    "file_name": file_name
                }
                
                # 履歴をセッションに保存
                st.session_state.history.append(history_item)
                
                # Supabaseにも保存
                if supabase:
                    with st.spinner("データベースに保存中..."):
                        success = save_to_supabase(history_item)
                        if success:
                            st.success("履歴がデータベースに保存されました", icon="✅")
                        else:
                            st.error("データベースへの保存に失敗しました")
                
                # 結果表示
                st.markdown('<div class="subtitle">要約結果</div>', unsafe_allow_html=True)
                
                # 結果ボックス
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.write(result)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # アクションボタン
                col1, col2, col3 = st.columns(3)
                
                # テキストファイルとしてダウンロード
                with col1:
                    download_filename = f"要約結果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    st.download_button(
                        label="📥 テキストでダウンロード",
                        data=result,
                        file_name=download_filename,
                        mime="text/plain",
                        use_container_width=True
                    )
                
                # クリップボードコピーボタン
                with col2:
                    st.button("📋 結果をコピー", 
                             help="テキストを選択してCtrl+CまたはCmd+Cでコピーできます",
                             use_container_width=True)
                
                # 新しい要約
                with col3:
                    if st.button("🔄 新しい要約を作成", use_container_width=True):
                        st.experimental_rerun()

# 履歴ページの実装
def history_page():
    st.markdown('<h1 class="main-title">📚 履歴</h1>', unsafe_allow_html=True)
    
    # Supabaseから最新の履歴を読み込む
    if supabase:
        with st.spinner("履歴を更新しています..."):
            db_history = load_history_from_supabase()
            
            # デバッグモードで詳細表示
            if st.session_state.debug_mode and db_history:
                with st.expander("データベースから取得した履歴データ"):
                    st.json(db_history)
            
            if db_history:
                # 古い履歴を削除して新しい履歴で更新
                st.session_state.history = []
                for item in db_history:
                    st.session_state.history.append({
                        'id': item.get('id', str(uuid.uuid4())),
                        'timestamp': item.get('created_at', datetime.now().isoformat()),
                        'mode': item.get('mode', 'general_summary'),
                        'input': item.get('input_preview', ''),
                        'result': item.get('result', ''),
                        'file_name': item.get('file_name', '')
                    })
    
    if not st.session_state.history:
        # 履歴がない場合の表示
        st.markdown('<div class="empty-state">', unsafe_allow_html=True)
        st.markdown('<div class="empty-state-icon">📝</div>', unsafe_allow_html=True)
        st.markdown('履歴はまだありません。ホームページで文章を要約してみましょう。', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ホームページへのリンク
        st.button("🏠 ホームに戻る", on_click=lambda: st.session_state.update({"current_page": "home"}))
        return
    
    # 履歴の表示オプション
    st.markdown('<div class="subtitle">履歴を表示</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        display_option = st.selectbox(
            "表示順", 
            options=["最新のものから表示", "古いものから表示", "モード別に表示"],
            index=0
        )
    
    # 検索オプション
    with col2:
        search_term = st.text_input("🔍 検索", placeholder="キーワードで検索...")
    
    # 履歴をフィルタリング/ソート
    filtered_history = st.session_state.history.copy()
    
    # 検索フィルタリング
    if search_term:
        filtered_history = [
            item for item in filtered_history 
            if search_term.lower() in item.get("result", "").lower() or 
               (item.get("file_name") and search_term.lower() in item.get("file_name", "").lower())
        ]
    
    # 表示順の適用
    if display_option == "最新のものから表示":
        # タイムスタンプでソート (ISO形式なので文字列比較でもOK)
        filtered_history = sorted(filtered_history, key=lambda x: x.get('timestamp', ''), reverse=True)
    elif display_option == "古いものから表示":
        filtered_history = sorted(filtered_history, key=lambda x: x.get('timestamp', ''))
    elif display_option == "モード別に表示":
        st.markdown("### モードを選択")
        mode_filter = st.selectbox(
            "モード", 
            list(MODES.keys()), 
            format_func=lambda x: MODES[x]["name"],
            label_visibility="collapsed"
        )
        filtered_history = [item for item in filtered_history if item.get("mode") == mode_filter]
        # モード内で日時順にソート
        filtered_history = sorted(filtered_history, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # 履歴数を表示
    if filtered_history:
        st.markdown(f"**{len(filtered_history)}件**の履歴が見つかりました")
    elif search_term:
        st.warning(f"「{search_term}」に一致する履歴は見つかりませんでした")
    
    # 履歴表示
    for i, item in enumerate(filtered_history):
        # item["mode"]が存在することを確認
        mode_key = item.get("mode", "general_summary")
        if mode_key not in MODES:
            mode_key = "general_summary"  # デフォルト値を設定
        
        # タイムスタンプを読みやすい形式に変換
        try:
            # ISO形式からdatetimeオブジェクトに変換
            if isinstance(item.get('timestamp', ''), str):
                dt = datetime.fromisoformat(item.get('timestamp', '').replace('Z', '+00:00'))
                display_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                display_time = item.get('timestamp', '日時不明')
        except:
            display_time = item.get('timestamp', '日時不明')
            
        with st.container():
            st.markdown(f"""
            <div class="history-item">
                <div class="history-header">
                    {MODES[mode_key]['icon']} {MODES[mode_key]['name']}
                    <span class="history-date">🕒 {display_time}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("詳細を表示", expanded=False):
                if item.get('file_name'):
                    st.markdown(f"**ファイル名:** {item.get('file_name')}")
                
                # 入力テキストのプレビュー
                st.markdown("**入力テキスト:**")
                st.text_area("", item.get('input', ''), height=80, disabled=True, key=f"input_{i}")
                
                # 結果表示
                st.markdown("**要約結果:**")
                
                with st.container():
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.write(item.get('result', '結果なし'))
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # アクションボタン
                col1, col2, col3 = st.columns(3)
                with col1:
                    # テキストファイルとしてダウンロード
                    timestamp_str = display_time.replace(':', '-').replace(' ', '_')
                    download_filename = f"要約結果_{timestamp_str}.txt"
                    st.download_button(
                        label="📥 テキストでダウンロード",
                        data=item.get('result', ''),
                        file_name=download_filename,
                        mime="text/plain",
                        key=f"download_{i}",
                        use_container_width=True
                    )
                
                with col2:
                    # 同じモードで再実行
                    if st.button("🔄 同じモードで再実行", key=f"rerun_{i}", use_container_width=True):
                        st.session_state.selected_mode = item.get('mode', 'general_summary')
                        st.experimental_rerun()
                
                with col3:
                    # 履歴から削除
                    if st.button("🗑️ この履歴を削除", key=f"delete_{i}", use_container_width=True):
                        history_id = item.get('id')
                        if history_id:
                            # Supabaseから削除
                            if supabase:
                                with st.spinner("データベースから削除中..."):
                                    success = delete_from_supabase(history_id)
                                    if success:
                                        st.success("履歴がデータベースから削除されました", icon="✅")
                            
                            # セッションからも削除
                            st.session_state.history = [h for h in st.session_state.history if h.get('id') != history_id]
                            st.experimental_rerun()
    
    # 履歴をクリアするボタン
    if filtered_history:
        st.markdown("---")
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🗑️ 履歴をすべて削除", type="secondary", use_container_width=True):
                # 確認ダイアログ
                st.warning("⚠️ すべての履歴が削除されます。この操作は元に戻せません。")
                confirm_col1, confirm_col2 = st.columns(2)
                with confirm_col1:
                    if st.button("✅ はい、すべて削除します", key="confirm_delete_all", use_container_width=True):
                        # Supabaseからすべて削除
                        if supabase:
                            with st.spinner("データベースから削除中..."):
                                success = delete_all_history_from_supabase()
                                if success:
                                    st.success("すべての履歴がデータベースから削除されました", icon="✅")
                        
                        # セッションもクリア
                        st.session_state.history = []
                        st.experimental_rerun()
                with confirm_col2:
                    if st.button("❌ キャンセル", key="cancel_delete_all", use_container_width=True):
                        st.experimental_rerun()

# 設定ページの実装
def settings_page():
    st.markdown('<h1 class="main-title">⚙️ 設定</h1>', unsafe_allow_html=True)
    
    # タブで設定カテゴリを分ける
    tabs = st.tabs(["API設定", "データベース設定", "要約設定"])
    
    with tabs[0]:
        st.markdown('<div class="subtitle">API設定</div>', unsafe_allow_html=True)
        
        with st.form("api_settings"):
            st.markdown('<div class="settings-group">', unsafe_allow_html=True)
            st.markdown('<div class="settings-label">Gemini API 設定</div>', unsafe_allow_html=True)
            
            api_key_input = st.text_input("API キー", 
                                         value=api_key if api_key else "", 
                                         type="password",
                                         help="Google AI StudioからAPI Keyを取得してください")
            
            model_name = st.selectbox("使用するモデル",
                                     ["gemini-1.5-pro", "gemini-pro", "gemini-1.0-pro"],
                                     index=0,
                                     help="テキスト生成に使用するGemini APIのモデル")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            submit_api = st.form_submit_button("API設定を保存", use_container_width=True)
        
        if submit_api:
            st.success("✅ API設定を保存しました！")
            st.info("📝 .envファイルに以下の内容を記述してください:")
            st.code(f'GEMINI_API_KEY={api_key_input}', language="text")
    
    with tabs[1]:
        st.markdown('<div class="subtitle">データベース設定</div>', unsafe_allow_html=True)
        
        with st.form("db_settings"):
            st.markdown('<div class="settings-group">', unsafe_allow_html=True)
            st.markdown('<div class="settings-label">Supabase 設定</div>', unsafe_allow_html=True)
            
            supabase_url_input = st.text_input("Supabase URL", 
                                             value=supabase_url if supabase_url else "",
                                             help="SupabaseのプロジェクトURLを入力してください")
            
            supabase_key_input = st.text_input("Supabase Key", 
                                             value=supabase_key if supabase_key else "",
                                             type="password",
                                             help="Supabaseのanon keyまたはservice roleキーを入力してください")
            
            st.markdown("""
            ※ Supabaseでは以下のテーブルを作成する必要があります:
            
            ```sql
            CREATE TABLE summaries (
              id UUID PRIMARY KEY,
              user_id UUID NOT NULL,
              mode TEXT NOT NULL,
              input_preview TEXT,
              result TEXT NOT NULL,
              file_name TEXT,
              created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            CREATE INDEX summaries_user_id_idx ON summaries (user_id);
            ```
            """)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            submit_db = st.form_submit_button("データベース設定を保存", use_container_width=True)
        
        if submit_db:
            st.success("✅ データベース設定を保存しました！")
            st.info("📝 .envファイルに以下の内容を記述してください:")
            st.code(f'SUPABASE_URL={supabase_url_input}\nSUPABASE_KEY={supabase_key_input}', language="text")
            st.warning("⚠️ 設定を反映するには、アプリケーションを再起動する必要があります。")
    
    with tabs[2]:
        st.markdown('<div class="subtitle">要約設定</div>', unsafe_allow_html=True)
        
        with st.form("summary_settings"):
            st.markdown('<div class="settings-group">', unsafe_allow_html=True)
            st.markdown('<div class="settings-label">テキスト処理設定</div>', unsafe_allow_html=True)
            
            max_length = st.slider("最大文字数制限", 
                                  1000, 50000, st.session_state.max_chars, 1000,
                                  format="%d文字",
                                  help="要約処理する最大文字数。長いテキストは切り詰められます。")
            
            # カスタムプロンプトのチェックボックス
            use_custom_prompt = st.checkbox("カスタムプロンプトを使用", 
                                         help="オリジナルの指示文を使用して要約します。")
            
            # カスタムプロンプトのテキストエリア
            custom_prompt = ""
            if use_custom_prompt:
                custom_prompt = st.text_area(
                    "カスタムプロンプト",
                    "以下の文章を読み、内容を要約してください。文章: {text}",
                    help="テキストは {text} プレースホルダーで置き換えられます。"
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            submit_summary = st.form_submit_button("要約設定を保存", use_container_width=True)
        
        if submit_summary:
            st.session_state.max_chars = max_length
            st.success("✅ 要約設定を保存しました！")
            if use_custom_prompt and custom_prompt:
                st.info("🔧 カスタムプロンプトが設定されました。")

# ヘルプページの実装
def help_page():
    st.markdown('<h1 class="main-title">❓ ヘルプ</h1>', unsafe_allow_html=True)
    
    # ヘルプセクション
    with st.expander("🔍 AI自動要約ツールとは？", expanded=True):
        st.markdown("""
        **AI自動要約ツール**は、Gemini APIを活用して長文（ニュース記事・ビジネス文書など）を自動で要約・分析する業務効率化ツールです。

        Streamlitで実装されており、ユーザーが複数の要約モードから選択して、テキストやファイルを効率的に処理できます。
        
        要約結果はSupabaseデータベースに保存され、後から参照することができます。
        """)
    
    with st.expander("💡 使い方ガイド"):
        st.markdown("""
        ### 基本的な使い方

        1. **ホーム画面**で、テキスト入力またはファイルアップロードを選択
        2. 要約したいテキストを入力、またはファイルをアップロード
        3. 5つの要約モードから目的に合ったものを選択
        4. 「要約開始」ボタンをクリック
        5. 結果を確認、必要に応じてダウンロードやコピーが可能
        6. 履歴は自動的にSupabaseデータベースに保存されます

        ### 各モードの特徴
        
        - **一般要約モード**: 内容を3〜5点に簡潔に要約
        - **ビジネス要約モード**: ビジネス文書の要点を3点に要約
        - **一文要約モード**: 全体を一文で簡潔に要約
        - **キーワード抽出モード**: 重要なキーワードを5つ抽出
        - **感情分析モード**: ポジティブ/ネガティブ/中立の3分類で感情傾向を分析
        """)
    
    with st.expander("🗄️ データベース設定"):
        st.markdown("""
        このアプリケーションは、Supabaseデータベースを使用して履歴を保存します。
        
        ### Supabase設定手順
        
        1. [Supabase](https://supabase.com/) でアカウントを作成
        2. 新しいプロジェクトを作成
        3. SQL Editorで以下のクエリを実行してテーブルを作成:
        
        ```sql
        CREATE TABLE summaries (
          id UUID PRIMARY KEY,
          user_id UUID NOT NULL,
          mode TEXT NOT NULL,
          input_preview TEXT,
          result TEXT NOT NULL,
          file_name TEXT,
          created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX summaries_user_id_idx ON summaries (user_id);
        ```
        
        4. 「Project Settings」→「API」から「URL」と「anon」キーを取得
        5. 設定ページでSupabaseのURLとキーを入力
        6. アプリケーションを再起動して設定を反映
        """)
    
    with st.expander("📂 サポートファイル形式"):
        st.markdown("""
        以下のファイル形式がサポートされています：
        
        | ファイル種別 | 拡張子 | 備考 |
        | --- | --- | --- |
        | テキストファイル | .txt | UTF-8エンコーディング推奨 |
        | PDFファイル | .pdf | テキスト抽出可能なPDFに対応 |
        | Wordファイル | .docx, .doc | 最新のWord形式推奨 |
        | 表計算ファイル | .csv, .xlsx, .xls | 表形式データに対応 |
        
        ※ファイルサイズやテキスト長によっては処理に時間がかかる場合があります。
        """)
    
    with st.expander("❓ よくある質問"):
        st.markdown("""
        **Q: APIキーはどこで取得できますか？**  
        A: [Google AI Studio](https://aistudio.google.com/app/apikey) でAPIキーを取得できます。取得後、.envファイルに保存するか設定ページで入力してください。

        **Q: 履歴はどのように保存されますか？**  
        A: 履歴はSupabaseデータベースに保存されます。アプリを再起動しても履歴は保持されます。

        **Q: 文字数制限はありますか？**  
        A: 現在、デフォルトで最大30,000文字までの処理をサポートしています。それ以上の長さのテキストは自動的に切り詰められます。設定ページで上限を変更できます。

        **Q: 複数のファイルを一括処理できますか？**  
        A: 現在のバージョンでは、一度に1つのファイルのみ処理可能です。将来のアップデートで一括処理機能を追加予定です。

        **Q: APIエラーが発生する場合はどうすればよいですか？**  
        A: APIキーの確認、インターネット接続の確認、入力テキストの長さの確認を行ってください。問題が解決しない場合は、設定ページでモデルを変更してみてください。
        """)
    
    with st.expander("🔧 トラブルシューティング"):
        st.markdown("""
        ### 一般的な問題の解決方法

        **問題: Supabaseに接続できない**
        - URLとキーが正しいか確認してください
        - インターネット接続を確認してください
        - サーバーの状態を[Supabaseステータスページ](https://status.supabase.com/)で確認してください

        **問題: ファイルのアップロードに失敗する**
        - サポートされているファイル形式か確認してください
        - ファイルサイズが大きすぎないか確認してください（20MB以下推奨）
        - 別のファイル形式に変換して試してください

        **問題: 要約結果が表示されない**
        - インターネット接続を確認してください
        - APIキーが正しく設定されているか確認してください
        - 入力テキストが長すぎる場合は、短くしてみてください

        **問題: 履歴が保存されない**
        - Supabase接続が正常か確認してください
        - データベーステーブルが正しく設定されているか確認してください
        - サイドバーの「デバッグモードを有効にする」をオンにして詳細情報を確認してください
        """)
    
    with st.expander("🔄 更新履歴"):
        st.markdown("""
        **バージョン 1.0.0 (2025年3月)**
        - 初期リリース
        - 5つの要約モード実装
        - 複数ファイル形式のサポート

        **バージョン 1.1.0 (2025年3月)**
        - UI全面リニューアル
        - 履歴機能の追加
        - 設定ページの追加
        - ヘルプセクションの充実
        
        **バージョン 1.2.0 (2025年3月)**
        - 履歴検索機能の追加
        - UIの改善とバグ修正
        - エラーハンドリングの強化
        - ドキュメントの充実
        
        **バージョン 2.0.0 (2025年3月)**
        - Supabaseデータベース連携機能の追加
        - 履歴の永続化
        - データベース設定ページの追加
        - セキュリティ強化
        
        **バージョン 2.1.0 (2025年3月)**
        - ユーザーID管理の改善
        - デバッグモードの追加
        - データ表示の最適化
        - 結果表示の高速化
        """)
    
    st.markdown("### お問い合わせ")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **サポート窓口**  
        不明点や機能リクエストがございましたら、お気軽にお問い合わせください。
        
        **Email**: support@ai-summarizer.example.com  
        """)
    
    with col2:
        st.info("""
        **開発者情報**  
        
        **GitHub**: [github.com/example/ai-summarizer](https://github.com/example/ai-summarizer)  
        **ドキュメント**: [docs.ai-summarizer.example.com](https://docs.ai-summarizer.example.com)
        """)

# メイン関数
def main():
    # サイドバーからページ関数を取得
    page_function = render_sidebar()
    
    # 選択されたページ関数を実行
    page_function()
    
    # フッター（全ページ共通）
    st.markdown("""
    <div class="footer">
        <p>AI自動要約ツール v2.1.0</p>
        <p>© 2025 All Rights Reserved</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()