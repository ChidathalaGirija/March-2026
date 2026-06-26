# Databricks notebook source
# MAGIC %md
# MAGIC 1. Load data from Ingestion Layer

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import *

# Example: read from ingestion path or table
df = spark.read.format("delta").table("ingestion_retail_sales")

print("✅ Data loaded from ingestion layer")

# COMMAND ----------

# MAGIC %md
# MAGIC 2. Add Audit Columns

# COMMAND ----------

df_bronze = df \
    .withColumn("ingestion_timestamp", current_timestamp()) \
    .withColumn("source_file_name", input_file_name()) \
    .withColumn("batch_id", lit("batch_001")) \
    .withColumn("processing_date", current_date())

print("✅ Audit columns added")

# COMMAND ----------

# MAGIC %md
# MAGIC 3. Write to Bronze Delta Table

# COMMAND ----------

# DBTITLE 1,Cell 6
(
    spark.read.format("csv")
    .option("header", "true")
    .schema(StructType([
        StructField("Row ID", IntegerType(), True),
        StructField("Order ID", StringType(), True),
        StructField("Sales", DoubleType(), True)
    ]))
    .load("/Volumes/retaildatabricks/retailsales/salesdata/")
    .withColumnRenamed("Row ID", "row_id")
    .withColumnRenamed("Order ID", "order_id")
    .withColumn("ingestion_timestamp", current_timestamp())
    .select("*", "_metadata.file_path")
    .withColumnRenamed("file_path", "source_file_name")
    .withColumn("batch_id", lit("batch_001"))
    .withColumn("processing_date", current_date().cast("string"))
    .select(
        "row_id",
        "order_id",
        "Sales",
        "source_file_name",
        "ingestion_timestamp",
        "batch_id",
        "processing_date"
    )
    .withColumnRenamed("Sales", "sales")
    .write.format("delta")
    .mode("overwrite")
    .saveAsTable("bronze_retail_sales")
)

print("✅ Data loaded into Bronze layer")

# COMMAND ----------

# MAGIC %md
# MAGIC 4. Validation Section

# COMMAND ----------

# DBTITLE 1,Cell 8
total_count = spark.table("retaildatabricks.default.bronze_retail_sales").count()
print("Total Records:", total_count)

# COMMAND ----------

# MAGIC %md
# MAGIC Null Count per Column

# COMMAND ----------

# DBTITLE 1,Cell 10
bronze_df = spark.table("retaildatabricks.default.bronze_retail_sales")

null_counts = bronze_df.select([
    sum(col(c).isNull().cast("int")).alias(c)
    for c in bronze_df.columns
])

display(null_counts)

# COMMAND ----------

# MAGIC %md
# MAGIC Duplicate Record Count

# COMMAND ----------

# DBTITLE 1,Cell 12
bronze_df = spark.table("retaildatabricks.default.bronze_retail_sales")
duplicate_count = bronze_df.count() - bronze_df.dropDuplicates().count()
print("Duplicate Records:", duplicate_count)

# COMMAND ----------

# MAGIC %md
# MAGIC Schema Validation

# COMMAND ----------

# DBTITLE 1,Cell 14
spark.table("retaildatabricks.default.bronze_retail_sales").printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC Mandatory Column Validation

# COMMAND ----------

# DBTITLE 1,Cell 16
mandatory_columns = ["id", "date", "amount"]  # change as per your dataset

bronze_columns = spark.table("retaildatabricks.default.bronze_retail_sales").columns
missing_cols = [c for c in mandatory_columns if c not in bronze_columns]

if len(missing_cols) == 0:
    print("✅ All mandatory columns present")
else:
    print("❌ Missing columns:", missing_cols)

# COMMAND ----------

# MAGIC %md
# MAGIC logging Requirements

# COMMAND ----------

# MAGIC %md
# MAGIC 1. Create Logging DataFrame / Table (Recommended)

# COMMAND ----------

