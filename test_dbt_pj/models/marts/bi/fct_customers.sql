-- models/marts/bi/fct_customers.sql

-- 【4層目：Marts (BI用)】 顧客軸の最終集計テーブル
with customers as (
    -- 【2層目：Staging】 顧客の基本属性
    select * from {{ ref('stg_customers') }}
),

orders as (
    -- 【3層目：Intermediate】 顧客ごとの注文サマリー
    select * from {{ ref('int_customer_orders') }}
),

payments as (
    -- 【3層目：Intermediate】 注文ごとの支払い集計を、顧客ごとに再集計
    select
        ord.customer_id,
        sum(pay.total_amount) as lifetime_value -- 累計売上（LTV）
    from {{ ref('stg_orders') }} as ord
    left join {{ ref('int_payments_pivoted') }} as pay on ord.order_id = pay.order_id
    group by 1
),

final as (
    -- 全ての部品を顧客IDでJOINし、BIで使いやすい1枚の表にする
    select
        customers.customer_id,
        customers.first_name,
        customers.last_name,
        orders.first_order_date,
        orders.most_recent_order_date,
        coalesce(orders.number_of_orders, 0) as number_of_orders,
        coalesce(payments.lifetime_value, 0) as lifetime_value
    from customers
    left join orders on customers.customer_id = orders.customer_id
    left join payments on customers.customer_id = payments.customer_id
)

select * from final