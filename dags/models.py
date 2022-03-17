"""Dummy data model definition."""

from sqlalchemy import Column, Integer, String, Date, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class FlightAvgDelay(Base):
    """Flight average delay data model"""

    TABLE_NAME = "flight_avg_delay"
    # orm metadata
    __tablename__ = TABLE_NAME

    # aep_code, flight_date, avg_delay
    id = Column(Integer, primary_key=True)
    aep_code = Column(String)
    flight_date = Column(Date)
    avg_delay = Column(Float)
    flight_day_nbr = Column(Integer)
    nbr_flights = Column(Integer)
    anomaly = Column(Boolean)

    def __repr__(self):
        res = (
            f"<FlightAvgDelay(aep_code={self.aep_code}, "
            f"flight_date={self.flight_date}, "
            f"avg_delay='{self.avg_delay}, "
            f"nbr_flights='{self.nbr_flights}, "
            f"anomaly='{self.anomaly}, "
            f"flight_day_nbr={self.flight_day_nbr})>"
        )
        return res
