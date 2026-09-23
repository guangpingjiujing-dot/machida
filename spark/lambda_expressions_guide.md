# RDD でよく使う Lambda 式ガイド

## Lambda 式とは

Lambda 式（ラムダ式）は、Python で無名関数を定義するための構文です。RDD の操作では、map、filter、reduce などの関数に渡す処理を簡潔に書くために頻繁に使用されます。

### 基本的な構文

```python
lambda 引数: 処理内容
```

通常の関数定義と比較すると：

```python
# 通常の関数定義
def double(x):
    return x * 2

# Lambda 式で同じことを書く
lambda x: x * 2
```

## RDD での Lambda 式の使い方

### 1. map での使用

`map` は各要素に関数を適用して変換します。

#### 基本的な例

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("LambdaGuide").master("local[*]").getOrCreate()
sc = spark.sparkContext

# 各要素を2倍にする
rdd = sc.parallelize([1, 2, 3, 4, 5])
doubled = rdd.map(lambda x: x * 2)
print(doubled.collect())  # [2, 4, 6, 8, 10]
```

#### 文字列の操作

```python
# 各文字列を大文字に変換
words = sc.parallelize(["hello", "world", "spark"])
uppercase = words.map(lambda x: x.upper())
print(uppercase.collect())  # ['HELLO', 'WORLD', 'SPARK']

# 各文字列の長さを取得
lengths = words.map(lambda x: len(x))
print(lengths.collect())  # [5, 5, 5]
```

#### 複雑な変換

```python
# 各数値の2乗を計算
numbers = sc.parallelize([1, 2, 3, 4, 5])
squared = numbers.map(lambda x: x ** 2)
print(squared.collect())  # [1, 4, 9, 16, 25]

# タプルの要素を操作
data = sc.parallelize([("Alice", 25), ("Bob", 30)])
ages_only = data.map(lambda x: x[1])  # タプルの2番目の要素を取得
print(ages_only.collect())  # [25, 30]
```

### 2. filter での使用

`filter` は条件に合う要素だけを残します。Lambda 式は **True または False を返す**必要があります。

#### 基本的な例

```python
# 偶数だけを残す
numbers = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
evens = numbers.filter(lambda x: x % 2 == 0)
print(evens.collect())  # [2, 4, 6, 8, 10]

# 5より大きい数だけを残す
greater_than_5 = numbers.filter(lambda x: x > 5)
print(greater_than_5.collect())  # [6, 7, 8, 9, 10]
```

#### 文字列のフィルタリング

```python
# 長さが5以上の文字列だけを残す
words = sc.parallelize(["hello", "hi", "world", "spark", "py"])
long_words = words.filter(lambda x: len(x) >= 5)
print(long_words.collect())  # ['hello', 'world', 'spark']

# 特定の文字を含む文字列だけを残す
contains_o = words.filter(lambda x: 'o' in x)
print(contains_o.collect())  # ['hello', 'world']
```

#### タプルのフィルタリング

```python
# 年齢が25以上の人のみを残す
people = sc.parallelize([("Alice", 25), ("Bob", 30), ("Charlie", 20)])
adults = people.filter(lambda x: x[1] >= 25)
print(adults.collect())  # [('Alice', 25), ('Bob', 30)]
```

### 3. reduce での使用

`reduce` は要素を順番に結合して1つの値にします。Lambda 式は **2つの引数を受け取り、1つの値を返す**必要があります。

#### reduce の動作の仕組み

`reduce` は以下のように動作します：

1. **最初の2つの要素**を取り出して、Lambda 式に渡します
2. Lambda 式の結果と**次の要素**を取り出して、再度 Lambda 式に渡します
3. これを**すべての要素がなくなるまで**繰り返します

具体例で見てみましょう：

```python
numbers = sc.parallelize([1, 2, 3, 4, 5])
total = numbers.reduce(lambda x, y: x + y)
```

この場合、`x` と `y` には以下のように値が代入されていきます：

**ステップ1**: 最初の2つの要素 `1` と `2` を取る
- `x = 1`（最初の要素）
- `y = 2`（2番目の要素）
- 結果: `1 + 2 = 3`

**ステップ2**: 前の結果 `3` と次の要素 `3` を取る
- `x = 3`（前のステップの結果）
- `y = 3`（3番目の要素）
- 結果: `3 + 3 = 6`

**ステップ3**: 前の結果 `6` と次の要素 `4` を取る
- `x = 6`（前のステップの結果）
- `y = 4`（4番目の要素）
- 結果: `6 + 4 = 10`

**ステップ4**: 前の結果 `10` と次の要素 `5` を取る
- `x = 10`（前のステップの結果）
- `y = 5`（5番目の要素）
- 結果: `10 + 5 = 15`

**最終結果**: `15`

つまり、`x` には「これまでの累積結果」、`y` には「次の要素」が代入されていきます。

#### 基本的な例

```python
# すべての要素の合計を計算
numbers = sc.parallelize([1, 2, 3, 4, 5])
total = numbers.reduce(lambda x, y: x + y)
print(total)  # 15
# 動作: 1+2=3 → 3+3=6 → 6+4=10 → 10+5=15

