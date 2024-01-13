#!/usr/bin/env python3

import sqlite3
import random
import timerit
import functools

from pathlib import Path
from contextlib import contextmanager
from itertools import repeat
from tqdm import tqdm, trange
from rich import print

@contextmanager
def load_db(key, make_db):
    db_path = Path(f'time_sqlite_{key}.db')
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row

    print(f"[bold]Using {key} database:[/bold]")
    print()

    if db_path.stat().st_size == 0:
        df = get_origins_df()
        print(f"Making the {key} database...")
        make_db(db, df)
        print()

    print(f"Database path: {db_path}")
    print(f"Database size: {db_path.stat().st_size / 1e9} GB")
    print()

    yield db

    print()

def make_naive_db(db, df):
    df.to_sql('origins', db, index_label='id')

def make_tag_index_db(db, df):
    make_naive_db(db, df)
    db.execute('CREATE INDEX ix_origins_tag ON origins(tag)')

def make_tag_fk_db(db, df):
    df['tag_id'] = df['tag'].values.codes

    tags = df[['tag_id', 'tag']]\
            .rename(columns={'tag_id': 'id'})\
            .drop_duplicates()\
            .sort_values('id')\
            .set_index('id')

    tags.to_sql('tags', db)

    origins = df[['x', 'y', 'z', 'tag_id']]
    origins.to_sql('origins', db, index_label='id')

    db.execute('CREATE INDEX ix_origins_tag_id ON origins(tag_id)')

def make_int_pk_db(db, df):
    df['id'] = range(df.shape[0])
    df['tag_id'] = df['tag'].values.codes

    tags = df[['tag_id', 'tag']]\
            .rename(columns={'tag_id': 'id'})\
            .drop_duplicates()\
            .sort_values('id')

    # Do everything with raw SQL to make sure the tables are created exactly 
    # how I want them to be.
    db.executescript('''\
            CREATE TABLE origins (tag_id, x, y, z);
            CREATE TABLE tags (id INTEGER PRIMARY KEY, tag);
    ''')

    def make_insert_query(table, cols, num_rows):
        cols_sql = ', '.join(cols)
        row_placeholders = '(' + ', '.join(repeat('?', len(cols))) + ')'
        placeholders = ', '.join(row_placeholders for _ in range(num_rows))
        return f'INSERT INTO {table} ({cols_sql}) VALUES {placeholders}'

    def insert(db, df, table, cols):
        # I experimented with inserted up to 10K rows per query, put this 
        # `executemany` approach still performed better.
        query = make_insert_query(table, cols, 1)
        rows = df[cols].itertuples(index=False, name=None)
        db.executemany(query, rows)

    insert(db, df, 'origins', ['tag_id', 'x', 'y', 'z'])
    insert(db, tags, 'tags', ['id', 'tag'])

    db.execute('CREATE INDEX ix_origins_tag_id ON origins(tag_id)')
    db.commit()

@functools.cache
def get_origins_df():
    print("Loading the origins data frame...")
    from atompaint.transform_pred.datasets.neighbor_count import load_origins
    return load_origins(Path('origins'))

# Randomly select a row from the database to query.
# >>> n = db.execute('SELECT MAX(id) FROM origins;').fetchone()[0]
# >>> i = random.randint(n)
# >>> tag = db.execute('SELECT tag FROM origins WHERE id=?', (i,)).fetchone()[0]
i = 5568537
tag = 'pisces/3KSNA'

with load_db('naive', make_naive_db) as db:

    for _ in timerit(label="'select by id'"):
        db.execute('SELECT * FROM origins WHERE id=?', (i,)).fetchone()

    for _ in timerit(label="'select by tag'"):
        db.execute('SELECT * FROM origins WHERE tag=?', (tag,)).fetchall()

with load_db('tag_index', make_tag_index_db) as db:

    for _ in timerit(label="'select by id'"):
        db.execute('SELECT * FROM origins WHERE id=?', (i,)).fetchone()

    for _ in timerit(label="'select by tag'"):
        db.execute('SELECT * FROM origins WHERE tag=?', (tag,)).fetchall()

with load_db('tag_fk', make_tag_fk_db) as db:

    for _ in timerit(label="'select origin by id'"):
        row = db.execute('SELECT * FROM origins WHERE id=?', (i,)).fetchone()

    for _ in timerit(label="'select tag by id'"):
        db.execute('SELECT tag FROM tags WHERE id=?', (row['tag_id'],)).fetchone()

    for _ in timerit(label="'select origins by tag_id'"):
        db.execute('SELECT * FROM origins WHERE tag_id=?', (row['tag_id'],)).fetchall()

with load_db('int_pk', make_int_pk_db) as db:

    for _ in timerit(label="'select origin by rowid'"):
        row = db.execute('SELECT * FROM origins WHERE rowid=?', (i,)).fetchone()

    for _ in timerit(label="'select tag by id'"):
        db.execute('SELECT tag FROM tags WHERE id=?', (row['tag_id'],)).fetchone()

    for _ in timerit(label="'select origins by tag_id'"):
        db.execute('SELECT * FROM origins WHERE tag_id=?', (row['tag_id'],)).fetchall()

    cur = db.cursor()

    for _ in timerit(label="'select origin by rowid'"):
        row = cur.execute('SELECT * FROM origins WHERE rowid=?', (i,)).fetchone()

    for _ in timerit(label="'select tag by id'"):
        cur.execute('SELECT tag FROM tags WHERE id=?', (row['tag_id'],)).fetchone()

    for _ in timerit(label="'select origins by tag_id'"):
        cur.execute('SELECT * FROM origins WHERE tag_id=?', (row['tag_id'],)).fetchall()

