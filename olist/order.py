import pandas as pd
import numpy as np
from olist.utils import haversine_distance
from olist.data import Olist

class Order:
    """
    DataFrames containing all orders as index, and various properties of these orders as columns
    """

    def __init__(self):
        # Assign an attribute ".data" to all new instances of Order
        self.data = Olist().get_data()

    def get_wait_time(self, is_delivered=True):
        """
        Returns a DataFrame with:
        [order_id, wait_time, expected_wait_time, delay_vs_expected, order_status]
        and filters out non-delivered orders unless specified
        """
        df = self.data['orders'].copy()

        if is_delivered:
            df = df[df['order_status'] == 'delivered']

        # Convert dates to datetime
        df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
        df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])
        df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'])

        # Compute wait_time and expected_wait_time
        df['wait_time'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days
        df['expected_wait_time'] = (df['order_estimated_delivery_date'] - df['order_purchase_timestamp']).dt.days

        # Compute delay_vs_expected, set negative delays to 0
        df['delay_vs_expected'] = np.where(
            df['wait_time'] - df['expected_wait_time'] > 0,
            df['wait_time'] - df['expected_wait_time'],
            0
        )

        return df[['order_id', 'wait_time', 'expected_wait_time', 'delay_vs_expected', 'order_status']]


    def get_review_score(self):
        """
        Returns a DataFrame with:
        order_id, dim_is_five_star, dim_is_one_star, review_score
        """
        df = self.data['order_reviews'].copy()
        df['dim_is_five_star'] = (df['review_score'] == 5).astype(int)
        df['dim_is_one_star'] = (df['review_score'] == 1).astype(int)
        return df[['order_id', 'dim_is_five_star', 'dim_is_one_star', 'review_score']]

    def get_number_items(self):
        """
        Returns a DataFrame with:
        order_id, number_of_items
        """
        df = self.data['order_items'].groupby('order_id').size().reset_index(name='number_of_items')
        return df

    def get_number_sellers(self):
        """
        Returns a DataFrame with:
        order_id, number_of_sellers
        """
        df = self.data['order_items'].groupby('order_id')['seller_id'].nunique().reset_index()
        df.rename(columns={'seller_id': 'number_of_sellers'}, inplace=True)
        return df

    def get_price_and_freight(self):
        """
        Returns a DataFrame with:
        order_id, price, freight_value
        """
        df = self.data['order_items'].groupby('order_id')[['price', 'freight_value']].sum().reset_index()
        return df

    def get_distance_seller_customer(self):
        """
        Returns a DataFrame with:
        order_id, distance_seller_customer
        Safe for large datasets without crashing the kernel
        """
        # اجلب order_items
        order_items = self.data['order_items'][['order_id', 'seller_id']].drop_duplicates()
        
        # دمج مع orders لجلب customer_id
        orders = self.data['orders'][['order_id', 'customer_id']].copy()
        df = order_items.merge(orders, on='order_id', how='left')
        
        # دمج مع sellers
        sellers = self.data['sellers'][['seller_id', 'seller_city', 'seller_state']].copy()
        df = df.merge(sellers, on='seller_id', how='left')
        
        # دمج مع customers
        customers = self.data['customers'][['customer_id', 'customer_city', 'customer_state']].copy()
        df = df.merge(customers, on='customer_id', how='left')
        
        # مسافة تقريبية إذا كانت نفس الولاية أو لا
        df['distance_seller_customer'] = np.where(
            df['seller_state'] == df['customer_state'], 50, 500
        )
        return df[['order_id', 'distance_seller_customer']]

    def get_training_data(self, is_delivered=True, with_distance_seller_customer=False):
        """
        Returns a clean DataFrame (without NaN), with the all following columns:
        ['order_id', 'wait_time', 'expected_wait_time', 'delay_vs_expected', 'order_status',
        'dim_is_five_star', 'dim_is_one_star', 'review_score', 'number_of_items',
        'number_of_sellers', 'price', 'freight_value', 'distance_seller_customer']
        """
        df = self.get_wait_time(is_delivered)
        df = df.merge(self.get_review_score(), on='order_id', how='left')
        df = df.merge(self.get_number_items(), on='order_id', how='left')
        df = df.merge(self.get_number_sellers(), on='order_id', how='left')
        df = df.merge(self.get_price_and_freight(), on='order_id', how='left')

        if with_distance_seller_customer:
            df = df.merge(self.get_distance_seller_customer(), on='order_id', how='left')

        return df.dropna()
