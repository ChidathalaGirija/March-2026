# Databricks notebook source
# MAGIC %md
# MAGIC 1. Load Data from Bronze Layer

# COMMAND ----------

df_bronze = spark.read.table("bronze_retail_sales")

display(df_bronze)

# COMMAND ----------

# MAGIC %md
# MAGIC 2. Data Cleaning & Standardization

# COMMAND ----------

# MAGIC %md
# MAGIC Remove Duplicates

# COMMAND ----------

df_silver = df_bronze.dropDuplicates()

# COMMAND ----------

# MAGIC %md
# MAGIC Handle Null Values

# COMMAND ----------

# DBTITLE 1,Cell 7
df_silver = df_silver.fillna({
    "sales": 0,
    "row_id": -1,
    "order_id": "unknown"
})

# COMMAND ----------

# MAGIC %md
# MAGIC Standardize Text Values

# COMMAND ----------

# DBTITLE 1,Cell 9
from pyspark.sql.functions import *

df_silver = df_silver \
    .withColumn("order_id", lower(trim(col("order_id"))))

# COMMAND ----------

# MAGIC %md
# MAGIC Correct Data Types

# COMMAND ----------

# DBTITLE 1,Cell 11
df_silver = df_silver \
    .withColumn("sales", col("sales").cast("double")) \
    .withColumn("processing_date", col("processing_date").cast("date"))

# COMMAND ----------

# MAGIC %md
# MAGIC Apply Business Rules

# COMMAND ----------

# DBTITLE 1,Cell 13
df_silver = df_silver.filter(col("sales") > 0)

# COMMAND ----------

# MAGIC %md
# MAGIC 3. Data Quality Validations

# COMMAND ----------

# MAGIC %md
# MAGIC Null Value Percentage

# COMMAND ----------

null_stats = df_silver.select([
    (sum(col(c).isNull().cast("int")) / count("*") * 100).alias(c)
    for c in df_silver.columns
])

display(null_stats)

# COMMAND ----------

# MAGIC %md
# MAGIC Duplicate Records Check

# COMMAND ----------

duplicate_count = df_silver.count() - df_silver.dropDuplicates().count()
print("Duplicate Records:", duplicate_count)

# COMMAND ----------

# MAGIC %md
# MAGIC Invalid Records Check

# COMMAND ----------

# DBTITLE 1,Cell 20
invalid_records = df_silver.filter(col("sales") <= 0)
print("Invalid Records:", invalid_records.count())

# COMMAND ----------

# DBTITLE 1,Cell 21
# Data Type Mismatch Check

# COMMAND ----------

df_silver.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC Mandatory Field Violations

# COMMAND ----------

mandatory_cols = ["id", "amount", "name"]

missing = [
    c for c in mandatory_cols if c not in df_silver.columns
]

print("Missing Mandatory Columns:", missing)

# COMMAND ----------

# MAGIC %md
# MAGIC Referential Integrity Check

# COMMAND ----------

# DBTITLE 1,Cell 26
# Example: checking orphan records
# (assuming customer_id should exist in customer table)

df_silver = df_silver.filter(col("row_id").isNotNull())

# COMMAND ----------

# MAGIC %md
# MAGIC Business Rule Violations

# COMMAND ----------

# DBTITLE 1,Cell 28
violations = df_silver.filter(col("sales") < 0)
print("Business Rule Violations:", violations.count())

# COMMAND ----------

# MAGIC %md
# MAGIC Reject Handling Design

# COMMAND ----------

# MAGIC %md
# MAGIC 1. Load Bronze Data

# COMMAND ----------

df = spark.read.table("bronze_retail_sales")



# COMMAND ----------

# MAGIC %md
# MAGIC 2. Define Data Quality Rules

# COMMAND ----------

# DBTITLE 1,Cell 33
from pyspark.sql.functions import *

mandatory_cols = ["row_id", "sales", "order_id"]

# COMMAND ----------

# MAGIC %md
# MAGIC 3. Identify Invalid Records

