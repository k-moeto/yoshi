from http.server import BaseHTTPRequestHandler
import json
import os
import google.generativeai as genai

class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        # CORSプリフライトリクエストの処理
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*') # すべてのオリジンを許可
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return

    def do_POST(self):
        # 1. リクエストボディの読み取り
        try:
            content_length = int(self.headers['Content-Length'])
            body_bytes = self.rfile.read(content_length)
            body_str = body_bytes.decode('utf-8')
            data = json.loads(body_str)
            input_text = data.get('text')
        except Exception as e:
            self._send_json_response({'error': f'リクエストの解析に失敗しました: {str(e)}'}, status_code=400)
            return

        if not input_text:
            self._send_json_response({'error': 'テキストがありません'}, status_code=400)
            return

        try:
            # 2. APIキーをVercelの環境変数から取得
            GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
            if not GEMINI_API_KEY:
                self._send_json_response({'error': 'APIキーがサーバーに設定されていません'}, status_code=500)
                return

            # 3. Gemini APIの呼び出し
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            prompt = self.create_prompt(input_text)
            
            response = model.generate_content(prompt)
            generated_quote = response.text.strip()

            # 4. 成功レスポンスを返す
            self._send_json_response({'quote': generated_quote})

        except Exception as e:
            self._send_json_response({'error': f'Gemini APIエラー: {str(e)}'}, status_code=500)
        
        return
    
    def _send_json_response(self, data, status_code=200):
        # JSONレスポンスを返すヘルパー関数
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*') # CORSヘッダー
        self.end_headers()
        # ensure_ascii=Falseで日本語の文字化けを防ぐ
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def create_prompt(self, user_text):
        # ユーザーから提供された例を忠実に再現
        return f"""
あなたは「山本由伸の言ってない名言ジェネレーター」です。
入力された平凡な言葉を、山本由伸風の「過剰に自信に満ちた、傲慢で絶対的なエース」のセリフに変換してください。

# 変換スタイルのルール
* 入力された言葉の本質的な意味を捉え、それを最大限に誇張する。
* 口調は「俺」。
* 相手、状況、ルールさえも見下すような、絶対的な自信を表現する。
* 平凡な目標を「すでに達成された当然の結果」かのように語る。

# スタイルの参考（「言った言葉」→「言ってない名言」）
* 言った: 「負けるわけにはいかない」
  → 言ってない: 「負けという選択肢はない」
* 言った: 「いつ投げる事になってもベストな投球ができるように」
  → 言ってない: 「俺を出す事が最善の選択肢だ」
* 言った: 「リリーフ陣に負担をかけたくない」
  → 言ってない: 「ブルペンのドアを施錠しておけ」
* 言った: 「点差が開いてもとても強力な打線なので油断せずに」
  → 言ってない: 「俺はキラーだ。倒れかけたらトドメを刺す」
* 言った: 「日本にいた頃と投球間隔が違って調整が上手くいかない事もありますが、今ある力を振り絞って…」
  → 言ってない: 「俺を日本式の中６日で投げさせろ。そうすれば最高の結果を出してやる」
* 言った: 「これ以上点を取られる訳にはいかないと思って」
  → 言ってない: 「これが今日お前らが得られる唯一の得点だ」
* 言った: 「監督やコーチを安心させられるように」
  → 言ってない: 「監督をベンチに縛りつけておけ」
* 言った: 「重要な1戦ですがいつもの調子でがんばります」
  → 言ってない: 「何ら問題ない。いつも通り始末するだけだ」
* 言った: 「自分に出来ることは全部できました」
  → 言ってない: 「俺に出来ないことはなかった」
* 言った: 「相手ピッチャーももの凄く良くて点が入らないのはわかっていた」
  → 言ってない: 「セカンドに入らなくていい際どい打球処理は全部俺がカバーしてやる」

# その他の参考スタイル
* 「俺はブルペンで肩を温めるから、お前らはシャンパンを冷やしておけ」
* 「連投の心配はしていない。ただトロントのシャンパンが口に合うかだけが唯一の心配だ。」
* 「相手は試される側だと理解すべきだ」
* 「子どもには山本由伸と名付けろ」
* 「俺が行く。完投からの中１日？知った事か」
* 「俺にとってこの状況は昼下がりのコーヒーブレイクと何ら変わらない平穏なものだ」
* 「第7戦のチケットは大事に取っとけ。きっと役に立つ」

# 変換タスク
以下の「入力された言葉」を、上記スタイルに基づいた「言ってない名言」に変換してください。

入力された言葉: 「{user_text}」

言ってない名言:
"""