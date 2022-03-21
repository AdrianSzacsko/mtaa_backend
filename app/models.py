from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP, VARCHAR, TEXT

# from .database import Base


class User():
    __tablename__ = "user_table"

    # no documentation on whether nullable is False on default
    id = Column(Integer, primary_key=True, nullable=False)

    email = Column(VARCHAR(30), unique=True, nullable=False)
    first_name = Column(VARCHAR(20), nullable=False)
    last_name = Column(VARCHAR(20), nullable=False)
    pwd = Column(VARCHAR(30), nullable=False)
    permission = Column(Boolean, nullable=False)  # TODO admin permission, could be Enum
    comments = Column(Integer, nullable=False, default=0)
    reg_date = Column(TIMESTAMP(timezone=False), nullable=False)
    study_year = Column(Integer, nullable=False)
    photo = bytearray  # TODO bytearray Column value


class Professor():
    __tablename__ = "professor_table"

    id = Column(Integer, primary_key=True, nullable=False)

    first_name = Column(VARCHAR(30), nullable=False)
    last_name = Column(VARCHAR(30), nullable=False)

    # TODO FOREIGN KEY FOR SUBJECT????


class Subject():
    __tablename__ = "subject_table"

    id = Column(Integer, primary_key=True, nullable=False)

    name = Column(VARCHAR(50), nullable=False, unique=True)
    code = Column(VARCHAR(10), nullable=False, unique=True)

    prof_id = Column(Integer, ForeignKey("professor_table.id", ondelete="CASCADE"), nullable=False,)


class Relation():
    __tablename__ = "relation_table"

    subj_id = Column(Integer, ForeignKey("subject_table.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    prof_id = Column(Integer, ForeignKey("professor_table.id", ondelete="CASCADE"), primary_key=True, nullable=False)


class SubjectReview():
    __tablename__ = "subj_review_table"

    subj_id = Column(Integer, ForeignKey("subject_table.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"), primary_key=True, nullable=False)

    message = Column(TEXT, nullable=False)
    review_date = Column(TIMESTAMP(timezone=False), nullable=False, default=TEXT("now()"))
    difficulty = Column(Integer, nullable=False)
    usability = Column(Integer, nullable=False)
    prof_avg = Column(Integer, nullable=False)


class ProfessorReview():
    __tablename__ = "prof_review_table"

    prof_id = Column(Integer, ForeignKey("professor_table.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"), primary_key=True, nullable=False)

    message = Column(TEXT, nullable=False)
    review_date = Column(TIMESTAMP(timezone=False), nullable=False, default=TEXT("now()"))
    rating = Column(Integer, nullable=False)

