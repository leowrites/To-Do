from numpy.testing._private.utils import break_cycles
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import numpy as np
import calendar

engine = create_engine('sqlite:///todo.db?check_same_thread=False')

Base = declarative_base()


class Table(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String)
    deadline = Column(Date, default=datetime.today())


# create table in databse
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

msg = """
1) Today's tasks
2) Week's tasks
3) All tasks
4) Miised tasks
5) Add task
6) Delete task
0) Exit
"""

def print_task_format_one(rows):
    # format is index. task day month
    for i in range(len(rows)):
        row = rows[i]
        print(
            f'{i+1}. {row.task} {row.deadline.day} {row.deadline.strftime("%b")}')


def menu(u_in):
    today = datetime.today().date()
    if u_in == 1:
        # return today's tasks
        rows = session.query(Table).filter(Table.deadline == today).all()
        print(f'Today {today.day} {today.strftime("%b")}:')
        if rows:
            for i in range(len(rows)):
                print(f'{i+1}. {rows[i].task}')
        else:
            print('Nothing to do!')

    elif u_in == 2:
        # week's tasks'
        # ignore tasks in the past
        for day in range(7):
            target_day = today + timedelta(days=day)
            rows = session.query(Table).filter(
                Table.deadline == target_day).all()
            print(
                f'\n{calendar.day_name[target_day.weekday()]} {target_day.strftime("%b")} {target_day.day}:')
            if rows:
                for i in range(len(rows)):
                    print(f'{i+1}. {rows[i].task}')
            else:
                print('Nothing to do!')

    elif u_in == 3:
        # return all tassks sorted by deadline
        rows = session.query(Table).order_by(Table.deadline).all()
        print_task_format_one(rows)
    
    elif u_in == 4:
        # shows missed tasks
        rows = session.query(Table).filter(Table.deadline < today).all()
        print('Missed tasks: ')
        if rows:
            print_task_format_one(rows)
        else:
            print('Nothing is missed!')

    elif u_in == 5:
        # add to db given task and date in format yyyy-mm-dd
        u_task = input('Enter task: ')
        u_deadline = datetime.strptime(
            input('Enter deadline:'), '%Y-%m-%d').date()
        if u_deadline:
            row = Table(task=u_task, deadline=u_deadline)
        else:
            row = Table(task=u_task)
        session.add(row)
        session.commit()

    elif u_in == 6:
        rows = session.query(Table).order_by(Table.deadline).all()
        if rows:
            print('Choose the number of task you want to delete:')
            print_task_format_one(rows)
            session.delete(rows[int(input())-1])
            session.commit()
            print('The task has been deleted!')
        else:
            print('Nothing to delete')

    else:
        return 0


while True:
    print(msg)
    try:
        out = menu(int(input('> ')))
        if out == 0:
            break
    except ValueError:
        pass
