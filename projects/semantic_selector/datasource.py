# -*- coding: utf-8 -*-
import os
import csv
import mysql.connector
import time
import numpy as np
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine, func
from sqlalchemy.ext.hybrid import hybrid_property


def read_canonical_topics():
    canonical_topic_table = {}
    file_path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(file_path, '../docs/canonicalTopics.csv')) \
            as csv_file:
        reader = csv.reader(csv_file, delimiter=",")
        for row in reader:
            if row[0] in canonical_topic_table:
                print(row[0])
            canonical_topic_table[row[0]] = row[1]
    return canonical_topic_table


class Input(declarative_base()):
    canonical_table = read_canonical_topics()
    __tablename__ = 'inputs'

    id = Column(Integer, primary_key=True)
    url = Column(String)
    html = Column(String)
    parent_html = Column(String)
    topic = Column(String)

    @hybrid_property
    def canonical_topic(self):
        if self.topic in Input.canonical_table:
            return self.canonical_table[self.topic]
        else:
            return 'unknown'

    def __repr__(self): return "<Input(url='%s', html='%s', topic='%s')" % (
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
            sub = self.session.query(Input.topic) \
                      .group_by(Input.topic) \
                      .having(func.count(1) > self.exclude_threshold)
            query = self.session.query(Input) \
                        .filter(Input.topic.in_(sub))
            for r in query.all():
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
