import yaml
from importlib import import_module

from dsbox.operators.data_executor import DataExecutor


class Dataoperations():
    """
    Load data operations meta-data.

    Ex:

    Join_train_data_source_files:
      operation_function:
        module: tree_disease.ml.feature_engineering
        name: join_dataframes
      input_unit:
        type: DataInputMultiFileUnit
        input_path_list:
          - '{}/X_tree_egc_t1.csv'
          - '{}/X_geoloc_egc_t1.csv'
          - '{}/Y_tree_egc_t1.csv'
        pandas_read_function_name: read_csv
        sep: ';'
      output_unit:
        type: DataOutputFileUnit
        output_path: '{}/X_train_raw.parquet'
        pandas_write_function_name: to_parquet

    """

    def __init__(self, input_path=None, output_path=None, data_unit_module='dsbox_lite.operators.data_unit'):
        self.input_path = input_path
        self.output_path = output_path
        self.parsed_datasets_file = None
        self.data_unit_module = data_unit_module

    def load_datasets(self, datasets_file_path):
        datasets_file = open(datasets_file_path)
        self.parsed_datasets_file = yaml.load(datasets_file, Loader=yaml.FullLoader)

    def run(self, operation_name):
        operation_structure = self.parsed_datasets_file[operation_name]

        operation_infos = operation_structure['operation_function']
        operation = getattr(import_module(operation_infos['module']), operation_infos['name'])
        op_kwargs = dict()
        if 'kwargs' in operation_infos:
            op_kwargs = operation_infos['kwargs']

        input_unit = None
        output_unit = None

        if 'input_unit' in operation_structure:
            input_unit_structure = operation_structure['input_unit']
            DataInputUnitClass = getattr(import_module(self.data_unit_module), input_unit_structure['type'])
            parameters = input_unit_structure.copy()
            parameters.pop('type')
            if 'input_path' in parameters:
                parameters['input_path'] = parameters['input_path'].format(self.input_path)
            if 'input_path_list' in parameters:
                parameters['input_path_list'] = [path.format(self.input_path) for path in parameters['input_path_list']]
            input_unit = DataInputUnitClass(**parameters)

        if 'output_unit' in operation_structure:
            output_unit_structure = operation_structure['output_unit']
            DataOutputUnitClass = getattr(import_module(self.data_unit_module), output_unit_structure['type'])
            parameters = output_unit_structure.copy()
            parameters.pop('type')
            parameters['output_path'] = parameters['output_path'].format(self.output_path)
            output_unit = DataOutputUnitClass(**parameters)

        task = DataExecutor(operation, input_unit=input_unit, output_unit=output_unit, **op_kwargs)
        task.execute()