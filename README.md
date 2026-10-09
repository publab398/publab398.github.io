# 398

友達や周りの人に、作っているゲームを紹介するためのサイト。公開URLは **https://publab398.github.io/** です。

Project-CDXのゲーム概要、画像、操作説明、テスト版のダウンロード先をまとめています。Hardpointをメインモードとして紹介し、FFAはサブモードとして遊び方の説明に載せています。宣伝用のコピーではなく、遊ぶ人が内容と操作を確認できる文言にします。

## ローカルで確認

Python 3.11以上を使います（GitHub Actionsは3.13）。

```bash
cd /home/taiseitakano/playground/publab398.github.io
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/build.py
python scripts/check.py
python -m http.server 8398 --directory _site --bind 127.0.0.1
```

ブラウザで http://127.0.0.1:8398/ を開きます。編集後はbuild.pyを再実行してください。`_site/`は生成物で、Gitには含めません。画像は`public/assets/`に置きます。

## 初回のGitHub公開

`publab398.github.io`を使うには、GitHub上で`publab398`というユーザーまたはOrganizationが必要です。既存の個人アカウントから管理する**Organization**を想定しています。名前の取得可否は未確認です。

1. GitHubの **Settings → Organizations → New organization** で、`publab398`を作成します。Freeプランで利用できます。
2. Organization配下に、**public**な`publab398.github.io`リポジトリを作成します。README・ライセンス・gitignoreは追加せず、空で作成してください。
3. 作成したリポジトリの **Settings → Pages → Build and deployment → Source** を **GitHub Actions** にします。
4. このローカルリポジトリで以下を実行します（HTTPS認証が必要です）。

```bash
git remote -v
git push -u origin main
```

`origin`には`https://github.com/publab398/publab398.github.io.git`を設定する想定です。未設定の場合は次を実行します。

```bash
git remote add origin https://github.com/publab398/publab398.github.io.git
```

5. **Actions → Build and deploy Pages** が成功したら、https://publab398.github.io/ を確認します。

以降はmainへのpushで自動公開します。Pull Requestではビルドとリンクの検証だけを行います。

## Google Driveのリンクを設定

`config/projects.json`のProject-CDXの`build`を編集します。

```json
"build": {
  "drive_url": "https://drive.google.com/drive/folders/ここにフォルダID",
  "version": "実際のビルド番号",
  "updated": "2026-10-09",
  "note": "ダウンロードには、アクセスを許可されたGoogleアカウントが必要です。"
}
```

`drive_url`がnullの場合は「配布準備中」と表示します。versionとupdatedも未確定ならnullのままで構いません。Driveの`latest`フォルダは**制限付き**にし、許可するテスターを閲覧者として追加して、ダウンロードを許可してください。

サイトはDrive内を取得しません。ビルド差し替え時に、表示するバージョンや更新日も更新してください。

## 特集・お知らせを追加

記事はMarkdown、先頭のメタデータは`+++`で囲んだTOMLです。テンプレートをコピーして使います。

- ステージ・武器などの特集: `examples/feature.md` → `content/project-cdx/features/任意の名前.md`
- 注目アップデートや配布のお知らせ: `examples/news.md` → `content/project-cdx/news/任意の名前.md`

ファイル名は半角小文字・数字・ハイフンを使います。タイトル・日付・概要は必須です。`draft = true`のままでは公開しません。`draft = false`にすると、Project-CDXページとホームへ自動でリンクを追加します。記事の日付が新しいものから表示します。

```toml
+++
title = "新しいステージを紹介"
date = "2026-10-09"
summary = "カードと記事冒頭に表示する短い紹介。"
label = "マップ紹介"
cover = "/assets/自分の画像.png"
cover_alt = "画像の内容を説明"
draft = false
+++
```

URLは`/project-cdx/features/任意の名前/`または`/project-cdx/news/任意の名前/`になります。画像なしの記事ではcoverとcover_altを省略できます。見出し、リンク、画像、リスト、表、コードブロックを使えます。HTMLは無効です。

毎回のアップデートを記事にする必要はありません。プレイヤーに紹介したいものがあるときに追加する運用です。

ゲーム全体の説明は`content/project-cdx/overview.md`、概要・特徴・配布情報は`config/projects.json`、サイト名と公開URLは`config/site.json`を編集します。

## 現在のゲームのスクリーンショットに更新

`fps-cdx` に自動撮影スクリプト、画角設定JSON、撮影メニューと手順書を追加しています。手順は隣のリポジトリの `scripts/capture-site-screenshots.md` を参照してください。描画できるUnity環境では `bash scripts/capture-site-screenshots.sh scripts/site-shots-junction.json` でHardpointを起動して撮影でき、画像を確認してJSONの位置・向き・画角を調整し、再撮影できます。手動ではEditorのPlay中に **Tools → FPS → Site Screenshots** から撮影でき、Junctionのプレイ画面は **F12** でも保存できます。

撮影した4枚を取り込むには、このリポジトリで次を実行します。

```bash
python3 scripts/import-screenshots.py ../fps-cdx/validation-logs/site-screenshots
python scripts/build.py
python scripts/check.py
```

1枚だけ更新する場合は `--shot gameplay`（または `cover`、`overview`、`starlight`）を指定します。取り込み前に画像を確認してください。取り込みツールはPNGと撮影メタデータの整合性を確認し、画像を`public/assets/`へ、撮影情報を`config/screenshots.json`へ保存します。Play中のEditorから撮影するため、配布ビルドも同じ内容であることを確認してください。

現時点の画像は既存資料から選んだもので、新しい撮影画像への差し替えはまだ行っていません。

## 公開内容

ゲームのソースコード、Unityプロジェクト、開発Git履歴、ビルド、テスターのメールアドレスは含めません。サイト用の画像4点と、プレイヤー向けに書き直した紹介文だけを使っています。生成時に公開対象となるのは`public/`のファイルと、テンプレート・設定・公開記事から生成したページです。

画像はProject-CDXの既存資料から選んでいます。画像と機能説明は開発時点の内容なので、配布ビルドに合わせて確認・更新してください。
