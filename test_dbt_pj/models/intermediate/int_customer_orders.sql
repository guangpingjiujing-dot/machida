-- models/intermediate/int_customer_orders.sql

-- 【3層目：Intermediate】 顧客ごとの注文サマリーを計算する中間モデル
with customers as (
    -- 【2層目：Staging】 顧客データ（お化粧直し済み）を参照
    select * from {{ ref('stg_customers') }}
),

orders as (
    -- 【2層目：Staging】 注文データ（お化粧直し済み）を参照
    select * from {{ ref('stg_orders') }}
),

customer_orders as (
    -- 顧客ごとの計算ロジックを集約（BIツールでの重複計算を防ぐ）
    select
        customer_id,
        min(order_date) as first_order_date,        -- 最初の注文日
        max(order_date) as most_recent_order_date,  -- 最新の注文日
        count(order_id) as number_of_orders        -- 累計注文回数
    from orders
    group by 1
)

-- 4層目（Marts）でJOINするための計算結果を出力
select * from customer_orders