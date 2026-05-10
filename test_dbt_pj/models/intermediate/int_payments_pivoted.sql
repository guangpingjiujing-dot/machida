-- models/intermediate/int_payments_pivoted.sql

-- 【3層目：Intermediate】 注文ごとの支払い合計金額を計算する中間モデル
with payments as (
    -- 【2層目：Staging】 決済データ（お化粧直し済み）を参照
    select * from {{ ref('stg_payments') }}
),

pivoted as (
    -- 注文(order_id)ごとに、成功した決済金額を合計する
    select
        order_id,
        sum(case when status = 'success' then amount else 0 end) as total_amount
    from payments
    group by 1
)

-- 4層目（Marts）でJOINするための集計結果を出力
select * from pivoted