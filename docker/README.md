# Docker・Docker Compose 入門

## コンテナとは

コンテナとは、アプリケーションとその実行に必要なもの（コード・ライブラリ・設定など）を一つにまとめた**軽量な実行環境**のこと。

一番の強みは**「どこで動かしても同じ環境になる」**こと。  
「自分のPCでは動くのに本番サーバーで動かない」という問題がなくなる。

### 仮想マシン（VM）との違い

| | VM | コンテナ |
|---|---|---|
| 起動時間 | 数分 | 数秒 |
| サイズ | 数GB〜数十GB | 数MB〜数百MB |
| 仕組み | OSごと仮想化 | OSのカーネルを共有 |
| 用途 | 完全な別PC環境が必要なとき | アプリを隔離して動かしたいとき |

---

## Docker とは

Docker は**コンテナを作って動かすためのソフトウェア（ツール）**。

コンテナという概念そのものは Docker より前からあるが、Docker が登場したことで誰でも簡単にコンテナを扱えるようになった。

主にやれること：
- イメージのビルド（`docker build`）
- コンテナの起動・停止（`docker run` / `docker stop`）
- コンテナ内への接続（`docker exec`）
- イメージの配布（`docker push` / `docker pull`）

---

## イメージ（Image）とは

コンテナを作るための**設計図・テンプレート**。

- イメージからコンテナを何個でも作れる
- コンテナは起動するたびにイメージをもとに作られる

```
イメージ（設計図）
    │
    ├──▶ コンテナA（起動中）
    ├──▶ コンテナB（停止中）
    └──▶ コンテナC（起動中）
```

イメージは**レイヤー構造**になっており、変更差分だけを積み重ねて管理している。  
このためキャッシュが効き、ビルドが速くなる。

---

## Dockerfile とは

イメージを作るための**手順書（設定ファイル）**。

「どのOSをベースにするか」「どんなファイルを入れるか」「起動時に何を実行するか」を記述する。

```dockerfile
# ベースとなるイメージを指定
FROM python:3.12-slim

# コンテナ内の作業ディレクトリを設定
WORKDIR /app

# ホストのファイルをコンテナ内にコピー
COPY app.py .

# コンテナ起動時に実行するコマンド
CMD ["python", "app.py"]
```

### 主な命令

| 命令 | 意味 |
|---|---|
| `FROM` | ベースとなるイメージを指定（必ず最初に書く） |
| `WORKDIR` | コンテナ内の作業ディレクトリを設定 |
| `COPY` | ホストのファイル/ディレクトリをコンテナ内にコピー |
| `RUN` | イメージビルド時にコマンドを実行（パッケージのインストールなど） |
| `CMD` | コンテナ起動時のデフォルトコマンド（`docker run` の末尾に引数を渡すと上書きされる） |
| `ENTRYPOINT` | 必ず実行されるコマンド（`docker run` の末尾の引数は上書きではなく追記になる） |
| `ENV` | 環境変数を設定 |

### CMD と ENTRYPOINT の違い

`CMD` はデフォルト値であり、`docker run` 実行時に末尾へ引数を渡すと丸ごと上書きされる。

```bash
# Dockerfile に CMD ["python", "app.py"] と書いてある場合
docker run myapp bash   # bash が CMD を上書きし、bash が起動する
```

`ENTRYPOINT` は固定のコマンドとして扱われ、`docker run` の末尾の引数は ENTRYPOINT に対する追加引数として渡される。

```bash
# Dockerfile に ENTRYPOINT ["python"] と書いてある場合
docker run myapp app.py   # python app.py として実行される
docker run myapp --version  # python --version として実行される
```

実用上は、**コンテナが「一つの決まったコマンドを実行する道具」として設計されているなら `ENTRYPOINT`、汎用的に使うなら `CMD`** という使い分けが多い。両方書くこともでき、その場合は `ENTRYPOINT` がコマンド、`CMD` がそのデフォルト引数になる。

---

## Docker Hub とは

Docker の**イメージ共有サービス（レジストリ）**。GitHub の Docker 版のようなもの。

- `python:3.12-slim` や `nginx` など、公式イメージが公開されている
- 自分で作ったイメージをアップロード（push）して共有できる
- `docker pull <イメージ名>` でダウンロードできる

Dockerfile の `FROM` に書くイメージ名は、基本的に Docker Hub から取得される。

```
Docker Hub の URL: https://hub.docker.com
```

---

## Docker Compose とは

**複数のコンテナをまとめて管理するツール**。

例えば「Webアプリ」と「データベース」のように、複数のコンテナを連携させたい場合に便利。

`docker-compose.yml` というファイルにすべての設定を書いておけば、コマンド一発で起動・停止できる。

```yaml
services:
  web:           # サービス名（自由につけられる）
    build: .     # このディレクトリのDockerfileを使ってビルド
    ports:
      - "8000:8000"  # ホスト:コンテナ のポートマッピング
```

### よく使うコマンド

| コマンド | 意味 |
|---|---|
| `docker compose up` | すべてのサービスを起動 |
| `docker compose up -d` | バックグラウンドで起動 |
| `docker compose down` | すべてのサービスを停止・削除 |
| `docker compose logs` | ログを確認 |
| `docker compose ps` | 起動中のサービスを確認 |

---

## よく使う Docker コマンド

```bash
# イメージのビルド
docker build -t myapp .

# コンテナの起動
docker run -p 8000:8000 myapp

# 起動中のコンテナ一覧
docker ps

# 全コンテナ一覧（停止中も含む）
docker ps -a

# コンテナの中に入る
docker exec -it <コンテナID or 名前> bash

# コンテナの停止
docker stop <コンテナID or 名前>

# コンテナの削除
docker rm <コンテナID or 名前>

# イメージ一覧
docker images

# イメージの削除
docker rmi <イメージID or 名前>
```
