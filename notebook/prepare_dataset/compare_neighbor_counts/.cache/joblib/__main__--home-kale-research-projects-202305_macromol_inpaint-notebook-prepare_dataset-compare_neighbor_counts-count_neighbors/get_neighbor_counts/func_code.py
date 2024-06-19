# first line: 8
@cache
def get_neighbor_counts():
    db = open_db('mmt_pdb.sqlite')
    cur = db.execute('SELECT zone_id, neighbor_id FROM zone_neighbor')
    rows = cur.fetchall()
    return pl.DataFrame(rows, ['zone_id', 'neighbor_id'], orient='row')
