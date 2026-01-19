from sqlalchemy import Column, Integer, String, Time, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    day = Column(String, nullable=False)  # Monday, Tuesday, etc.
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    location = Column(String)
    instructor = Column(String)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "day": self.day,
            "start_time": str(self.start_time),
            "end_time": str(self.end_time),
            "location": self.location,
            "instructor": self.instructor,
        }