# COMMAND ----------

# DBTITLE 1,Cell 35
invalid_df = df.filter(
    (col("row_id").isNull()) |
    (col("sales").isNull()) |
    (col("sales") <= 0) |
    (col("order_id").isNull())
)

# COMMAND ----------

# MAGIC %md
# MAGIC 4. Valid Records (Silver Data)

# COMMAND ----------

valid_df = df.subtract(invalid_df)

# COMMAND ----------

# MAGIC %md
# MAGIC 5. Data Quality Failure Flagging

# COMMAND ----------

# DBTITLE 1,Cell 39
dq_failed_df = df.withColumn(
    "dq_status",
    when(
        (col("row_id").isNull()) |
        (col("sales").isNull()) |
        (col("sales") <= 0),
        "FAIL"
    ).otherwise("PASS")
)

# COMMAND ----------

# MAGIC %md
# MAGIC 6. Write Valid Data → Silver Table

# COMMAND ----------

valid_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("silver_retail_sales")

print("✅ Valid data written to Silver table")


# COMMAND ----------

# MAGIC %md
# MAGIC 7. Write Invalid Records → Rejected Table

# COMMAND ----------

# DBTITLE 1,Cell 43
invalid_df.withColumn("reject_reason",
    when(col("row_id").isNull(), "Missing ID")
    .when(col("sales").isNull(), "Missing Sales")
    .when(col("sales") <= 0, "Invalid Sales")
    .otherwise("Unknown")
).write \
 .format("delta") \
 .mode("overwrite") \
 .saveAsTable("silver_rejected_records")

print("❌ Invalid records stored in rejected table")

# COMMAND ----------

# MAGIC %md
# MAGIC 8. Write Data Quality Failures Table

# COMMAND ----------

dq_failed_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("silver_dq_failures")

print("⚠️ Data Quality failures stored")

# COMMAND ----------

# MAGIC %md
# MAGIC 9. Summary Metrics

# COMMAND ----------

print("Total Records:", df.count())
print("Valid Records:", valid_df.count())
print("Invalid Records:", invalid_df.count())
print("DQ Failures:", dq_failed_df.filter(col("dq_status") == "FAIL").count())

# COMMAND ----------

# MAGIC %md
# MAGIC Silver Layer — Logging Implementation

# COMMAND ----------

# MAGIC %md
# MAGIC 1. Start Timer

# COMMAND ----------

import time
from pyspark.sql.functions import *

start_time = time.time()

# COMMAND ----------

# MAGIC %md
# MAGIC 2. Records Received

# COMMAND ----------

records_received = df.count()

# COMMAND ----------

# MAGIC %md
# MAGIC 3. Identify Invalid / Rejected Records

# COMMAND ----------

# DBTITLE 1,Cell 54
invalid_df = df.filter(
    (col("row_id").isNull()) |
    (col("sales").isNull()) |
    (col("sales") <= 0)
)

records_rejected = invalid_df.count()

# COMMAND ----------

# MAGIC %md
# MAGIC 4. Valid Records

# COMMAND ----------

valid_df = df.subtract(invalid_df)
records_processed = valid_df.count()

# COMMAND ----------

# MAGIC %md
# MAGIC 5. Validation Failures

# COMMAND ----------

validation_failures = records_rejected   # same as rejected in this case

# COMMAND ----------

# MAGIC %md
# MAGIC 6. Processing Duration

# COMMAND ----------

end_time = time.time()
processing_duration = end_time - start_time

# COMMAND ----------

# MAGIC %md
# MAGIC 7. Job Status Logic

# COMMAND ----------

job_status = "SUCCESS" if records_rejected == 0 else "PARTIAL_SUCCESS"

# COMMAND ----------

# MAGIC %md
# MAGIC 8. Create Logging DataFrame

# COMMAND ----------

# DBTITLE 1,Cell 64
import datetime