# すべての要素の積を計算
product = numbers.reduce(lambda x, y: x * y)
print(product)  # 120
# 動作: 1*2=2 → 2*3=6 → 6*4=24 → 24*5=120

# 最大値を取得
maximum = numbers.reduce(lambda x, y: x if x > y else y)
print(maximum)  # 5
# 動作: max(1,2)=2 → max(2,3)=3 → max(3,4)=4 → max(4,5)=5

# 最小値を取得
minimum = numbers.reduce(lambda x, y: x if x < y else y)
print(minimum)  # 1
# 動作: min(1,2)=1 → min(1,3)=1 → min(1,4)=1 → min(1,5)=1
```

#### filter と reduce の違い

`filter` と `reduce` の違いを理解すると、Lambda 式の使い方がより明確になります：

**filter の場合**:
- `x` には**各要素が1つずつ**代入される
- Lambda 式は各要素に対して**独立して**実行される
- 結果は複数の要素を持つ RDD になる

```python
# filter の例
numbers = sc.parallelize([1, 2, 3, 4, 5])
evens = numbers.filter(lambda x: x % 2 == 0)
# x には順番に 1, 2, 3, 4, 5 が代入される
# 各要素に対して独立して条件判定が行われる
# 結果: [2, 4]
```

**reduce の場合**:
- `x` には**これまでの累積結果**が代入される
- `y` には**次の要素**が代入される
- Lambda 式は**前の結果を使いながら**実行される
- 結果は1つの値になる

```python
# reduce の例
numbers = sc.parallelize([1, 2, 3, 4, 5])
total = numbers.reduce(lambda x, y: x + y)
# ステップ1: x=1, y=2 → 結果=3
# ステップ2: x=3, y=3 → 結果=6
# ステップ3: x=6, y=4 → 結果=10
# ステップ4: x=10, y=5 → 結果=15
# 最終結果: 15
```

#### 文字列の結合

```python
# 文字列を結合
words = sc.parallelize(["Hello", " ", "World", "!"])
sentence = words.reduce(lambda x, y: x + y)
print(sentence)  # "Hello World!"
```

### 4. flatMap での使用

`flatMap` は各要素を複数の要素に展開します。Lambda 式は **リストやイテラブルを返す**必要があります。

#### 基本的な例

```python
# 各文字列を文字のリストに展開
words = sc.parallelize(["hello", "world"])
chars = words.flatMap(lambda x: list(x))
print(chars.collect())  # ['h', 'e', 'l', 'l', 'o', 'w', 'o', 'r', 'l', 'd']

# 各数値とその2倍を返す
numbers = sc.parallelize([1, 2, 3])
doubled = numbers.flatMap(lambda x: [x, x * 2])
print(doubled.collect())  # [1, 2, 2, 4, 3, 6]

# 文章を単語に分割
sentences = sc.parallelize(["Hello world", "Spark is great"])
words = sentences.flatMap(lambda x: x.split())
print(words.collect())  # ['Hello', 'world', 'Spark', 'is', 'great']
```

### 5. キー・値ペアの操作

キー・値ペアの RDD では、タプル `(key, value)` を操作します。

#### mapValues

```python
# 値だけを変換（キーはそのまま）
data = sc.parallelize([("apple", 3), ("banana", 2), ("orange", 5)])
doubled_values = data.mapValues(lambda x: x * 2)
print(doubled_values.collect())  # [('apple', 6), ('banana', 4), ('orange', 10)]
```

#### reduceByKey

`reduceByKey` は、**同じキーを持つ要素の値だけを結合**します。`reduce` と似ていますが、キーごとに独立して処理されます。

```python
# 同じキーの値を合計
data = sc.parallelize([("apple", 3), ("banana", 2), ("apple", 5)])
total = data.reduceByKey(lambda x, y: x + y)
print(total.collect())  # [('apple', 8), ('banana', 2)]
```

**動作の仕組み**:

`reduceByKey` では、`x` と `y` には**値（value）だけ**が代入されます（キーは除く）。

元のデータ: `[("apple", 3), ("banana", 2), ("apple", 5)]`

**キー "apple" の処理**:
- ステップ1: `x = 3`（最初の "apple" の値）、`y = 5`（2番目の "apple" の値）
- 結果: `3 + 5 = 8`
- 最終結果: `("apple", 8)`

**キー "banana" の処理**:
- "banana" は1つしかないので、そのまま残る
- 最終結果: `("banana", 2)`

つまり、`reduceByKey` では：
- `x` には「同じキーの値の累積結果」が代入される
- `y` には「同じキーの次の値」が代入される
- **キーごとに独立して** `reduce` が実行される

**もう1つの例**:

```python
data = sc.parallelize([("apple", 1), ("banana", 2), ("apple", 3), ("banana", 4), ("apple", 5)])
total = data.reduceByKey(lambda x, y: x + y)
print(total.collect())  # [('apple', 9), ('banana', 6)]
```

**キー "apple" の処理**:
- ステップ1: `x = 1`, `y = 3` → `1 + 3 = 4`
- ステップ2: `x = 4`, `y = 5` → `4 + 5 = 9`
- 最終結果: `("apple", 9)`

**キー "banana" の処理**:
- ステップ1: `x = 2`, `y = 4` → `2 + 4 = 6`
- 最終結果: `("banana", 6)`

#### map（キー・値ペア全体を操作）

```python
# キーと値を入れ替える
data = sc.parallelize([("apple", 3), ("banana", 2)])
swapped = data.map(lambda x: (x[1], x[0]))
print(swapped.collect())  # [(3, 'apple'), (2, 'banana')]

