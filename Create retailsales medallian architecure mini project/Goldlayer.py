# Databricks notebook source
# MAGIC %md
# MAGIC Load silverlayer data

# COMMAND ----------

from pyspark.sql.functions import *
from datetime import datetime

silver_df = spark.table("silver_retail_sales")

# COMMAND ----------

# MAGIC %md
# MAGIC 2. Initialize Variables

# COMMAND ----------

batch_id = "BATCH_001"
aggregation_date = current_date()
processing_time = current_timestamp()

start_time = datetime.now()
source_records = silver_df.count()

# COMMAND ----------

# MAGIC %md
# MAGIC 3. Business Aggregations

# COMMAND ----------

# MAGIC %md
# MAGIC KPI Table

# COMMAND ----------

# DBTITLE 1,Cell 7
kpi_df = silver_df.agg(
    count("*").alias("total_transactions"),
    sum("sales").alias("total_revenue"),
    avg("sales").alias("avg_transaction_value"),
    countDistinct("order_id").alias("unique_orders")
)



# COMMAND ----------

# MAGIC %md
# MAGIC Summary Table

# COMMAND ----------

# DBTITLE 1,Cell 9
summary_df = silver_df.groupBy("order_id").agg(
    sum("sales").alias("total_spent"),
    count("*").alias("total_orders")
)

# COMMAND ----------

# MAGIC %md
# MAGIC Trend Analysis (Daily Sales)

# COMMAND ----------

# DBTITLE 1,Cell 11
trend_df = silver_df.groupBy("processing_date").agg(
    sum("sales").alias("daily_sales"),
    count("*").alias("daily_orders")
).orderBy("processing_date")

# COMMAND ----------

# MAGIC %md
# MAGIC Performance Metrics Table

# COMMAND ----------

# DBTITLE 1,Cell 13
performance_df = silver_df.groupBy("source_layer").agg(
    sum("sales").alias("revenue"),
    count("*").alias("transactions")
)

# COMMAND ----------

# MAGIC %md
# MAGIC Reporting Table (Final Business View)

# COMMAND ----------

# DBTITLE 1,Cell 15
report_df = silver_df.select(
    "order_id",
    "sales",
    "processing_date",
    "source_layer"
)

# COMMAND ----------

# MAGIC %md
# MAGIC **Validations**

# COMMAND ----------

# MAGIC %md
# MAGIC Aggregate Totals Check

# COMMAND ----------

# DBTITLE 1,Cell 18
silver_total = silver_df.agg(sum("sales")).collect()[0][0]
gold_total = summary_df.agg(sum("total_spent")).collect()[0][0]

print("Totals Match:", silver_total == gold_total)

# COMMAND ----------

# MAGIC %md
# MAGIC Duplicate Check

# COMMAND ----------

dup_count = summary_df.count() - summary_df.dropDuplicates().count()
print("Duplicate Aggregates:", dup_count)

# COMMAND ----------

# MAGIC %md
# MAGIC Missing Dimensions

# COMMAND ----------

# DBTITLE 1,Cell 22
summary_df.filter(col("order_id").isNull()).show()

# COMMAND ----------

# MAGIC %md
# MAGIC Missing Measures

# COMMAND ----------

summary_df.filter(col("total_spent").isNull()).show()

# COMMAND ----------

# MAGIC %md
# MAGIC **Add Audit Columns**

# COMMAND ----------

def add_audit(df):
    return df.withColumn("batch_id", lit(batch_id)) \
             .withColumn("aggregation_date", aggregation_date) \
             .withColumn("processing_timestamp", processing_time) \
             .withColumn("gold_load_status", lit("SUCCESS"))

