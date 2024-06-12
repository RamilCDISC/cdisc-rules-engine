import asyncio
from abc import ABC
from functools import wraps, partial
from typing import Callable, List, Optional, Iterable, Iterator
from concurrent.futures import ThreadPoolExecutor
import os
import numpy as np
import pandas as pd

from cdisc_rules_engine.constants.domains import AP_DOMAIN_LENGTH
from cdisc_rules_engine.interfaces import (
    CacheServiceInterface,
    ConfigInterface,
    DataServiceInterface,
)
from cdisc_rules_engine.constants.classes import (
    FINDINGS,
    FINDINGS_ABOUT,
    EVENTS,
    INTERVENTIONS,
    RELATIONSHIP,
)
from cdisc_rules_engine.models.dataset_types import DatasetTypes
from cdisc_rules_engine.services import logger
from cdisc_rules_engine.services.cdisc_library_service import CDISCLibraryService
from cdisc_rules_engine.services.data_readers import DataReaderFactory
from cdisc_rules_engine.utilities.utils import (
    convert_library_class_name_to_ct_class,
    get_dataset_cache_key_from_path,
    get_directory_path,
    search_in_list_of_dicts,
)
from cdisc_rules_engine.utilities.sdtm_utilities import get_class_and_domain_metadata
from cdisc_rules_engine.models.dataset.dataset_interface import DatasetInterface
from cdisc_rules_engine.models.dataset import PandasDataset


def cached_dataset(dataset_type: str):
    """
    Decorator that can be applied to get_dataset_... functions
    to support caching service.
    Before calling the wrapped function it checks
    if needed dataset exists in cache.
    Bear in mind that wrapped functions have to be
    called with kwargs in order to support cache key template.
    """
    if not DatasetTypes.contains(dataset_type):
        raise ValueError(f"Invalid dataset type: {dataset_type}")

    def decorator(func: Callable):
        @wraps(func)
        def inner(*args, **kwargs):
            instance: BaseDataService = args[0]
            dataset_name: str = kwargs["dataset_name"]
            logger.info(
                f"Downloading dataset from storage. dataset_name={dataset_name},"
                f" wrapped function={func.__name__}"
            )
            cache_key: str = get_dataset_cache_key_from_path(dataset_name, dataset_type)
            cache_data = instance.cache_service.get_dataset(cache_key)
            if cache_data is not None:
                logger.info(
                    f'Dataset "{dataset_name}" was found in cache.'
                    f" cache_key={cache_key}"
                )
                dataset = cache_data
            else:
                dataset = func(*args, **kwargs)
                instance.cache_service.add_dataset(cache_key, dataset)
            logger.info(f"Downloaded dataset. dataset={dataset}")
            return dataset

        return inner

    return decorator


