class Olist:
    def get_data(self):
        import os
        import pandas as pd

        # بناء المسار المطلق لمجلد csv
        base_path = os.path.dirname(__file__)
        csv_path = os.path.join(base_path, 'data', 'csv')

        # قائمة أسماء الملفات
        file_names = [f for f in os.listdir(csv_path) if f.endswith('.csv')]

        # تحويل أسماء الملفات لمفاتيح dictionary
        key_names = [f.replace('olist_', '').replace('_dataset.csv', '').replace('.csv','') for f in file_names]

        # قراءة CSVs وبناء dictionary
        data = {}
        for key, file in zip(key_names, file_names):
            data[key] = pd.read_csv(os.path.join(csv_path, file))

        return data

    def ping(self):
        print("pong")

