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

ファイル名は半角小文字・数字・ハイフンを使います。タイトル・日付・概要は必須です。`draft = true`のままでは公開しません。`draft = false`にすると、Project-CDXページとホームへ自動でリンクを追加します。`updated`があれば更新日、なければ公開日の新しい順で表示します。homeは最近の6件を表示します。

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

ゲーム全体の説明は`content/project-cdx/overview.md`、概要・特徴・配布情報は`config/projects.json`、サイト名と公開URLは`config/site.json`を編集します。

## 現在のゲームのスクリーンショットに更新

Junctionのカバー・全体図とHardpointのプレイ画面は、サイトのルートから次の1コマンドで撮影・取り込み・再生成できます。Unityの画面表示とライセンス接続が使える通常のターミナルで実行してください。

```bash
bash scripts/refresh-junction.sh
```

ゲーム側のプロジェクトを一時コピーして撮影し、成功した画像のみ取り込みます。出力先は最初に表示される`/tmp/publab398-junction-*`です。取り込み後にJunctionとHardpointの記事の更新日時を設定し、ビルド・リンク検証を実行します。2026-10-10の今回の再撮影は画面表示・ライセンス接続エラーで失敗しているため、掲載画像の撮影日時は`config/screenshots.json`を参照してください。

生成する画像・CSSのURLにはファイル内容のハッシュを付けます。同じ名前で差し替えても、公開後は更新した画像が読み込まれます。

`fps-cdx` に自動撮影スクリプト、画角設定JSON、撮影メニューと手順書を追加しています。手順は隣のリポジトリの `scripts/capture-site-screenshots.md` を参照してください。描画できるUnity環境では `bash scripts/capture-site-screenshots.sh scripts/site-shots-junction.json` でHardpointを起動して撮影でき、画像を確認してJSONの位置・向き・画角を調整し、再撮影できます。手動ではEditorのPlay中に **Tools → FPS → Site Screenshots** から撮影でき、Junctionのプレイ画面は **F12** でも保存できます。

撮影した4枚を取り込むには、このリポジトリで次を実行します。

```bash
python3 scripts/import-screenshots.py ../fps-cdx/validation-logs/site-screenshots
python scripts/build.py
python scripts/check.py
```

1枚だけ更新する場合は `--shot gameplay`（または `cover`、`overview`、`starlight`）を指定します。取り込み前に画像を確認してください。取り込みツールはPNGと撮影メタデータの整合性を確認し、画像を`public/assets/`へ、撮影情報を`config/screenshots.json`へ保存します。Play中のEditorから撮影するため、配布ビルドも同じ内容であることを確認してください。

Junctionのカバー、全体図、Hardpointのプレイ画面とStarlight Parkの全体図は、2026-10-10に現在のEditorで撮影した画像へ更新済みです。撮影メタデータの`version`はEditorの設定値で、配布ビルドのバージョンとは別です。

武器8種類とエアストのタブレット画面は、`fps-cdx`側で以下の設定からまとめて撮影できます。説明用にプレイヤーとBotを静止させ、エアストのチャージを設定したオフライン撮影です。通常の試合で獲得したチャージを撮るものではありません。

```bash
# fps-cdxで実行
bash scripts/capture-site-screenshots.sh scripts/site-shots-guides.json validation-logs/site-guides

# このサイトのリポジトリで画像を確認してから実行
python3 scripts/import-screenshots.py ../fps-cdx/validation-logs/site-guides --group guides
```

武器8種類のプレイ画面とエアストのタブレット画面は、2026-10-10に撮影した画像へ更新済みです。撮影情報は`config/screenshots.json`、画像と選択アイコンの出典は`config/guide-image-sources.json`に記録しています。選択アイコンはゲーム内の素材です。

## 公開内容

ゲームのソースコード、Unityプロジェクト、開発Git履歴、ビルド、テスターのメールアドレスは含めません。サイト用の画像と、プレイヤー向けに書き直した紹介文だけを使っています。生成時に公開対象となるのは`public/`のファイルと、テンプレート・設定・公開記事から生成したページです。

画像と機能説明は開発時点の内容なので、配布ビルドに合わせて確認・更新してください。