class BaseDataService(DataServiceInterface, ABC):
    """
    An abstract base class for all data services that implement
    data service interface. The class implements some methods
    whose implementation stays the same regardless of the service.
    It is not necessary to inherit from this class.
    """

    def __init__(
        self,
        cache_service: CacheServiceInterface,
        reader_factory: DataReaderFactory,
        config: ConfigInterface,
        **kwargs,
    ):
        self.cache_service = cache_service
        self._reader_factory = reader_factory
        self._config = config
        self.cdisc_library_service: CDISCLibraryService = CDISCLibraryService(
            self._config.getValue("CDISC_LIBRARY_API_KEY", ""), self.cache_service
        )
        self.standard = kwargs.get("standard")
        self.version = (kwargs.get("standard_version") or "").replace(".", "-")
        self.library_metadata = kwargs.get("library_metadata")
        self.dataset_implementation = kwargs.get(
            "dataset_implementation", PandasDataset
        )

    def get_dataset_by_type(
        self, dataset_name: str, dataset_type: str, **params
    ) -> DatasetInterface:
        """
        Generic function to return dataset based on the type.
        dataset_type param can be: contents, metadata, variables_metadata.
        """
        dataset_type_to_function_map: dict = {
            DatasetTypes.CONTENTS.value: self.get_dataset,
            DatasetTypes.METADATA.value: self.get_dataset_metadata,
            DatasetTypes.VARIABLES_METADATA.value: self.get_variables_metadata,
        }
        return dataset_type_to_function_map[dataset_type](
            dataset_name=dataset_name, **params
        )

    def concat_split_datasets(
        self, func_to_call: Callable, dataset_names: List[str], **kwargs
    ) -> DatasetInterface:
        """
        Accepts a list of split dataset filenames, asynchronously downloads
        all of them and merges into a single DataFrame.

        function_to_call must accept dataset_name and kwargs
        as input parameters and return pandas DataFrame.
        """
        # pop drop_duplicates param at the beginning to avoid passing it to func_to_call
        drop_duplicates: bool = kwargs.pop("drop_duplicates", False)

        # download datasets asynchronously
        datasets: Iterable[DatasetInterface] = self._async_get_datasets(
            func_to_call, dataset_names, **kwargs
        )
        # insert merge logic
        full_dataset = self.dataset_implementation()
        for dataset in datasets:
            full_dataset = full_dataset.concat(dataset, ignore_index=True)

        if drop_duplicates:
            full_dataset.drop_duplicates()
        return full_dataset

    def merge_split_dataset(self, full_dataset, supp_dataset):
        # static keys for merge
        static_keys = ["STUDYID", "USUBJID", "APID", "POOLID", "SPDEVID"]
        # Determine the common keys present in both datasets
        common_keys = [
            key
            for key in static_keys
            if key in full_dataset.columns and key in supp_dataset.columns
        ]
        dynamic_key = supp_dataset["IDVAR"].iloc[0]
        splitDF_filtered = supp_dataset.copy()
        unique_qnams = splitDF_filtered["QNAM"].unique()
        for qnam in unique_qnams:
            current_split = splitDF_filtered[splitDF_filtered["QNAM"] == qnam]
            if (
                "IDVARVAL" in current_split.columns
                and dynamic_key in full_dataset.columns
            ):
                common_keys.append(dynamic_key)
                current_split = current_split.rename(columns={"IDVARVAL": dynamic_key})
        full_dataset[dynamic_key] = full_dataset[dynamic_key].astype(str)
        current_split[dynamic_key] = current_split[dynamic_key].astype(str)
        merged_df = pd.merge(
            full_dataset.data,
            current_split,
            how="left",
            on=common_keys,
            suffixes=("", "_supp"),
        )
        if merged_df.duplicated(subset=common_keys).any():
            raise ValueError(
                f"Multiple records with the same QNAM '{qnam}' match a single parent record"
            )
        # TODO: Add new columns corresponding to each QNAM
        merged_df = PandasDataset(merged_df)
        return merged_df

    def get_dataset_class(
        self,
        dataset: DatasetInterface,
        file_path: str,
        datasets: List[dict],
        domain: str,
    ) -> Optional[str]:
        if self.standard is None or self.version is None:
            raise Exception("Missing standard and version data")

        standard_data = self._get_standard_data()

        class_data, _ = get_class_and_domain_metadata(standard_data, domain)
        name = class_data.get("name")
        if name:
            return convert_library_class_name_to_ct_class(name)

        return self._handle_special_cases(dataset, domain, file_path, datasets)

    def _get_standard_data(self):
        return (
            self.library_metadata.standard_metadata
            or self.cdisc_library_service.get_standard_details(
                self.standard, self.version
            )
        )

    def _handle_special_cases(self, dataset, domain, file_path, datasets):
        if self._contains_topic_variable(dataset, domain, "TERM"):
            return EVENTS
        if self._contains_topic_variable(dataset, domain, "TRT"):
            return INTERVENTIONS
        if self._contains_topic_variable(dataset, domain, "QNAM"):
            return RELATIONSHIP
        if self._contains_topic_variable(dataset, domain, "TESTCD"):
            if self._contains_topic_variable(dataset, domain, "OBJ"):
                return FINDINGS_ABOUT
            return FINDINGS
        if self._is_associated_persons(dataset, domain):
            return self._get_associated_persons_inherit_class(
                dataset, file_path, datasets, domain
            )
        return None

    def _is_associated_persons(self, dataset, domain) -> bool:
        """
        Check if AP-- domain.
        """
        return (
            "DOMAIN" in dataset
            and self._domain_starts_with(domain, "AP")
            and len(domain) == AP_DOMAIN_LENGTH
        )

    def _get_associated_persons_inherit_class(
        self, dataset, file_path, datasets: List[dict], domain: str
    ):
        """
        Check with inherit class AP-- belongs to.
        """
        ap_suffix = domain[2:]
        directory_path = get_directory_path(file_path)
        if len(datasets) > 1:
            domain_details: dict = search_in_list_of_dicts(
                datasets, lambda item: item.get("domain") == ap_suffix
            )
            if domain_details:
                file_name = domain_details["filename"]
                new_file_path = os.path.join(directory_path, file_name)
                new_domain_dataset = self.get_dataset(dataset_name=new_file_path)
            else:
                raise ValueError("Filename for domain doesn't exist")
            if self._is_associated_persons(new_domain_dataset):
                raise ValueError("Nested Associated Persons domain reference")
            return self.get_dataset_class(
                new_domain_dataset,
                new_file_path,
                datasets,
                domain_details["domain"],
            )
        else:
            return None

    def _contains_topic_variable(self, dataset, domain, variable):
        """
        Checks if the given dataset-class string ends with a particular variable string.
        Returns True/False
        """
        if "DOMAIN" not in dataset and "RDOMAIN" not in dataset:
            return False
        elif "DOMAIN" in dataset:
            return domain.upper() + variable in dataset
        elif "RDOMAIN" in dataset:
            return variable in dataset

    def _domain_starts_with(self, domain, variable):
        """
        Checks if the given dataset-class string starts with
         a particular variable string.
        Returns True/False
        """
        return domain.startswith(variable)

    @staticmethod
    def _replace_nans_in_numeric_cols_with_none(dataset: DatasetInterface):
        """
        Replaces NaN in numeric columns with None.
        """
        numeric_columns = dataset.data.select_dtypes(include=np.number).columns
        dataset[numeric_columns] = dataset.data[numeric_columns].replace(np.nan, None)

    async def _async_get_dataset(
        self, function_to_call: Callable, dataset_name: str, **kwargs
    ) -> DatasetInterface:
        """
        Asynchronously executes passed function_to_call.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, partial(function_to_call, dataset_name=dataset_name, **kwargs)
        )

    def _async_get_datasets(
        self, function_to_call: Callable, dataset_names: List[str], **kwargs
    ) -> Iterator[DatasetInterface]:
        """
        The method uses multithreading to download each
        dataset in dataset_names param in parallel.

        function_to_call param is a function that downloads
        one dataset. So, this function is asynchronously called
        for each item of dataset_names param.
        """
        with ThreadPoolExecutor() as executor:
            return executor.map(
                lambda name: function_to_call(dataset_name=name, **kwargs),
                dataset_names,
            )
