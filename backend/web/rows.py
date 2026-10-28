def as_dicts(cursor, rows):
	names = [column[0] for column in cursor.description]
	return [dict(zip(names, row)) for row in rows]
