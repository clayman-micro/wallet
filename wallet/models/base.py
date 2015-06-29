import sqlalchemy

metadata = sqlalchemy.Metadata()


def create_table(name, columns):
    base_columns = [
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True)
    ]
    base_columns.extend(columns)
    return sqlalchemy.Table(name, metadata, *base_columns)