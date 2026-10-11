# WSL / Ubuntu の使い方と Spark 実行環境の準備

Windows で Linux 環境を使うための WSL と Ubuntu の基本操作、および Spark を実行するための Java・Python の準備をまとめます。

Spark の学習手順は [README.md](README.md) を参照してください。

## 1. WSL と Ubuntu を開く

Windows Terminal またはスタートメニューから **Ubuntu** を開きます。PowerShell から起動する場合は、次のコマンドを使います。

```powershell
# インストール済みの WSL ディストリビューションを確認する
wsl -l -v

# 既定の Ubuntu を起動する
wsl
```

初回起動時には、Ubuntu 用のユーザー名とパスワードを設定します。これは Windows のアカウントとは別です。

- Ubuntu 用のユーザー名: `sparkuser`
- パスワード: このファイルや Git には記録しない

## 2. Ubuntu の基本操作

Ubuntu のターミナルでは、次の操作をよく使います。

```bash
# 現在いるフォルダを表示する
pwd

# ファイル・フォルダを一覧表示する
ls -la

# 1 つ上のフォルダへ移動する
cd ..

# 自分のホームフォルダへ移動する
cd ~

# フォルダを作成する
mkdir -p ~/workspace

# Ubuntu ターミナルを終了する
exit
```

### Windows のファイルを WSL から開く

Windows の `C:\test_github\machida` は、WSL では `/mnt/c/test_github/machida` として見えます。

```bash
# Windows の C: ドライブにあるプロジェクトへ移動する
cd /mnt/c/test_github/machida

# 現在のフォルダを VS Code で開く（VS Code と WSL 拡張機能がある場合）
code .
```

> 小さな学習用ファイルは `/mnt/c/...` でも問題ありません。大きなデータを扱う場合は、速度と Linux のファイル権限の扱いやすさのため、`~/workspace` のような WSL 側のフォルダで作業することをおすすめします。

## 3. VS Code を WSL / Ubuntu に接続する

Spark ハンズオンでは、VS Code の編集画面とターミナルも Ubuntu 側へ接続して使います。これにより、VS Code から実行する Python が WSL 側の Java・PySpark・DuckDB を使います。

1. VS Code の拡張機能で、Microsoft 提供の **WSL** 拡張機能をインストールする。
2. Ubuntu ターミナルで、ハンズオンのフォルダへ移動して `code .` を実行する。

```bash
# ハンズオンのフォルダを WSL 接続の VS Code で開く
cd /mnt/c/test_github/machida/spark_duckdb_handson
code .
```

新しく開いた VS Code の左上と左下に、`spark_duckdb_handson [WSL: Ubuntu]`、`WSL: Ubuntu` と表示されれば成功です。初回に「制限モード」と表示された場合は、自分のフォルダであることを確認してから信頼します。

仮想環境を作成する前でも VS Code は開けます。**この資料の「6. ハンズオン用の Python 環境を作る」を完了した後**に、VS Code の「ターミナル」→「新しいターミナル」を開き、仮想環境を有効化します。

```bash
# WSL 側の Spark 用仮想環境を有効化する
source ~/venvs/spark-duckdb-handson/bin/activate

# WSL 側の Python が使われていることを確認する
which python
```

ターミナルは次のように表示されます。

```text
(spark-duckdb-handson) sparkuser@DESKTOP-...:/mnt/c/test_github/machida/spark_duckdb_handson$
/home/sparkuser/venvs/spark-duckdb-handson/bin/python
```

`(.venv) PS C:\...` と表示される場合は Windows の PowerShell です。このハンズオンの Spark 実行には使用せず、`WSL: Ubuntu` のウィンドウへ戻ります。

> VS Code が WSL に接続していても、プロジェクトの実体は Windows 側の `C:\test_github\...` のままです。Ubuntu からは `/mnt/c/...` として同じコードと入力データを読んでいます。Spark の Parquet 出力は、Linux の権限設定を行える Ubuntu 側の `~/workspace/spark_duckdb_output/` に保存します。

## 4. Spark 実行に必要なソフトウェアを入れる

Spark は Java 上で動き、ハンズオンでは Python から Spark を操作します。Ubuntu のターミナルで次を実行してください。

```bash
# パッケージ一覧を更新する
sudo apt update

# Java 21、Python 仮想環境、pip をインストールする
sudo apt install -y openjdk-21-jdk python3-venv python3-pip

# Java が使えることを確認する（21 系と表示されれば OK）
java -version

# Python が使えることを確認する
python3 --version
```

