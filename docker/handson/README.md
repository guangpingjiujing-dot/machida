# Docker ハンズオン

Python の標準ライブラリだけで動く最小構成のWebサーバーを使って、Docker の基本操作を体験する。

## ファイル構成

```
handson/
├── app.py              # Pythonの標準ライブラリだけで動くWebサーバー
├── Dockerfile          # イメージの定義
├── docker-compose.yml  # Compose設定
└── README.md           # この手順書
```

---

## 事前確認: Docker がインストールされているか確認する

### Docker のバージョン確認

```bash
docker --version
```

`Docker version 27.x.x, build xxxxxxx` のように表示されれば OK。

### Docker デーモンの起動確認

```bash
docker info
```

正常に情報が表示されれば Docker デーモンが起動している。

`Cannot connect to the Docker daemon` というエラーが出た場合は Docker Desktop を起動する。

### 動作確認（Hello World）

```bash
docker run hello-world
```

`Hello from Docker!` と表示されれば Docker は正しく動いている。

---

## Part 1: Dockerfile からイメージをビルドしてコンテナを動かす

### Step 1: イメージをビルドする

```bash
docker build -t myapp .
```

- `-t myapp` : ビルドしたイメージに `myapp` という名前（タグ）をつける
- `.` : このディレクトリの `Dockerfile` を使う

ビルドが完了したらイメージが作られていることを確認する。

```bash
docker images
```

`myapp` が一覧に表示されれば OK。

---

### Step 2: コンテナを起動する

```bash
docker run -p 8000:8000 --name mycontainer myapp
```

- `-p 8000:8000` : ホストの 8000番ポートをコンテナの 8000番ポートにつなぐ
- `--name mycontainer` : コンテナに名前をつける
- `myapp` : 使うイメージ名


ブラウザで http://localhost:8000 を開いて確認する。

---

### Step 3: コンテナの中に入る

コンテナは動かしたまま、**別のターミナルを開いて**以下を実行する。

```bash
docker exec -it mycontainer bash
```

- `exec` : 起動中のコンテナでコマンドを実行する
- `-it` : インタラクティブ（対話的）にターミナルを使う
- `mycontainer` : 対象のコンテナ名
- `bash` : 実行するコマンド（bashシェルを起動）

コンテナの中に入ると、プロンプトが変わる（例: `root@abc123:/app#`）。

コンテナの中を見てみる。

```bash
# 作業ディレクトリの確認
pwd

# ファイル一覧
ls

# app.py の中身を確認
cat app.py

# OS情報の確認（slim版Debianが入っている）
cat /etc/os-release
```

コンテナから出るには `exit` を入力する。

```bash
exit
```

---

### Step 4: コンテナを停止・削除する

最初のターミナルで `Ctrl + C` を押してコンテナを停止する。

停止後、コンテナを削除する。

```bash
docker stop mycontainer   # 停止（すでに止まっていればスキップ可）
docker rm mycontainer     # 削除
```

削除できたか確認する。

```bash
docker ps -a
```

`mycontainer` が表示されなければ OK。

---

## Part 2: Docker Compose で起動する

### Step 1: Compose でビルド＆起動

```bash
docker compose up --build
```

- `--build` : 起動前にイメージを再ビルドする（初回は必須）

ブラウザで http://localhost:8000 を開いて確認する。

バックグラウンドで動かしたい場合は `-d` をつける。

```bash
docker compose up --build -d
```

---

### Step 2: 起動状態を確認する

```bash
docker compose ps
```

`web` と `db` の両サービスが `running` になっていれば OK。

`web` は自前の Dockerfile からビルドしたイメージ、`db` は Docker Hub から取得した公式の PostgreSQL イメージが使われている。

---

### Step 3: コンテナの中に入る（Compose の場合）

**web サービスに入る**

```bash
docker compose exec web bash
```

- `exec` : 起動中のサービスのコンテナに入る
- `web` : `docker-compose.yml` に書いたサービス名

中に入ったらファイルを確認して `exit` で出る。

---

**db サービス（PostgreSQL）に入る**

```bash
docker compose exec db bash
```

コンテナの中に入ったら `psql` で PostgreSQL に接続する。

```bash
psql -U user -d mydb
```

接続できたら SQL を試してみる。

```sql
-- バージョン確認
SELECT version();

-- テーブル一覧（最初は何もない）
\dt

-- 接続を終了
\q
```

`psql` を終了したら `exit` でコンテナからも出る。

---

### Step 4: 停止・削除する

```bash
docker compose down
```

コンテナとネットワークが削除される。イメージは残る。

イメージも一緒に削除したい場合は `--rmi all` をつける。

```bash
docker compose down --rmi all
```

---

## まとめ

| やったこと | コマンド |
|---|---|
| イメージのビルド | `docker build -t myapp .` |
| コンテナの起動 | `docker run -p 8000:8000 --name mycontainer myapp` |
| コンテナの中に入る | `docker exec -it mycontainer bash` |
| コンテナの停止 | `docker stop mycontainer` |
| コンテナの削除 | `docker rm mycontainer` |
| Compose で起動 | `docker compose up --build` |
| web コンテナに入る | `docker compose exec web bash` |
| db コンテナに入る | `docker compose exec db bash` |
| Compose で停止・削除 | `docker compose down` |
