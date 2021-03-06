import unittest
from datetime import datetime
import pandas as pd

from airflow import DAG

from dsbox.operators.data_operator import DataOperator
from dsbox.operators.data_unit import DataInputFileUnit, DataOutputFileUnit, DataOutputPlasmaUnit, DataInputPlasmaUnit
from dsbox.dbconnection.plasma_connector import PlasmaConnector
from dsbox.utils import execute_dag

from tests.config import socket_name, object_id


def drop_na_dataframe(dataframe, columns):
    dataframe = dataframe.dropna(subset=columns)
    return dataframe


class TestDagFile(unittest.TestCase):
    def test_building_two_operators_with_execution(self):
        # given
        plasma_connector = PlasmaConnector(socket_name)

        dag = DAG(dag_id='test_dag_plasma', start_date=datetime.now())

        input_csv_unit = DataInputFileUnit('data/X.csv', sep=';')
        output_plasma_unit = DataOutputPlasmaUnit(plasma_connector, object_id)
        task_1 = DataOperator(operation_function=drop_na_dataframe,
                              params={'columns': ['ANNEEREALISATIONDIAGNOSTIC']},
                              input_unit=input_csv_unit,
                              output_unit=output_plasma_unit,
                              dag=dag, task_id='data_operator_csv_to_plasma')

        input_plasma_unit = DataInputPlasmaUnit(plasma_connector, object_id)
        output_csv_unit = DataOutputFileUnit('data/X_parsed_22.csv', index=False)
        task_2 = DataOperator(operation_function=drop_na_dataframe,
                              params={'columns': ['ANNEETRAVAUXPRECONISESDIAG']},
                              input_unit=input_plasma_unit,
                              output_unit=output_csv_unit,
                              dag=dag, task_id='data_operator_plasma_to_csv')

        task_2.set_upstream(task_1)

        # when
        execute_dag(dag, verbose=True)

        # then
        df = pd.read_csv('data/X_parsed_22.csv')
        self.assertEqual((7241, 27), df.shape)


