from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Rider(Base):
    __tablename__ = "riders"

    id = Column(String, primary_key=True, index=True) # rider_id e.g. "sikorov_l"
    name = Column(String, nullable=False)

    # Ratings
    rating_road = Column(Float, default=1000.0)
    rating_gravel = Column(Float, default=1000.0)
    rating_mtb = Column(Float, default=1000.0)

    # Race counts for weighted average
    races_road = Column(Integer, default=0)
    races_gravel = Column(Integer, default=0)
    races_mtb = Column(Integer, default=0)

    last_trend = Column(Float, default=0.0)

    results = relationship("Result", back_populates="rider")

    @property
    def races_count(self):
        return self.races_road + self.races_gravel + self.races_mtb


class Race(Base):
    __tablename__ = "races"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    category = Column(String, nullable=False) # 'road', 'gravel', 'mtb'
    k_factor = Column(Float, default=1.0)

    results = relationship("Result", back_populates="race")


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("races.id"))
    rider_id = Column(String, ForeignKey("riders.id"))
    time_sec = Column(Float, nullable=False) # can be null if DNF/DSQ? Requirement says exclude DNF/DSQ. So if they are in DB they might be null or have a status string. Let's add status.
    status = Column(String, default="FIN") # "FIN", "DNF", "DSQ"

    race = relationship("Race", back_populates="results")
    rider = relationship("Rider", back_populates="results")
