import mysql.connector

class Database():
    """
    __init__(config) -> None
        config: dic

    constructor for the database
    uses args given in config to initialize the db
    returns nnothing
    """
    def __init__(self, config) -> None:
        self.conn = mysql.connector.connect(
            user=config["DB_USER"],
            host=config['DB_HOST'],
            password=config["DB_PASSWORD"],
            database=config["DB_NAME"],
            port=config["DB_PORT"]
        )

    """
    query(query, one) -> Any
        query: str
        one: bool = False

    executes the query given by parameter through a cursor
    if one == True, returns only one value; else, returns all
    returns query results
    """
    def query(self, query: str, one: bool = False):
        cursor = self.conn.cursor(dictionary=True, buffered=True)
        cursor.execute(query)
        data = cursor.fetchone() if one else cursor.fetchall()
        # print(data)
        cursor.close()
        return data

    """
    command(cmd) -> None
        cmd: str

    executes the command given by parameter through a cursor
    returns nothing
    """
    def command(self, cmd: str):
        cursor = self.conn.cursor()
        cursor.execute(cmd)
        cursor.close()
        self.conn.commit()