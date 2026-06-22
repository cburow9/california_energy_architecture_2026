import logging
from typing import Iterator, Optional, Dict, Any
from functools import wraps
import time

from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPICallError, NotFound, Cancelled

logger = logging.getLogger(__name__)


def retry_on_transient(max_retries: int = 3, backoff_factor: float = 1.5):
    """
    Decorator to retry on transient BigQuery errors.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (Cancelled, TimeoutError) as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} retries: {e}")
                        raise
                    wait_time = backoff_factor ** attempt
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
        return wrapper
    return decorator


class BigQueryClient:
    """BigQuery client with error handling, retry logic, and cost controls."""
    
    def __init__(
        self,
        project: Optional[str] = None,
        max_results_per_page: int = 10000,
        timeout_seconds: int = 300,
        max_bytes_billed: int = 10_000_000_000
    ):
        """
        Initialize BigQuery client with safety defaults.
        
        Args:
            project: GCP project ID
            max_results_per_page: Limit for streaming results to avoid memory overload
            timeout_seconds: Query timeout in seconds
            max_bytes_billed: Maximum bytes to bill per query (10GB default = cost limit)
        """
        try:
            self.client = bigquery.Client(project=project)
            self.max_results_per_page = max_results_per_page
            self.timeout_seconds = timeout_seconds
            self.max_bytes_billed = max_bytes_billed
            logger.info(f"BigQuery client initialized for project: {project}")
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery client: {e}")
            raise

    @retry_on_transient(max_retries=3)
    def load_table(self, dataset: str, table: str) -> Iterator[Dict[str, Any]]:
        """
        Stream rows from a table with chunking to avoid memory overload.
        
        Args:
            dataset: Dataset ID
            table: Table ID
            
        Yields:
            Rows as dictionaries
            
        Raises:
            NotFound: If table doesn't exist
            GoogleAPICallError: On API errors after retries
        """
        try:
            table_id = f"{self.client.project}.{dataset}.{table}"
            table_ref = self.client.get_table(table_id)
            logger.info(f"Loading table {table_id} with page size {self.max_results_per_page}")
            
            row_count = 0
            for row in self.client.list_rows(table_ref, page_size=self.max_results_per_page):
                row_count += 1
                yield dict(row)
            
            logger.info(f"Successfully streamed {row_count} rows from {table_id}")
                
        except NotFound as e:
            logger.error(f"Table not found: {dataset}.{table}")
            raise
        except Exception as e:
            logger.error(f"Error loading table {dataset}.{table}: {e}")
            raise

    @retry_on_transient(max_retries=3)
    def run_query(
        self,
        query: str,
        use_cache: bool = True,
        priority: str = "interactive",
        query_params: Optional[list] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        Execute query with timeout, caching, and cost controls.
        
        Args:
            query: SQL query string
            use_cache: Use BigQuery result cache (faster, no additional cost)
            priority: 'interactive' or 'batch' (batch is cheaper, slower)
            query_params: List of query parameters for parameterized queries
            
        Yields:
            Query result rows as dictionaries
            
        Raises:
            TimeoutError: If query exceeds timeout
            GoogleAPICallError: On API errors after retries
        """
        job_config = bigquery.QueryJobConfig(
            use_query_cache=use_cache,
            priority=bigquery.QueryPriority.INTERACTIVE if priority == "interactive"
                     else bigquery.QueryPriority.BATCH,
            maximum_bytes_billed=self.max_bytes_billed,
            query_parameters=query_params or []
        )
        
        try:
            logger.info(f"Executing query (priority={priority}, cache={use_cache})")
            job = self.client.query(query, job_config=job_config, timeout=self.timeout_seconds)
            
            row_count = 0
            for row in job.result(page_size=self.max_results_per_page):
                row_count += 1
                yield dict(row)
            
            bytes_billed = job.total_bytes_billed or 0
            logger.info(
                f"Query completed. Rows: {row_count}, Bytes billed: {bytes_billed:,}, "
                f"Slot time: {job.slot_millis}ms"
            )
            
        except TimeoutError as e:
            logger.error(f"Query timed out after {self.timeout_seconds}s")
            raise
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