# 値が5以上のものだけを残す
data = sc.parallelize([("apple", 3), ("banana", 7), ("orange", 2)])
filtered = data.filter(lambda x: x[1] >= 5)
print(filtered.collect())  # [('banana', 7)]
```

## よくあるパターン

### パターン1: 複数の操作をチェーン

```python
numbers = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

# 偶数だけを選んで2倍にする
result = numbers.filter(lambda x: x % 2 == 0).map(lambda x: x * 2)
print(result.collect())  # [4, 8, 12, 16, 20]
```

### パターン2: 条件分岐を含む処理

```python
# 5より大きい場合は2倍、それ以外はそのまま
numbers = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
result = numbers.map(lambda x: x * 2 if x > 5 else x)
print(result.collect())  # [1, 2, 3, 4, 5, 12, 14, 16, 18, 20]
```

### パターン3: 複数の要素を持つタプルの操作

```python
# (名前, 年齢, 部署) のタプルから年齢だけを取得
people = sc.parallelize([
    ("Alice", 25, "Engineering"),
    ("Bob", 30, "Marketing"),
    ("Charlie", 35, "Engineering")
])
ages = people.map(lambda x: x[1])
print(ages.collect())  # [25, 30, 35]

# 年齢が30以上の人の名前だけを取得
names = people.filter(lambda x: x[1] >= 30).map(lambda x: x[0])
print(names.collect())  # ['Bob', 'Charlie']
```

## Lambda 式の制限と注意点

### 1. 複雑な処理は通常の関数を使う

Lambda 式は1行で書ける簡単な処理に適しています。複雑な処理の場合は、通常の関数を定義した方が読みやすくなります。

```python
# ❌ 読みにくい（Lambda 式が複雑）
result = rdd.map(lambda x: x * 2 if x > 5 else x * 3 if x > 3 else x)

# ✅ 読みやすい（通常の関数を使用）
def transform(x):
    if x > 5:
        return x * 2
    elif x > 3:
        return x * 3
    else:
        return x

result = rdd.map(transform)
```

### 2. 変数のキャプチャに注意

Lambda 式は外部の変数を参照できますが、注意が必要です。

```python
# これは動作します
multiplier = 2
result = rdd.map(lambda x: x * multiplier)

# しかし、ループ内で変数を使う場合は注意が必要
# （詳細は高度なトピックなので、ここでは省略）
```

### 3. デバッグが難しい

Lambda 式は名前がないため、エラーが発生したときにデバッグが難しい場合があります。複雑な処理の場合は、通常の関数を使うことをおすすめします。

## 練習問題

以下の問題を解いて、Lambda 式の使い方を練習してみましょう。

### 問題1: 数値のリストから、5より大きい数の2乗を計算してください

```python
numbers = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
# ここにコードを書いてください
# 期待される結果: [36, 49, 64, 81, 100]
```

### 問題2: 文字列のリストから、長さが5以上の文字列を大文字に変換してください

```python
words = sc.parallelize(["hello", "hi", "world", "spark", "py"])
# ここにコードを書いてください
# 期待される結果: ['HELLO', 'WORLD', 'SPARK']
```

### 問題3: キー・値ペアの RDD から、値が10以上のものだけを残し、値を2倍にしてください

```python
data = sc.parallelize([("apple", 5), ("banana", 15), ("orange", 8), ("grape", 20)])
# ここにコードを書いてください
# 期待される結果: [('banana', 30), ('grape', 40)]
```

## まとめ

- Lambda 式は無名関数を簡潔に書くための構文
- RDD の `map`、`filter`、`reduce`、`flatMap` などで頻繁に使用される
- 簡単な処理には Lambda 式、複雑な処理には通常の関数を使う
- 読みやすさとデバッグのしやすさを考慮して使い分ける

## 参考

- [Python Lambda 式の公式ドキュメント](https://docs.python.org/ja/3/tutorial/controlflow.html#lambda-expressions)
- `rdd_examples.py` - RDD のサンプルコードも参照してください