log_df = spark.createDataFrame([(
    records_received,
    records_processed,
    records_rejected,
    validation_failures,
    processing_duration,
    job_status,
    datetime.datetime.now()
)], schema="""
records_received BIGINT,
records_processed BIGINT,
records_rejected BIGINT,
validation_failures BIGINT,
processing_duration_seconds DOUBLE,
job_status STRING,
log_timestamp TIMESTAMP
""")


# COMMAND ----------

# MAGIC %md
# MAGIC Add Audit Columns

# COMMAND ----------

# DBTITLE 1,Cell 66
import uuid

batch_id = str(uuid.uuid4())
source_layer = "silver"
processing_time = current_timestamp()

final_df = valid_df.withColumn("batch_id", lit(batch_id)) \
    .withColumn("source_layer", lit(source_layer)) \
    .withColumn("processing_timestamp", processing_time) \
    .withColumn("record_status", lit("VALID"))

# COMMAND ----------

# MAGIC %md
# MAGIC Rejected Audit

# COMMAND ----------

# DBTITLE 1,Cell 68
rejected_df = invalid_df.withColumn("batch_id", lit(batch_id)) \
    .withColumn("source_layer", lit(source_layer)) \
    .withColumn("processing_timestamp", processing_time) \
    .withColumn("record_status", lit("REJECTED"))

# COMMAND ----------

# MAGIC %md
# MAGIC Logging Metrics

# COMMAND ----------

# DBTITLE 1,Cell 70
records_processed = final_df.count()
records_rejected = rejected_df.count()
validation_failures = records_rejected

end_time = time.time()
duration = end_time - start_time

# COMMAND ----------

# MAGIC %md
# MAGIC Deliverables

# COMMAND ----------

# MAGIC %md
# MAGIC silver delta tables

# COMMAND ----------

# DBTITLE 1,Cell 73
final_df.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("silver_retail_sales")

print("✅ Valid data written to silver_retail_sales")

# COMMAND ----------

# MAGIC %md
# MAGIC Rejected Table

# COMMAND ----------

rejected_df.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("rejected_retail_sales")

# COMMAND ----------

# MAGIC %md
# MAGIC Validation Report

# COMMAND ----------

validation_report = spark.createDataFrame([
    ("Total Records", records_received),
    ("Processed Records", records_processed),
    ("Rejected Records", records_rejected),
    ("Duplicate Records", duplicate_count)
], ["Metric", "Value"])

validation_report.show()

# COMMAND ----------

# MAGIC %md
# MAGIC Audit Report

# COMMAND ----------

from datetime import datetime
audit_df = spark.createDataFrame([

    (batch_id, source_layer, str(datetime.now()), records_processed, records_rejected)
], ["Batch_ID", "Source_Layer", "Processing_Time", "Processed", "Rejected"])

audit_df.write.format("delta") \
    .mode("append") \
    .saveAsTable("audit_silver_layer")

# COMMAND ----------

# MAGIC %md
# MAGIC Execution Logs

# COMMAND ----------

print("===== Execution Summary =====")
print(f"Records Received  : {records_received}")
print(f"Records Processed : {records_processed}")
print(f"Records Rejected  : {records_rejected}")
print(f"Validation Errors : {validation_failures}")
print(f"Duration (sec)    : {duration}")

# COMMAND ----------

# MAGIC %md
# MAGIC View Refined (Silver) Data

# COMMAND ----------

df = spark.table("silver_retail_sales")
df.show(10, False)

# COMMAND ----------

# MAGIC %md
# MAGIC Compare Bronze vs Silver

# COMMAND ----------

bronze_count = spark.table("bronze_retail_sales").count()
silver_count = df.count()

print("Bronze Count :", bronze_count)
print("Silver Count :", silver_count)

# COMMAND ----------

# MAGIC %md
# MAGIC Check Audit Columns

# COMMAND ----------

df.select("batch_id", "source_layer", "processing_timestamp", "record_status").show(5, False)

# COMMAND ----------

# MAGIC %md
# MAGIC Quick Data Profiling

# COMMAND ----------

df.describe().show()