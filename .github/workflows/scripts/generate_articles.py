import os
import json
import anthropic
import urllib.parse
from datetime import datetime
from pathlib import Path

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
AMAZON_ASSOCIATE_ID = "aitak-22"

KEYWORDS = [
    "レオパードゲッコー ケージ",
    "ボールパイソン 飼育セット",
    "爬虫類 サーモスタット",
    "レオパ 床材",
    "爬虫類 紫外線ライト",
    "ヒョウモントカゲモドキ 餌",
    "爬虫類 ケージ おすすめ",
    "レオパ シェルター",
    "爬虫類 保温球",
    "レオパ カルシウムパウダー",
    "ボールパイソン ケージ",
    "爬虫類 温度計 湿度計",
    "レオパ 水入れ",
    "爬虫類 ピンセット",
    "コーンスネーク 飼育セット",
]


def amazon_search_url(keyword):
    encoded = urllib.parse.quote(keyword)
    return f"https://www.amazon.co.jp/s?k={encoded}&tag={AMAZON_ASSOCIATE_ID}"


def generate_article(keyword):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    amazon_url = amazon_search_url(keyword)

    prompt = f"""あなたはペット専門のアフィリエイトライターです。
以下のキーワードについて、SEOに最適化された日本語の記事をHTML形式で書いてください。

キーワード: {keyword}
AmazonリンクURL: {amazon_url}

要件:
- h1タグでタイトル（キーワードを含む）
- 導入文200文字程度（読者の悩みに共感する内容）
- h2で「{keyword}を選ぶポイント」（3〜4点を具体的に解説）
- h2で「Amazonでの選び方」（以下のリンクボタンを必ず含める）
  <a href="{amazon_url}" class="btn" target="_blank" rel="nofollow">Amazonで{keyword}を探す →</a>
- h2で「まとめ」（簡潔に）
- 文字数: 1000〜1500文字
- HTMLのbodyタグ内の内容のみ出力（html/head/bodyタグ不要）
- 自然で親しみやすい文体
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def save_article(keyword, content):
    slug = keyword.replace(" ", "-").replace("　", "-")
    date = datetime.now().strftime("%Y%m%d")
    filename = f"articles/{slug}-{date}.html"
    Path("articles").mkdir(exist_ok=True)

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{keyword} おすすめ・選び方 | 爬虫類グッズ比較</title>
    <meta name="description" content="{keyword}のおすすめ商品や選び方を解説。初心者にもわかりやすく紹介します。">
    <style>
        body {{ font-family: -apple-system, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.8; color: #333; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #27ae60; padding-bottom: 10px; }}
        h2 {{ color: #27ae60; margin-top: 40px; }}
        a.btn {{ display: inline-block; background: #FF9900; color: white; padding: 12px 24px; border-radius: 4px; text-decoration: none; margin: 15px 0; font-weight: bold; }}
        a.btn:hover {{ background: #e68a00; }}
        .back {{ margin-bottom: 20px; }}
        .back a {{ color: #666; text-decoration: none; }}
        footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #999; font-size: 0.85em; }}
    </style>
</head>
<body>
    <div class="back"><a href="../index.html">← トップへ戻る</a></div>
    {content}
    <footer>最終更新: {datetime.now().strftime("%Y年%m月%d日")} ※本記事にはアフィリエイトリンクが含まれます。</footer>
</body>
</html>"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return filename


def load_existing_articles():
    index_path = Path("articles_index.json")
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_articles_index(articles):
    with open("articles_index.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)


def update_index(all_articles):
    links = ""
    for article in sorted(all_articles, key=lambda x: x["date"], reverse=True):
        links += f'<li><a href="{article["filename"]}">{article["keyword"]} おすすめ・選び方</a></li>\n        '

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>爬虫類グッズ比較・おすすめ情報</title>
    <meta name="description" content="レオパ・ボールパイソンなど爬虫類の飼育に必要なグッズを徹底比較！初心者にもわかりやすく紹介します。">
    <style>
        body {{ font-family: -apple-system, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.8; color: #333; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #27ae60; padding-bottom: 10px; }}
        ul {{ padding: 0; list-style: none; }}
        li {{ margin: 12px 0; padding: 12px 16px; border: 1px solid #ddd; border-radius: 6px; }}
        a {{ color: #e67e00; text-decoration: none; font-size: 1.05em; }}
        a:hover {{ text-decoration: underline; }}
        footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #999; font-size: 0.85em; }}
    </style>
</head>
<body>
    <h1>🦎 爬虫類グッズ比較・おすすめ情報</h1>
    <p>レオパ・ボールパイソンなど爬虫類の飼育に必要なグッズを徹底比較！<br>初心者にもわかりやすく、おすすめ商品を紹介します。</p>
    <ul>
        {links}
    </ul>
    <footer>最終更新: {datetime.now().strftime("%Y年%m月%d日")} ※本サイトにはアフィリエイトリンクが含まれます。</footer>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)


def main():
    import random
    all_articles = load_existing_articles()
    done_keywords = {a["keyword"] for a in all_articles}
    remaining = [k for k in KEYWORDS if k not in done_keywords]
    if not remaining:
        remaining = KEYWORDS

    keywords = random.sample(remaining, min(2, len(remaining)))
    new_articles = []

    for keyword in keywords:
        print(f"記事生成中: {keyword}")
        content = generate_article(keyword)
        filename = save_article(keyword, content)
        entry = {"keyword": keyword, "filename": filename, "date": datetime.now().strftime("%Y-%m-%d")}
        new_articles.append(entry)
        print(f"完了: {filename}")

    all_articles.extend(new_articles)
    save_articles_index(all_articles)
    update_index(all_articles)
    print(f"完了! {len(new_articles)}記事を生成しました。")


if __name__ == "__main__":
    main()