kpi_df = add_audit(kpi_df)
summary_df = add_audit(summary_df)
trend_df = add_audit(trend_df)
performance_df = add_audit(performance_df)
report_df = add_audit(report_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Logging Metrics

# COMMAND ----------

target_records = report_df.count()

end_time = datetime.now()
duration = (end_time - start_time).seconds

print("===== Gold Layer Logs =====")
print(f"Source Records      : {source_records}")
print(f"Target Records      : {target_records}")
print(f"Processing Duration : {duration} sec")
print("KPI Generation      : SUCCESS")

# COMMAND ----------

# MAGIC %md
# MAGIC **Write Gold Tables**

# COMMAND ----------

# MAGIC %md
# MAGIC KPI Table

# COMMAND ----------

kpi_df.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("gold_kpi_table")

# COMMAND ----------

# MAGIC %md
# MAGIC Summary Table

# COMMAND ----------

summary_df.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("gold_summary_table")

# COMMAND ----------

# MAGIC %md
# MAGIC Trend Table

# COMMAND ----------

trend_df.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("gold_trend_table")

# COMMAND ----------

# MAGIC %md
# MAGIC Performance Table

# COMMAND ----------

performance_df.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("gold_performance_table")

# COMMAND ----------

# MAGIC %md
# MAGIC Reporting Table

# COMMAND ----------

report_df.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("gold_reporting_table")

# COMMAND ----------

# MAGIC %md
# MAGIC **Validation Report**

# COMMAND ----------

validation_df = spark.createDataFrame([
    ("Totals Match", int(silver_total == gold_total)),
    ("Duplicate Aggregates", dup_count)
], ["Validation", "Result"])

validation_df.show()

# COMMAND ----------

# MAGIC %md
# MAGIC Audit Report

# COMMAND ----------

audit_df = spark.createDataFrame([
    (batch_id, str(datetime.now()), "SUCCESS")
], ["Batch_ID", "Processing_Time", "Status"])

audit_df.write.format("delta") \
    .mode("append") \
    .saveAsTable("audit_gold_layer")

# COMMAND ----------

# MAGIC %md
# MAGIC Logging Framework

# COMMAND ----------

spark.sql("""
CREATE TABLE IF NOT EXISTS log_table (
    notebook_name STRING,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration INT,
    batch_id STRING,
    source_layer STRING,
    target_layer STRING,
    record_count INT,
    success_status STRING,
    failure_status STRING,
    error_details STRING
)
USING DELTA
""")

# COMMAND ----------

# MAGIC %md
# MAGIC Logging Functions

# COMMAND ----------

# DBTITLE 1,Cell 47
from datetime import datetime

def log_execution(notebook, start_time, batch_id, source, target, record_count, status, error_msg=""):
    
    end_time = datetime.now()
    duration = (end_time - start_time).seconds
    
    log_data = [(notebook, start_time, end_time, duration, batch_id,
                 source, target, record_count,
                 "SUCCESS" if status == "SUCCESS" else "FAILED",
                 "FAILED" if status == "FAILED" else "NA",
                 error_msg)]
    
    columns = ["notebook_name","start_time","end_time","duration","batch_id",
               "source_layer","target_layer","record_count",
               "success_status","failure_status","error_details"]
    
    spark.createDataFrame(log_data, "notebook_name STRING, start_time TIMESTAMP, end_time TIMESTAMP, duration INT, batch_id STRING, source_layer STRING, target_layer STRING, record_count INT, success_status STRING, failure_status STRING, error_details STRING") \
        .write.format("delta").mode("append").saveAsTable("log_table")

# COMMAND ----------

# MAGIC %md
# MAGIC 2. Validation Framework

# COMMAND ----------

# MAGIC %md
# MAGIC Create Validation Table
# MAGIC

# COMMAND ----------

spark.sql("""
CREATE TABLE IF NOT EXISTS validation_table (
    validation_name STRING,
    validation_status STRING,
    expected_result STRING,
    actual_result STRING,
    failed_count INT,
    validation_timestamp TIMESTAMP
)
USING DELTA
""")

# COMMAND ----------

# MAGIC %md
# MAGIC Validation Function

# COMMAND ----------

def log_validation(name, expected, actual, failed_count):
    
    status = "PASS" if expected == actual else "FAIL"
    
    val_data = [(name, status, str(expected), str(actual), failed_count, datetime.now())]
    
    columns = ["validation_name","validation_status","expected_result",
               "actual_result","failed_count","validation_timestamp"]
    
    spark.createDataFrame(val_data, columns) \
        .write.format("delta").mode("append").saveAsTable("validation_table")

# COMMAND ----------

# MAGIC %md
# MAGIC **3. Audit Framework**

# COMMAND ----------

# MAGIC %md
# MAGIC Create Audit Table

# COMMAND ----------

spark.sql("""
CREATE TABLE IF NOT EXISTS audit_table (
    batch_id STRING,
    source_name STRING,
    target_name STRING,
    processing_date DATE,
    total_read INT,
    total_written INT,
    rejected_records INT,
    status STRING
)
USING DELTA
""")

# COMMAND ----------

# MAGIC %md
# MAGIC Audit Function

# COMMAND ----------

def log_audit(batch_id, source, target, read_count, write_count, reject_count, status):
    
    audit_data = [(batch_id, source, target, datetime.now().date(),
                   read_count, write_count, reject_count, status)]
    
    columns = ["batch_id","source_name","target_name","processing_date",
               "total_read","total_written","rejected_records","status"]
    
    spark.createDataFrame(audit_data, columns) \
        .write.format("delta").mode("append").saveAsTable("audit_table")