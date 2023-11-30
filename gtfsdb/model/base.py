import os
import time
import pandas as pd
from sqlalchemy.ext.declarative import declarative_base


class _Base(object):
    @classmethod
    def load_table(cls, extract_dir, sess, alias):
        file_path = os.path.join(extract_dir, cls.filename)
        if not os.path.exists(file_path):
            return

        start_time = time.time()

        df = pd.read_csv(file_path, dtype = 'object')

        batch_size = 10000
        i = 0
        records = []
        for _, row_series in df.iterrows():
            i += 1

            record = cls.make_record(row_series, alias)
            records.append(record)

            if i >= batch_size:
                sess.bulk_save_objects(records, return_defaults=True)

                print("inserted %s records" % len(records))
                i = 0
                records = []

        if len(records) > 0:
            sess.bulk_save_objects(records, return_defaults=True)
            print("inserted %s records" % len(records))

        process_time = time.time() - start_time
        print("Loaded %s in %s seconds" % (cls.__tablename__, process_time))

    @classmethod
    def validate_table(cls, extract_dir, alias):
        file_path = os.path.join(extract_dir, cls.filename)
        if not os.path.exists(file_path):
            return

        start_time = time.time()

        df = pd.read_csv(file_path, dtype = 'object')

        for _, row_series in df.iterrows():
            valid, reason = cls.validate_record(row_series, alias)
            if not valid:
                print("validation error: %s" % reason)
                print("row series", row_series)
                raise Exception(reason)

        process_time = time.time() - start_time
        print("Validated %s in %s seconds" % (cls.__tablename__, process_time))

    @classmethod
    def validate_record(row_series, alias):
        raise("should implement")

    @classmethod
    def make_record(row_series, alias):
        raise("should implement")

Base = declarative_base(cls=_Base)
