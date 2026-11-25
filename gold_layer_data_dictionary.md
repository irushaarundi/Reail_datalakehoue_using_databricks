# Gold Layer Data Dictionary

This document describes the Gold layer of the Retail Data Lakehouse (`workspace.gold` schema in the `workspace` catalog). The Gold layer models the cleaned Silver data into an analytics-ready star schema with 4 dimension tables and 3 fact tables. All tables are managed Delta tables built by the notebooks in `Scripts/gold/`.

## Overview

| Table | Type | Purpose |
| --- | --- | --- |
| dim_date | Dimension | Store the calendar dimension with date attributes (day, week, month, quarter, year, weekend flag) used to slice facts by time. |
| dim_product | Dimension | Store product details (name, category, cost price, planned unit price) for analyzing sales by product and category. |
| dim_store | Dimension | Store store details enriched with demographic and geographic data (region, city, size, manager, open/close dates, lat/long). |
| dim_promo_calander | Dimension | Store promotional campaign details (discount, valid date range, store, category) for measuring promotion effectiveness. |
| fact_tanstractions | Fact | Store sales transactions enriched with store, product, date, and promo surrogate keys along with quantity, price, discount, and revenue. |
| fact_inventory_snapshot | Fact | Store periodic stock levels per store and product, enabling inventory and out-of-stock analysis. |
| fact_daily_foot_traffic | Fact | Store daily visitor counts per store, enabling traffic trend analysis and the link between promotions and footfall. |

> Note: the table names `fact_tanstractions` and `dim_promo_calander` carry misspellings inherited from the raw source data naming.

## dim_date

Purpose: Store the calendar dimension with date attributes (day, week, month, quarter, year, weekend flag) used to slice facts by time. Built by `Scripts/gold/gold_dim_date` from the date range spanned by `silver.transtractions`.

| Column | Data Type | Description |
| --- | --- | --- |
| date_key | INT | Surrogate key - row number over dates, primary key. |
| full_day | DATE | The calendar date. |
| day | INT | Day of month (1-31). |
| day_name | STRING | Weekday name (Monday...Sunday). |
| week | INT | ISO week of year. |
| month | INT | Month number (1-12). |
| month_name | STRING | Month name (January...December). |
| quarter | INT | Quarter (1-4). |
| year | INT | Year. |
| is_weekend | INT | 1 if Saturday/Sunday, else 0. |

## dim_product

Purpose: Store product details (name, category, cost price, planned unit price) for analyzing sales by product and category. Built by `Scripts/gold/gold_dim_product` from `silver.product`.

| Column | Data Type | Description |
| --- | --- | --- |
| product_key | INT | Surrogate key, primary key. |
| product_id | STRING | Business product ID. |
| product_name | STRING | Product name. |
| category | STRING | Product category. |
| cost_price | INT | Unit cost. |
| plan_unit_price | INT | Planned/list unit price. |

## dim_store

Purpose: Store store details enriched with demographic and geographic data (region, city, size, manager, open/close dates, lat/long). Built by `Scripts/gold/gold_dim_store` from `silver.store`.

| Column | Data Type | Description |
| --- | --- | --- |
| store_key | INT | Surrogate key, primary key. |
| store_id | STRING | Business store ID. |
| store_name | STRING | Store name (title-cased and standardized in Silver). |
| region | STRING | Sales region. |
| city | STRING | City. |
| store_sqft | INT | Store size in square feet. |
| store_manager | STRING | Manager name. |
| store_open_date | DATE | Store opening date. |
| store_close_date | DATE | Store closing date (null if still open). |
| latitude | DOUBLE | Geographic latitude. |
| longitude | DOUBLE | Geographic longitude. |
| store_availability | STRING | Availability status. |

## dim_promo_calander

Purpose: Store promotional campaign details (discount, valid date range, store, category) for measuring promotion effectiveness. Built by `Scripts/gold/gold_dim_promo` from `silver.promo_calander`.

