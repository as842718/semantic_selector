# -*- coding: utf-8 -*-
import os
import mysql.connector
import time
import numpy as np
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine


class Inputs(declarative_base()):
    __tablename__ = 'inputs'

    id = Column(Integer, primary_key=True)
    url = Column(String)
    html = Column(String)
    parent_html = Column(String)
    topic = Column(String)

    def __repr__(self):
        return "<Input(url='%s', html='%s', topic='%s')" % (
                self.url, self.html, self.topic)


class InputTags(object):
    class __InputTags:
        def __init__(self, exclude_threshold):
            self.engine = create_engine(
                    'mysql+mysqlconnector://root:@localhost/register_form',
                    echo=False)
            self.Session = sessionmaker(bind=self.engine)
            self.session = self.Session()
            self.exclude_threshold = exclude_threshold

        def fetch_data(self, ratio_test_data, seed):
            all_data = []
            sql = '''
            select * from inputs
                     where topic IN
                     (select topic from inputs
                                   group by topic
                                   having count(1) > :threshold)
                     order by id
'''
            vals = {'threshold': self.exclude_threshold}
            for r in self.session.execute(sql, vals):
                all_data.append(r)
            n = len(all_data)
            if os.getenv('N_TEST_DATA'):
                perm = [int(x) for x in os.getenv('N_TEST_DATA').split(',')]
            else:
                np.random.seed(seed)
                perm = np.random.permutation(n)[0:int(n * ratio_test_data)]
            test_data = [all_data[i] for i in perm]
            training_data = [all_data[i] for i in range(0, n) if i not in perm]
            return (training_data, test_data)

    instance = None

    def __init__(self, exclude_threshold=10):
        if not InputTags.instance:
            InputTags.instance = InputTags.__InputTags(exclude_threshold)

    def __getattr__(self, name):
        return getattr(self.instance, name)


if __name__ == "__main__":
    print("datasource")
