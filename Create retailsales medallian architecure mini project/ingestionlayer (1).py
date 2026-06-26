# Databricks notebook source
try:
    volume_paths = dbutils.fs.ls("/Volumes/retaildatabricks/retailsales/")
    for v in volume_paths:
        print(f"{v.path} - {v.name}")
except Exception as e:
    print(f"Error listing volumes: {e}")

# COMMAND ----------

df = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("/Volumes/retaildatabricks/retailsales/salesdata/train.csv")

display(df)

# COMMAND ----------

# MAGIC %md
# MAGIC 1. Source File Validation

# COMMAND ----------

path = "/Volumes/retaildatabricks/retailsales/salesdata/"

files = dbutils.fs.ls(path)

if len(files) == 0:
    raise Exception("❌ No files found in source path")
else:
    print("✅ Files available:")
    for f in files:
        print(f.name)

# COMMAND ----------

# MAGIC %md
# MAGIC 2. File Format Validation
# MAGIC

# COMMAND ----------

for f in files:
    if not f.name.endswith(".csv"):
        raise Exception(f"❌ Invalid file format: {f.name}")

print("✅ All files are CSV")

# COMMAND ----------

# MAGIC %md
# MAGIC 3. File Size Validation

# COMMAND ----------

for f in files:
    size_mb = f.size / (1024 * 1024)
    print(f"{f.name} → {round(size_mb,2)} MB")
    
    if size_mb == 0:
        raise Exception(f"❌ File is empty: {f.name}")

print("✅ File size validation passed")

# COMMAND ----------

# MAGIC %md
# MAGIC 4. File Naming Convention Validation

# COMMAND ----------

import re

pattern = r"^(train|sales).*\.csv$"

for f in files:
    if not re.match(pattern, f.name):
        raise Exception(f"❌ Invalid file name: {f.name}")

print("✅ File naming convention valid")

# COMMAND ----------

# MAGIC %md
# MAGIC 5. Schema Validation

# COMMAND ----------

from pyspark.sql.types import *

expected_schema = StructType([
    StructField("Row ID", IntegerType(), True),
    StructField("Order ID", StringType(), True),
    StructField("Order Date", StringType(), True),
    StructField("Ship Date", StringType(), True),
    StructField("Ship Mode", StringType(), True),
    StructField("Customer ID", StringType(), True),
    StructField("Customer Name", StringType(), True),
    StructField("Segment", StringType(), True),
    StructField("Country", StringType(), True),
    StructField("City", StringType(), True),
    StructField("State", StringType(), True),
    StructField("Postal Code", StringType(), True),
    StructField("Region", StringType(), True),
    StructField("Product ID", StringType(), True),
    StructField("Category", StringType(), True),
    StructField("Sub-Category", StringType(), True),
    StructField("Product Name", StringType(), True),
    StructField("Sales", DoubleType(), True)
])

# COMMAND ----------

# MAGIC %md
# MAGIC Read Data with Schema

# COMMAND ----------

df = spark.read.format("csv") \
    .schema(expected_schema) \
    .option("header", "true") \
    .load(path)

print("✅ Data loaded with expected schema")

# COMMAND ----------

# MAGIC %md
# MAGIC 🔹 Compare Schema

# COMMAND ----------

if df.schema != expected_schema:
    raise Exception("❌ Schema mismatch detected")
else:
    print("✅ Schema validation passed")

# COMMAND ----------

# MAGIC %md
# MAGIC Setup Variables

# COMMAND ----------

from pyspark.sql.functions import current_timestamp, input_file_name, lit
from datetime import datetime
import uuid

source_path = "/Volumes/retaildatabricks/retailsales/salesdata/"
batch_id = str(uuid.uuid4())
processing_date = datetime.today().strftime('%Y-%m-%d')

start_time = datetime.now()
print(f"🚀 Pipeline started at: {start_time}")

# COMMAND ----------

# MAGIC %md
# MAGIC Ingestion Enrichment (Audit Columns)

# COMMAND ----------

df = df.withColumn("ingestion_timestamp", current_timestamp()) \
       .withColumn("source_file_name", input_file_name()) \
       .withColumn("batch_id", lit(batch_id)) \
       .withColumn("processing_date", lit(processing_date))