| Column | Data Type | Description |
| --- | --- | --- |
| promo_key | INT | Surrogate key, primary key. |
| promo_id | STRING | Business promo ID. |
| promo_name | STRING | Promotion name. |
| category | STRING | Category the promo applies to. |
| discount_pct | DOUBLE | Discount fraction (e.g. 0.15 = 15%). |
| start_date | DATE | Promo start date. |
| end_date | DATE | Promo end date. |
| store_id | STRING | Store the promo applies to. |

## fact_tanstractions

Purpose: Store sales transactions enriched with store, product, date, and promo surrogate keys along with quantity, price, discount, and revenue. Built by `Scripts/gold/gold_fact_transtraction` by joining `silver.transtractions` to all four dimensions; one row per transaction.

| Column | Data Type | Description |
| --- | --- | --- |
| transaction_id | INT | Transaction ID, primary key of the grain. |
| date_key | INT | Foreign key to dim_date.date_key. |
| promo_key | INT | Foreign key to dim_promo_calander.promo_key (null if no promo matched). |
| order_date | DATE | Transaction date. |
| store_key | INT | Foreign key to dim_store.store_key. |
| store_id | STRING | Natural key kept for traceability. |
| store_name | STRING | Store name. |
| region | STRING | Store region. |
| product_key | INT | Foreign key to dim_product.product_key. |
| product_id | STRING | Natural key kept for traceability. |
| product_name | STRING | Product name. |
| category | STRING | Product category. |
| quantity | INT | Units sold. |
| applied_unit_price | INT | Unit price after Silver outlier correction (3x median rule). |
| applied_discount | DOUBLE | Discount applied to this transaction (fraction, null = none). |
| customer_id | STRING | Customer identifier. |
| loyalty_member | STRING | yes/no (mapped from 0/1 in Silver). |
| revenue | DOUBLE | Computed as quantity x price x (1 - discount), rounded to 2 decimals. |

## fact_inventory_snapshot

Purpose: Store periodic stock levels per store and product, enabling inventory and out-of-stock analysis. Built by `Scripts/gold/gold_fact_inventory_snapshot` from `silver.inventory_snapshot`; one row per store-product-snapshot-date.

| Column | Data Type | Description |
| --- | --- | --- |
| store_key | INT | Foreign key to dim_store.store_key. |
| store_id | STRING | Natural key kept for traceability. |
| product_key | INT | Foreign key to dim_product.product_key. |
| product_id | STRING | Natural key kept for traceability. |
| date_key | INT | Foreign key to dim_date.date_key. |
| snapshot_date | DATE | Date of the inventory snapshot. |
| units_on_hand | INT | Stock units on hand at snapshot. |

## fact_daily_foot_traffic

Purpose: Store daily visitor counts per store, enabling traffic trend analysis and the link between promotions and footfall. Built by `Scripts/gold/gold_fact_daily_foot_traffic` from `silver.daily_foot_trafic`; one row per store per day.

| Column | Data Type | Description |
| --- | --- | --- |
| store_key | INT | Foreign key to dim_store.store_key. |
| store_id | STRING | Natural key kept for traceability. |
| date_key | INT | Foreign key to dim_date.date_key. |
| date | DATE | Foot-traffic date. |
| promo_key | INT | Foreign key to dim_promo_calander.promo_key. |
| foot_traffic | INT | Visitor count for the day. |

## Star schema relationships

- fact_tanstractions.date_key -> dim_date.date_key
- fact_tanstractions.store_key -> dim_store.store_key
- fact_tanstractions.product_key -> dim_product.product_key
- fact_tanstractions.promo_key -> dim_promo_calander.promo_key (matched on order_date within promo start/end dates, store_id, and category)
- fact_inventory_snapshot joins dim_date, dim_store, and dim_product on date_key, store_key, and product_key
- fact_daily_foot_traffic joins dim_date, dim_store, and dim_promo_calander on date_key, store_key, and promo_key
