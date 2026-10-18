# 398Playground

398Playgroundのゲーム紹介サイト。公開URLは **https://publab398.github.io/** です。

Vaultcore Arena（旧開発名称: Project-CDX）のゲーム概要、画像、操作説明、テスト版のダウンロード先をまとめています。Hardpointをメインモードとして紹介し、FFAはサブモードとして遊び方の説明に載せています。宣伝用のコピーではなく、遊ぶ人が内容と操作を確認できる文言にします。

## ローカルで確認

Python 3.11以上を使います（GitHub Actionsは3.13）。

```bash
cd publab398.github.io
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

## 名称と表記

正式な名称は設定ファイルで一元管理し、テンプレートとビルドスクリプトから参照します。

| 項目 | 表記 | 定義場所 |
| --- | --- | --- |
| サイト名・開発者名 | 398Playground | `config/site.json`の`name` |
| コピーライト | © 2026 398Playground. All rights reserved. | `config/site.json`の`copyright` |
| ゲーム名 | Vaultcore Arena | `config/projects.json`の`name` |
| 旧開発名称 | Project-CDX | `config/projects.json`の`former_name` |
| 開発・パブリッシャー | 398Playground | `config/projects.json`の`developer`・`publisher` |

ページタイトル、Open Graph、ヘッダー・フッター、パンくず、ダウンロード欄はこれらの値から生成します。ヘッダーのロゴは「398」マーク（`templates/base.html`のSVG、`public/assets/favicon.svg`と同じ図柄）と「Playground」の文字で398Playgroundと読ませる表示です。Markdownの記事本文とリンク文にはゲーム名を直接書いているため、名称を変えるときは`content/`も検索してください。

次の識別子は、公開URLや既存のリンクを壊さないためにProject-CDX由来のまま残しています。

- ゲームページのURL `/project-cdx/`（`config/projects.json`の`slug`）と、記事のURL・`content/project-cdx/`
- 画像のファイル名 `public/assets/project-cdx-*`
- ビルドの実行ファイル名 `ProjectCDX.exe`（ゲーム側のビルド設定で決まるため、サイトでは変更しない）

## Google Driveのリンクを設定

`config/projects.json`のVaultcore Arenaの`build`を編集します。

```json
"build": {
  "drive_url": "https://drive.google.com/drive/folders/ここにフォルダID",
  "version": "実際のビルド番号",
  "updated": "2026-10-09",
  "channel": "限定プレイテスト（開発ビルド）",
  "install": "ダウンロードしたZIPを展開し、`ProjectCDX.exe`を起動します。",
  "limitations": ["既知の制限を1項目ずつ"],
  "note": "ダウンロードには、アクセスを許可されたGoogleアカウントが必要です。"
}
```

`drive_url`がnullの場合は「配布準備中」と表示します。versionとupdatedも未確定ならnullのままで構いません。`channel`・`install`・`limitations`は省略でき、省略した項目はダウンロード欄に表示しません。`install`と`limitations`ではMarkdownのインラインコード（`` ` ``）などを使えます。Driveの`latest`フォルダは**制限付き**にし、許可するテスターを閲覧者として追加して、ダウンロードを許可してください。

サイトはDrive内を取得しません。ビルド差し替え時に、表示するバージョンや更新日も更新してください。

## 特集・お知らせを追加

記事はMarkdown、先頭のメタデータは`+++`で囲んだTOMLです。テンプレートをコピーして使います。

- ステージ・武器などの特集: `examples/feature.md` → `content/project-cdx/features/任意の名前.md`
- 注目アップデートや配布のお知らせ: `examples/news.md` → `content/project-cdx/news/任意の名前.md`

ファイル名は半角小文字・数字・ハイフンを使います。タイトル・日付・概要は必須です。`draft = true`のままでは公開しません。`draft = false`にすると、ゲームページ（`/project-cdx/`）とホームへ自動でリンクを追加します。`updated`があれば更新日、なければ公開日の新しい順で表示します。homeは最近の6件を表示します。

```toml
+++
title = "新しいステージを紹介"
date = "2026-10-09"
updated = "2026-10-10T01:32:04+09:00"
summary = "カードと記事冒頭に表示する短い紹介。"
label = "マップ紹介"
cover = "/assets/自分の画像.png"
cover_alt = "画像の内容を説明"
draft = false
+++
```

URLは`/project-cdx/features/任意の名前/`または`/project-cdx/news/任意の名前/`になります。画像なしの記事ではcoverとcover_altを省略できます。見出し、リンク、画像、リスト、表、コードブロックを使えます。HTMLは無効です。

既存の記事を更新するときは、`date`を公開日のまま残し、`updated`を編集日時へ更新します。`updated`は省略可能で、`YYYY-MM-DD`またはタイムゾーン付きの日時を指定できます。同日の更新順も反映したいときは日時を使います。日付のみの指定は日本時間の午前0時として扱います（`config/site.json`の`timezone`で変更可能）。記事とhomeには更新日を表示します。

武器記事は`gallery = "weapons"`と`[[weapons]]`の名前・種類・画像・短い説明からカードを生成します。画像と説明の重複を避け、画像をクリックすると原寸で確認できます。

毎回のアップデートを記事にする必要はありません。プレイヤーに紹介したいものがあるときに追加する運用です。

ゲーム全体の説明は`content/project-cdx/overview.md`、概要・特徴・配布情報は`config/projects.json`、サイト名・コピーライト・公開URLは`config/site.json`を編集します。

## 公開内容

ゲームのソースコード、Unityプロジェクト、開発Git履歴、ビルド、テスターのメールアドレスは含めません。サイト用の画像と、プレイヤー向けに書き直した紹介文だけを使っています。生成時に公開対象となるのは`public/`のファイルと、テンプレート・設定・公開記事から生成したページです。

画像と機能説明は開発時点の内容なので、配布ビルドに合わせて確認・更新してください。
