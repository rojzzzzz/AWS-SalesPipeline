from aws import s3
import time
import logging

def ingestion():
    csv_data = """order_id,customer_id,product,quantity,amount,date
    ORD001,CUST42,Premium T-Shirt,2,51.98,2024-01-15
    ORD002,CUST17,Running Shoes,1,89.99,2024-01-15
    ORD003,CUST42,Slim Fit Pants,1,49.99,2024-01-15
    ORD004,CUST08,Winter Jacket,1,129.99,2024-01-15
    ORD005,CUST23,Cotton Hoodie,2,79.98,2024-01-15
    ORD006,CUST11,Leather Belt,1,24.99,2024-01-15
    ORD007,CUST35,Denim Jeans,3,149.97,2024-01-15
    ORD008,CUST17,Sports Shorts,2,39.98,2024-01-15
    ORD009,CUST09,Classic Sneakers,1,74.99,2024-01-15
    ORD010,CUST42,Polo Shirt,2,59.98,2024-01-15
    ORD011,CUST28,Winter Scarf,1,19.99,2024-01-15
    ORD012,CUST14,Leather Jacket,1,199.99,2024-01-15
    ORD013,CUST08,Casual T-Shirt,4,79.96,2024-01-15
    ORD014,CUST31,Running Shoes,2,179.98,2024-01-15
    ORD015,CUST23,Slim Fit Pants,1,49.99,2024-01-15
    ORD016,CUST05,Summer Dress,2,89.98,2024-01-15
    ORD017,CUST17,Baseball Cap,3,44.97,2024-01-15
    ORD018,CUST39,Premium T-Shirt,1,25.99,2024-01-15
    ORD019,CUST11,Denim Jacket,1,89.99,2024-01-15
    ORD020,CUST42,Cotton Hoodie,1,39.99,2024-01-15
    ORD021,CUST28,Classic Sneakers,2,149.98,2024-01-15
    ORD022,CUST09,Leather Belt,2,49.98,2024-01-15
    ORD023,CUST35,Sports Shorts,3,59.97,2024-01-15
    ORD024,CUST14,Winter Jacket,1,129.99,2024-01-15
    ORD025,CUST05,Polo Shirt,2,59.98,2024-01-15
    ORD026,CUST31,Summer Dress,1,44.99,2024-01-15
    ORD027,CUST08,Running Shoes,1,89.99,2024-01-15
    ORD028,CUST23,Denim Jeans,2,99.98,2024-01-15
    ORD029,CUST39,Winter Scarf,3,59.97,2024-01-15
    ORD030,CUST17,Leather Jacket,1,199.99,2024-01-15
"""

    s3.put_object(Bucket='fashionstore-raw', Key='orders/2024-01-15/orders_hour_14.csv', Body=csv_data.encode())
    logging.info("File uploaded to S3 raw")
