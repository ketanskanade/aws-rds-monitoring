# RDS Resource Utilization Monitoring Script

## Overview
This Python script retrieves and monitors Amazon RDS (Relational Database Service) resource utilization metrics and stores the data in an Excel sheet. The script uses AWS CloudWatch to gather information such as CPU utilization, memory usage, and IOPS (Input/Output Operations Per Second) for each RDS instance.

## Prerequisites
- Python 3.x
- AWS CLI configured with the necessary permissions
- Boto3 library
- Pandas library

## Usage
1. Clone the repository or download the `aws_rds_monitoring.py` script.
2. Install the required Python libraries:
    ```bash
    pip install boto3 pandas
    ```
3. Run the script with the desired options:
    ```bash
    python3 aws_rds_monitoring.py --days=30
    ```

## Options
- `--days`: Number of days to pull data (default: 30)

## Output
The script generates an Excel file containing RDS instance utilization data, with a filename format like `rds_database_instance_utilization_<timestamp>_30days.xlsx`.

## Sample Output
The script prints information about each RDS instance, including instance ID, engine, size, average and maximum CPU utilization, average and maximum memory utilization, default IOPS, and maximum read/write IOPS.

## Example
```bash
python3 aws_rds_monitoring.py --days=30
