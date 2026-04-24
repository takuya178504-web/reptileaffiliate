import os
import json
import requests
import anthropic
from datetime import datetime
from pathlib import Path

RAKUTEN_APP_ID = os.environ["RAKUTEN_APP_ID"]
RAKUTEN_AFFILIATE_ID = os.environ.get("RAKUTEN_AFFILIATE_ID", "")
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
RAKUTEN_ACCESS_KEY = os.environ["RAKUTEN_ACCESS_KEY"]

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
]


def fetch_rakuten_products(keyword, num=5):
    url = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260401"
    params = {
        "applicationId": RAKUTEN_APP_ID,
        "accessKey": RAKUTEN_ACCESS_KEY,
        "affiliateId": RAKUTEN_AFFILIATE_ID,
        "keyword": keyword,
        "hits": num,
        "sort": "-reviewCount",
        "imageFlag": 1,
        "formatVersion": 2,
        "format": "json",
    }
    headers = {"Referer": "https://github.com"}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    data = resp.json()
    print(f"APIレスポンス: {data}")
    return data.get("Items", [])


def generate_article(keyword, products):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    product_info = ""
    for i, item in enumerate(products, 1):
        affiliate_url = item.get("affiliateUrl") or item.get("itemUrl", "")
        product_info += f"""
商品{i}: {item['itemName']}
価格: {item['itemPrice']}円
レビュー数: {item.get('reviewCount', 0)}件
評価: {item.get('reviewAverage', 0)}点
URL: {affiliate_url}
"""

    prompt = f"""あなたはペット専門のアフィリエイトライターです。
以下のキーワードと商品情報をもとに、SEOに最適化された日本語の記事をHTML形式で書いてください。

キーワード: {keyword}

商品情報:
{product_info}

要件:
- h1タグでタイトル、導入文（200文字程度）、各商品をh2で紹介、最後にまとめ
- 各商品に「楽天で見る →」リンクを含める（URLはそのまま使用）
- 読者に寄り添った自然で親しみやすい文章
- 文字数: 1000〜1500文字
- HTMLのbodyタグ内の内容のみ出力（head・bodyタグ自体は不要）
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
    <title>{keyword} おすすめ商品 | 爬虫類グッズ比較</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.8; color: #333; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #27ae60; padding-bottom: 10px; }}
        h2 {{ color: #27ae60; margin-top: 40px; }}
        a.btn {{ display: inline-block; background: #bf0000; color: white; padding: 8px 20px; border-radius: 4px; text-decoration: none; margin-top: 10px; }}
        a.btn:hover {{ background: #8b0000; }}
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
        links += f'<li><a href="{article["filename"]}">{article["keyword"]} おすすめ商品</a></li>\n        '

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
        li {{ margin: 12px 0; padding: 12px; border: 1px solid #ddd; border-radius: 6px; }}
        a {{ color: #bf0000; text-decoration: none; font-size: 1.05em; }}
        a:hover {{ text-decoration: underline; }}
        footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #999; font-size: 0.85em; }}
    </style>
</head>
<body>
    <h1>🦎 爬虫類グッズ比較・おすすめ情報</h1>
    <p>レオパ・ボールパイソンなど爬虫類の飼育に必要なグッズを徹底比較！<br>楽天市場の人気商品からおすすめを厳選してご紹介します。</p>
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
        print(f"処理中: {keyword}")
        products = fetch_rakuten_products(keyword)
        if not products:
            print(f"商品が見つかりません: {keyword}")
            continue
        content = generate_article(keyword, products)
        filename = save_article(keyword, content)
        entry = {"keyword": keyword, "filename": filename, "date": datetime.now().strftime("%Y-%m-%d")}
        new_articles.append(entry)
        print(f"記事を保存: {filename}")

    all_articles.extend(new_articles)
    save_articles_index(all_articles)
    update_index(all_articles)
    print(f"完了! {len(new_articles)}記事を生成しました。")


if __name__ == "__main__":
    main()
