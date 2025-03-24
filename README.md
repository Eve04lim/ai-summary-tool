# AI自動要約ツール

Gemini API を使用して長文（ニュース記事・ビジネス文書など）を自動で要約・分析する業務効率化ツールです。

## 機能

- **一般要約モード**: ざっくり内容を掴みたいときに使用。内容を3〜5点に簡潔に要約します。
- **ビジネス要約モード**: 会議メモや報告書の要点をすぐ掴みたいとき。重要な要点を3点に要約します。
- **一文要約モード**: 全体を一言で掴みたいとき。内容を一文で簡潔に要約します。
- **キーワード抽出モード**: 文章のキモとなる単語を抽出。重要なキーワードを5つ抽出します。
- **感情分析モード**: 文章の感情傾向を知る。ポジティブ/ネガティブ/中立で分類します。

## セットアップ方法

### 1. リポジトリのクローン

```bash
git clone https://github.com/yourusername/ai-summarizer-tool.git
cd ai-summarizer-tool
```

### 2. 仮想環境のセットアップと必要なパッケージのインストール

```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
# Windowsの場合:
venv\Scripts\activate
# macOS/Linuxの場合:
source venv/bin/activate

# 必要なパッケージのインストール
pip install -r requirements.txt
```

### 3. Gemini API キーの設定

1. [Google AI Studio](https://aistudio.google.com/app/apikey) でAPIキーを取得してください
2. `.env` ファイルを作成し、APIキーを設定します:

```
GEMINI_API_KEY=your_api_key_here
```

### 4. アプリケーションの起動

```bash
streamlit run app.py
```

ブラウザで自動的に `http://localhost:8501` が開き、アプリケーションが表示されます。

## 使用方法

1. サイドバーから要約モードを選択します
2. テキスト入力またはファイルアップロードを選択します
3. テキストを入力するか、サポートされているファイル（.txt, .pdf, .docx, .doc, .csv, .xlsx, .xls）をアップロードします
4. 「要約する」ボタンをクリックします
5. 結果を確認し、必要に応じてコピーします

## 技術仕様

- **フロントエンド**: Streamlit
- **AI API**: Google Gemini Pro
- **サポートファイル形式**: TXT, PDF, DOCX, DOC, CSV, XLSX, XLS

## 注意事項

- テキストの最大長は30,000文字までです（Gemini APIの制限による）
- APIキーの使用量と料金にご注意ください

## ライセンス

[MIT License](LICENSE)