# COMMAND ----------

# MAGIC %md
# MAGIC 9. Write to Bronze Layer
# MAGIC

# COMMAND ----------

from pyspark.sql.functions import current_timestamp, input_file_name, lit
from pyspark.sql.types import *
from datetime import datetime
import uuid

# Paths
source_path = "/Volumes/retaildatabricks/retailsales/salesdata/"

# Metadata
batch_id = str(uuid.uuid4())
processing_date = datetime.today().strftime('%Y-%m-%d')

# Logging
start_time = datetime.now()
status = "SUCCESS"
error_message = ""

print(f"🚀 Pipeline Started at: {start_time}")

# COMMAND ----------

try:
    files = dbutils.fs.ls(source_path)

    if len(files) == 0:
        raise Exception("❌ No files found in source path")

    file_names = []
    
    for f in files:
        # File format check
        if not f.name.endswith(".csv"):
            raise Exception(f"❌ Invalid file format: {f.name}")
        
        # Empty file check
        if f.size == 0:
            raise Exception(f"❌ Empty file: {f.name}")
        
        file_names.append(f.name)

    print("✅ Source validation passed")

except Exception as e:
    status = "FAILED"
    error_message = str(e)
    raise

# COMMAND ----------

if len(file_names) != len(set(file_names)):
    raise Exception("❌ Duplicate files detected")

print("✅ No duplicate files")

# COMMAND ----------

expected_schema = StructType([
    StructField("Row ID", IntegerType(), True),
    StructField("Order ID", StringType(), True),
    StructField("Sales", DoubleType(), True)
])

# COMMAND ----------

try:
    df = spark.read.format("csv") \
        .option("header", "true") \
        .schema(expected_schema) \
        .load(source_path)

    print("✅ Data read successfully")

except Exception as e:
    status = "FAILED"
    error_message = str(e)
    raise

# COMMAND ----------

if df.schema != expected_schema:
    raise Exception("❌ Schema mismatch")

print("✅ Schema validation passed")

# COMMAND ----------

df = df.withColumn("ingestion_timestamp", current_timestamp()) \
       .withColumn("source_file_name", input_file_name()) \
       .withColumn("batch_id", lit(batch_id)) \
       .withColumn("processing_date", lit(processing_date))

# COMMAND ----------

from pyspark.sql.functions import current_timestamp, lit

df = df.withColumn("ingestion_timestamp", current_timestamp()) \
       .withColumn("source_file_name", input_file_name()) \
       .withColumn("batch_id", lit(batch_id)) \
       .withColumn("processing_date", lit(processing_date))

# COMMAND ----------

# DBTITLE 1,Cell 30
record_count = (
    spark.read.format("csv")
    .option("header", "true")
    .schema(expected_schema)
    .load(source_path)
    .count()
)
print(f"📊 Total records read: {record_count}")

# COMMAND ----------

# DBTITLE 1,Write Bronze Table
from pyspark.sql.functions import current_timestamp, lit

bronze_df = (
    spark.read.format("csv")
    .option("header", "true")
    .schema(expected_schema)
    .load(source_path)
    .selectExpr("`Row ID` as row_id", "`Order ID` as order_id", "_metadata.file_path")
    .withColumnRenamed("file_path", "source_file_name")
    .withColumn("ingestion_timestamp", current_timestamp())
    .withColumn("batch_id", lit(batch_id))
    .withColumn("processing_date", lit(processing_date))
)

record_count = bronze_df.count()

bronze_df.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("bronze_retail_sales")

print(f"✅ Data loaded into Bronze layer with {record_count} records")

# COMMAND ----------

end_time = datetime.now()

log_data = [(
    str(start_time),
    str(end_time),
    ",".join(file_names),
    record_count,
    status,
    error_message
)]

log_df = spark.createDataFrame(log_data, [
    "start_time",
    "end_time",
    "file_names",
    "record_count",
    "status",
    "error_message"
])

log_df.write.mode("append").saveAsTable("ingestion_logs")

print("✅ Logs generated successfully")
