import datetime

from sqlalchemy import text

from aftafa.common.dal import (
    session as db_session,
    engine as db_engine
)


class Checker:
    def __init__(self) -> None:
        with open("scripts/mvm/checks/mail_list_check_date.sql", "r") as f:
            self.date_check_query = f.read()

        with open("scripts/mvm/checks/mail_list_check_anomaly.sql", "r") as f:
            self.anomaly_queries: list[str] = f.read().split(';')

    def check_dates(self) -> None:
        stmt = text(self.date_check_query)
        query_result = db_session.execute(stmt)
        db_session.close()
        query_result = query_result.fetchall()
        if not query_result:
            return None
        query_result = [
            {
                'missing_date': query_result_val[0].strftime('%Y-%m-%d'),
                'mv_mail_list_sale_date': (query_result_val[1].strftime('%Y-%m-%d') if isinstance(query_result_val[1], datetime.date) else query_result_val[1]),
                'mv_mail_list_stock_date': (query_result_val[2].strftime('%Y-%m-%d') if isinstance(query_result_val[2], datetime.date) else query_result_val[2]),
                'date_check': query_result_val[3]
            }
            for query_result_val in query_result
        ]

        return query_result
        

    def check_anomalies(self) -> None:
        pass