## 5. Java の確認

今回の Ubuntu 環境では、`java -version` が表示される状態で PySpark を起動できました。通常は `JAVA_HOME` を設定しなくても問題ありません。

```bash
# Java が利用できることを確認する
java -version
```

`JAVA_GATEWAY_EXITED` など、Spark が Java を見つけられないエラーが出た場合だけ、次のコマンドで Java の場所を自動検出して設定します。

```bash
# 現在使用している Java の実体から JAVA_HOME を自動設定する
export JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")"

# 設定された Java の場所を確認する
echo "$JAVA_HOME"
```

## 6. ハンズオン用の Python 環境を作る

Python の仮想環境を作ると、Spark 関連のパッケージをこのハンズオン用に分けて管理できます。

```bash
# ハンズオンのフォルダへ移動する
cd /mnt/c/test_github/machida/spark_duckdb_handson

# WSL 側に仮想環境を置くフォルダを作る（初回のみ）
mkdir -p ~/venvs

# WSL 側に、このハンズオン専用の仮想環境を作る（初回のみ）
python3 -m venv ~/venvs/spark-duckdb-handson

# 仮想環境を有効化する（新しい Ubuntu ターミナルを開くたびに実行する）
source ~/venvs/spark-duckdb-handson/bin/activate

# WSL 側の Python が選ばれていることを確認する
which python

# pip 自体を更新する
python -m pip install --upgrade pip

# Spark と、Parquet を確認するための DuckDB をインストールする
python -m pip install pyspark duckdb
```

仮想環境が有効な間は、ターミナル行頭に `(spark-duckdb-handson)` と表示されます。`which python` は `/home/sparkuser/venvs/spark-duckdb-handson/bin/python` を表示します。作業を終えたら、次のコマンドで抜けます。

```bash
# Python 仮想環境を終了する
deactivate
```

### Spark の起動確認

仮想環境を有効化したまま、最初のサンプルを実行します。

```bash
# PySpark と DuckDB が読み込めることを確認する
python -c "import pyspark, duckdb; print('PySpark:', pyspark.__version__); print('DuckDB:', duckdb.__version__)"

# Spark を起動して DataFrame を表示する
python 01_hello_spark.py
```

`Spark version: 4.2.0` と `Alice`、`Bob`、`Carol` の表が表示されれば成功です。

> WSL のローカル実行では、ホスト名が loopback を指す警告や Native Hadoop library の警告が表示されることがあります。このハンズオンでの CSV・Parquet 処理には影響しません。

### このハンズオンにおける並行実行の設定

ハンズオンの Spark スクリプトでは `local[2]` を使います。これは Ubuntu 上のこの PC 内で、最大2個の Spark タスクを同時に実行する設定です。入力をいくつのパーティション（仕事）に分けるかは別の話で、Spark の Driver が入力ファイルの状況から自動で決めます。

たとえば野球データの実行では、50個のCSVが17パーティションに分かれました。この場合も17個を同時実行するのではなく、`local[2]` により最大2個ずつ順番に実行されます。詳細は [README.md](README.md) の「分散処理はどのように動いたか」を参照してください。

## よくあるエラー

### `JAVA_GATEWAY_EXITED` または `Java gateway process exited`

Java が未インストール、または `JAVA_HOME` が正しくない可能性があります。

```bash
# Java のバージョンを確認する
java -version

# Java の場所を確認する
echo "$JAVA_HOME"

# 現在使用している Java の実体から JAVA_HOME を自動設定する
export JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")"
echo "$JAVA_HOME"
```

### `ensurepip` が失敗して仮想環境を作れない

Windows 側のフォルダ（`/mnt/c/...`）に `python3 -m venv venv` を実行すると、`ensurepip` が失敗する場合があります。仮想環境は WSL 側のホームディレクトリに作成してください。

```bash
# WSL 側に仮想環境を作成する
mkdir -p ~/venvs
python3 -m venv ~/venvs/spark-duckdb-handson

# 作成した WSL 側の仮想環境を有効化する
source ~/venvs/spark-duckdb-handson/bin/activate
```

### `ModuleNotFoundError: No module named 'pyspark'`

仮想環境を有効化していないか、その環境に PySpark を入れていない状態です。

```bash
# WSL 側の仮想環境を有効化する
source ~/venvs/spark-duckdb-handson/bin/activate

# 有効化した環境に PySpark をインストールする
python -m pip install pyspark
```

準備ができたら、[README.md](README.md) に戻って Spark ハンズオンを始めてください。
