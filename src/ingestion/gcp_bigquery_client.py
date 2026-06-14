from google.cloud import bigquery
from typing import Optional


class BigQueryClient:
    def __init__(self, project: Optional[str] = None):
        self.client = bigquery.Client(project=project)

    def load_table(self, dataset: str, table: str):
        dataset_ref = self.client.dataset(dataset)
        table_ref = dataset_ref.table(table)
        table = self.client.get_table(table_ref)
        return self.client.list_rows(table).to_dataframe()

    def run_query(self, query: str):
        job = self.client.query(query)
        return job.result().to_dataframe()
