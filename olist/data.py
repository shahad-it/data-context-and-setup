import os
import pandas as pd

class Olist:
    def get_data(self):
        """
        Returns a dictionary with all Olist datasets as pandas DataFrames.
        Keys: 'sellers', 'orders', 'order_items', etc.
        """
        # تحديد المسار الأساسي لمجلد olist
        base_path = os.path.dirname(__file__)  # هذا يعطيك مسار .../olist
        # المسار الصحيح لملفات CSV
        csv_path = os.path.abspath(os.path.join(base_path, '..', 'data', 'csv'))

        # الحصول على أسماء جميع ملفات CSV
        file_names = [f for f in os.listdir(csv_path) if f.endswith('.csv')]

        # تحويل أسماء الملفات لمفاتيح dictionary
        key_names = [
            f.replace('olist_', '').replace('_dataset.csv', '').replace('.csv', '') 
            for f in file_names
        ]

        # قراءة كل ملف CSV وتحويله لـ DataFrame
        data = {}
        for key, file in zip(key_names, file_names):
            data[key] = pd.read_csv(os.path.join(csv_path, file))

        return data

    def ping(self):
        """Simple test function."""
        print("pong")