spark.sql("""
CREATE TABLE IF NOT EXISTS bronze_pipeline_logs (
    job_name STRING,
    source_record_count BIGINT,
    target_record_count BIGINT,
    validation_result STRING,
    processing_duration_seconds DOUBLE,
    job_status STRING,
    start_time TIMESTAMP,
    end_time TIMESTAMP
)
USING DELTA
""")

# COMMAND ----------

# MAGIC %md
# MAGIC 2. Capture Start Time

# COMMAND ----------

from pyspark.sql.functions import *
import time

job_name = "bronze_retail_sales_job"

start_time = time.time()
start_timestamp = current_timestamp()

# COMMAND ----------

# MAGIC %md
# MAGIC 3. Source & Target Counts

# COMMAND ----------

# DBTITLE 1,Cell 24
source_count = (
    spark.read.format("csv")
    .option("header", "true")
    .schema(StructType([
        StructField("Row ID", IntegerType(), True),
        StructField("Order ID", StringType(), True),
        StructField("Sales", DoubleType(), True)
    ]))
    .load("/Volumes/retaildatabricks/retailsales/salesdata/")
    .count()
)
target_count = spark.table("retaildatabricks.default.bronze_retail_sales").count()

# COMMAND ----------

# MAGIC %md
# MAGIC 4. Validation Results

# COMMAND ----------

# DBTITLE 1,Cell 26
source_count = (
    spark.read.format("csv")
    .option("header", "true")
    .schema(StructType([
        StructField("Row ID", IntegerType(), True),
        StructField("Order ID", StringType(), True),
        StructField("Sales", DoubleType(), True)
    ]))
    .load("/Volumes/retaildatabricks/retailsales/salesdata/")
    .count()
)
target_count = spark.table("retaildatabricks.default.bronze_retail_sales").count()
print("Source Count:", source_count)
print("Target Count:", target_count)


# COMMAND ----------

# DBTITLE 1,Validation Results
validation_results = []

# Null check
bronze_table = spark.table("retaildatabricks.default.bronze_retail_sales")
null_check = bronze_table.select([sum(col(c).isNull().cast("int")).alias(c) for c in bronze_table.columns])

if source_count == target_count:
    validation_results.append("Record count matched")
else:
    validation_results.append("Record count mismatch")

validation_result_str = ", ".join(validation_results)
print("Validation:", validation_result_str)

# COMMAND ----------

# MAGIC %md
# MAGIC 5. Processing Duration

# COMMAND ----------

end_time = time.time()
processing_duration = end_time - start_time

# COMMAND ----------

# MAGIC %md
# MAGIC 6. Job Status Logic

# COMMAND ----------

if "mismatch" in validation_result_str.lower():
    job_status = "FAILED"
else:
    job_status = "SUCCESS"

# COMMAND ----------

# MAGIC %md
# MAGIC 7. Write Logs to Table

# COMMAND ----------

# DBTITLE 1,Cell 33
import datetime

log_df = spark.createDataFrame([(
    job_name,
    source_count,
    target_count,
    validation_result_str,
    processing_duration,
    job_status,
    datetime.datetime.now(),
    datetime.datetime.now()
)], schema="""
job_name STRING,
source_record_count BIGINT,
target_record_count BIGINT,
validation_result STRING,
processing_duration_seconds DOUBLE,
job_status STRING,
start_time TIMESTAMP,
end_time TIMESTAMP
""")

log_df.write.mode("append").saveAsTable("bronze_pipeline_logs")

