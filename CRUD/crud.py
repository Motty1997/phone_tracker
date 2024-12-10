from db.database import driver


def single_query(query: str, params: dict={}):
    with driver.session()as session:
        return session.run(query=query, parameters=params).single()


def data_query(query: str, params: dict={}):
    with driver.session()as session:
        return session.run(query=query, parameters=params).data()
