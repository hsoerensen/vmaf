__copyright__ = "Copyright 2016, Netflix, Inc."
__license__ = "Apache, Version 2.0"

import os

import config
from core.result import Result
from tools.misc import make_parent_dirs_if_nonexist


class ResultStore(object):
    """
    Provide capability to save and load a Result.
    """
    pass


class SqliteResultStore(ResultStore):
    """
    persist result by a SQLite engine that save/load result.
    """
    pass


class FileSystemResultStore(ResultStore):
    """
    persist result by a simple file system that save/load result in a directory.
    The directory has multiple subdirectories, each corresponding to an Executor
    (e.g. a VMAF feature extractor, or a NO19 feature extractor, or a
    VMAF quality runner, or a SSIM quality runner). Each subdirectory contains
    multiple files, each file stores dataframe for an asset, and has file name
    str(asset).
    """
    def __init__(self,
                 logger=None,
                 result_store_dir=config.ROOT +
                                "/workspace/result_store_dir/file_result_store"
                 ):
        self.logger = logger
        self.result_store_dir = result_store_dir

    def save(self, result):
        result_file_path = self._get_result_file_path(result)
        make_parent_dirs_if_nonexist(result_file_path)
        with open(result_file_path, "wt") as result_file:
            result_file.write(str(result.to_dataframe().to_dict()))

    def load(self, asset, executor_id):
        import pandas as pd
        import ast
        result_file_path = self._get_result_file_path2(asset, executor_id)

        if not os.path.isfile(result_file_path):
            return None

        with open(result_file_path, "rt") as result_file:
            df = pd.DataFrame.from_dict(ast.literal_eval(result_file.read()))
            result = Result.from_dataframe(df)
        return result

    def delete(self, asset, executor_id):
        result_file_path = self._get_result_file_path2(asset, executor_id)
        if os.path.isfile(result_file_path):
            os.remove(result_file_path)

    def clean_up(self):
        """
        WARNING: RMOVE ENTIRE RESULT STORE, USE WITH CAUTION!!!
        :return:
        """
        import shutil
        if os.path.isdir(self.result_store_dir):
            shutil.rmtree(self.result_store_dir)

    def _get_result_file_path(self, result):
        return "{dir}/{executor_id}/{str}".format(dir=self.result_store_dir,
                                                  executor_id=result.executor_id,
                                                  str=str(result.asset))

    def _get_result_file_path2(self, asset, executor_id):
        return "{dir}/{executor_id}/{str}".format(dir=self.result_store_dir,
                                                  executor_id=executor_id,
                                                  str=str(asset))