print("✅ Pipeline log written successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC Audit Columns

# COMMAND ----------

from pyspark.sql.functions import *
import uuid

df_bronze = df \
    .withColumn("batch_id", lit(str(uuid.uuid4()))) \
    .withColumn("load_timestamp", current_timestamp()) \
    .withColumn("processing_date", current_date()) \
    .withColumn("source_system", lit("azure_sql")) \
    .withColumn("created_timestamp", current_timestamp())

# COMMAND ----------

# MAGIC %md
# MAGIC Deliverables

# COMMAND ----------

# DBTITLE 1,Untitled
# Bronze Delta Table


# COMMAND ----------

# DBTITLE 1,Cell 37
df = (
    spark.read.format("csv")
    .option("header", "true")
    .schema(StructType([
        StructField("Row ID", IntegerType(), True),
        StructField("Order ID", StringType(), True),
        StructField("Sales", DoubleType(), True)
    ]))
    .load("/Volumes/retaildatabricks/retailsales/salesdata/")
)

(
    df
    .withColumnRenamed("Row ID", "row_id")
    .withColumnRenamed("Order ID", "order_id")
    .withColumn("ingestion_timestamp", current_timestamp())
    .select("*", "_metadata.file_path")
    .withColumnRenamed("file_path", "source_file_name")
    .withColumn("batch_id", lit("batch_001"))
    .withColumn("processing_date", current_date().cast("string"))
    .select(
        "row_id",
        "order_id",
        "Sales",
        "source_file_name",
        "ingestion_timestamp",
        "batch_id",
        "processing_date"
    )
    .withColumnRenamed("Sales", "sales")
    .write.format("delta")
    .mode("overwrite")
    .saveAsTable("bronze_retail_sales")
)

df_bronze = spark.table("retaildatabricks.default.bronze_retail_sales")

# COMMAND ----------

# MAGIC %md
# MAGIC 2. Validation Report

# COMMAND ----------

# DBTITLE 1,Cell 39
bronze_table = spark.table("retaildatabricks.default.bronze_retail_sales")
source_count = (
    spark.read.format("csv")
    .option("header", "true")
    .schema(StructType([
        StructField("Row ID", IntegerType(), True),
        StructField("Order ID", StringType(), True),
        StructField("Sales", DoubleType(), True)
    ]))
    .load("/Volumes/retaildatabricks/retailsales/salesdata/")
    .count()
)

target_count = bronze_table.count()
duplicate_count = target_count - bronze_table.dropDuplicates().count()
null_counts = {
    c: bronze_table.filter(col(c).isNull()).count()
    for c in bronze_table.columns
}

validation_report = {
    "source_count": source_count,
    "target_count": target_count,
    "duplicate_count": duplicate_count,
    "null_counts": null_counts,
    "schema": bronze_table.schema.simpleString(),
    "missing_mandatory_columns": [
        c for c in ["id", "date", "amount"] if c not in bronze_table.columns
    ]
}

display(validation_report)

# COMMAND ----------

# MAGIC %md
# MAGIC 3. Audit Report

# COMMAND ----------

# DBTITLE 1,Cell 41
import uuid
from pyspark.sql.functions import *

audit_report = {
    "batch_id": str(uuid.uuid4()),
    "source_system": "azure_sql",
    "processing_date": current_date(),
    "load_timestamp": current_timestamp(),
    "record_count": spark.table("retaildatabricks.default.bronze_retail_sales").count()
}

display(audit_report)

# COMMAND ----------

# MAGIC %md
# MAGIC 4. Execution Logs
# MAGIC

# COMMAND ----------

# DBTITLE 1,Cell 43
import time
import datetime

start_time = time.time()

source_count = (
    spark.read.format("csv")
    .option("header", "true")
    .schema(StructType([
        StructField("Row ID", IntegerType(), True),
        StructField("Order ID", StringType(), True),
        StructField("Sales", DoubleType(), True)
    ]))
    .load("/Volumes/retaildatabricks/retailsales/salesdata/")
    .count()
)
target_count = spark.table("retaildatabricks.default.bronze_retail_sales").count()

end_time = time.time()
duration = end_time - start_time

job_status = "SUCCESS" if source_count == target_count else "FAILED"

log_df = spark.createDataFrame([(
    audit_report["batch_id"],
    source_count,
    target_count,
    job_status,
    duration,
    datetime.datetime.now()
)], schema="""
batch_id STRING,
source_count BIGINT,
target_count BIGINT,
job_status STRING,
processing_duration_seconds DOUBLE,
log_timestamp TIMESTAMP
""")

log_df.write.mode("append").saveAsTable("bronze_execution_logs")

print("✅ Execution logs stored")

# COMMAND ----------

# DBTITLE 1,Cell 44
display(spark.table("retaildatabricks.default.bronze_retail_sales"))