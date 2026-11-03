BASE_PATH = "/Volumes/workspace/bronze/store_sources"

INGESTION_CONFIG= [
        {
            "path" : f"{BASE_PATH}/Product.csv",
            "table" :  "product"
        }
        ,
        {
            "path" : f"{BASE_PATH}/daily_foot_traffic.csv",
            "table":  "daily_foot_trafic"
        }
        ,
        {
            "path" : f"{BASE_PATH}/inventory_snapshot.csv",
            "table":  "inventory_snapshot"
        }
        ,
        {
            "path" : f"{BASE_PATH}/promo_calander.csv",
            "table":  "promo_calander"
        }
        ,
        {
            "path" : f"{BASE_PATH}/store.csv",
            "table":  "store"
        }
        ,
        {
            "path" : f"{BASE_PATH}/transtractions.csv",
            "table":  "transtractions"
        }
]