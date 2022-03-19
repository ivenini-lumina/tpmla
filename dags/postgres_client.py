"""Postgres client module"""
from models import Base, FlightAvgDelay
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

CONNECTION_ID = "flightsdb-conn"


class PostgresClient:
    """Postgres client class to access the database"""

    def __get_db_engine(self):
        engine = None
        print("Creating DB connection with the following data")
        hook = PostgresHook(postgres_conn_id=CONNECTION_ID, echo=True)
        print(hook)
        print("DB Engine data information")
        engine = hook.get_sqlalchemy_engine()
        print(engine)
        return engine

    def create_tables(self):
        """Create all tables in DB for all model mapped classes in the ORM system"""
        print("Creating DB tables")
        # Logic to create tables goes here.
        # https://docs.sqlalchemy.org/en/14/orm/tutorial.html#create-a-schema
        engine = self.__get_db_engine()
        Base.metadata.create_all(engine)

    def bulk_save(self, flight_avg_delay_list):
        """bulk save for FlightAvgDelay list"""
        print(f"Saving list {flight_avg_delay_list}")
        print("Create DB engine")
        engine = self.__get_db_engine()
        print("Create DB session")
        session = Session(engine)
        print(f"Deleting {FlightAvgDelay.TABLE_NAME} table")
        del_query = session.query(FlightAvgDelay)
        del_query.delete()
        print(f"Adding list with {len(flight_avg_delay_list)} elements")
        session.add_all(flight_avg_delay_list)
        session.commit()
        print("Commit complete")
        session.close()
        print("Session closed")

    def bulk_update(self, vector_input, vector_prediction, from_date, to_date):
        """Update table FlightAvgDelay with anomaly data"""

        sql_upd_0 = (
            f"update {FlightAvgDelay.TABLE_NAME} set anomaly = false "
            f"where flight_date between :dfrom and :dto "
        )
        txt_upd_0 = text(sql_upd_0)

        sql_upd_1 = (
            f"update {FlightAvgDelay.TABLE_NAME} set anomaly = true where id = :p_id "
        )
        txt_upd_1 = text(sql_upd_1)

        print("Create DB engine")
        engine = self.__get_db_engine()
        print("Create DB connection")
        with engine.connect() as conn:
            print(f"Execute sql {sql_upd_0}")
            print(f"SQL params: from={from_date} | to={to_date}")
            result_0 = conn.execute(txt_upd_0, dfrom=from_date, dto=to_date)
            print(f"Result: {result_0}")
            print(f"Result Type: {type(result_0)}")

            anomaly_count = 0

            for idx, vec in enumerate(vector_input):
                v_id = vec[2]
                v_anomaly = False
                if vector_prediction[idx] == -1:
                    v_anomaly = True

                if v_anomaly:
                    # result_1 = conn.execute(txt_upd_1, p_id=v_id)
                    conn.execute(txt_upd_1, p_id=v_id)
                    anomaly_count = anomaly_count + 1

            print(f"Anomaly count updated in DB: {anomaly_count}")

            # conn.execute("commit")
            # print("Commit complete")

        return result_0

    def get_avg_delay_for_aep(self, from_date, to_date):
        """get FlightAvgDelay data for date range and aep code"""

        sql = (
            f"select id, flight_date, avg_delay "
            f"from {FlightAvgDelay.TABLE_NAME} "
            f"where flight_date between :dfrom and :dto"
        )
        txt = text(sql)

        print("Create DB engine")
        engine = self.__get_db_engine()
        print("Create DB connection")
        conn = engine.connect()
        print(f"Execute sql {sql}")
        print(f"SQL params: from={from_date} | to={to_date}")
        result = conn.execute(txt, dfrom=from_date, dto=to_date).fetchall()
        # print(f"Result: {result}")
        print(f"Result Type: {type(result)}")
        return result
