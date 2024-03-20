    import argparse
    import boto3
    import csv
    import time
    from datetime import datetime, timedelta
    import psutil
    import pandas as pd

    def get_rds_metrics(instance_id, days):
        client = boto3.client('cloudwatch')
        
        # Get the average and maximum CPU utilization, memory usage, and IOPS over the last 30 days
        response_cpu = client.get_metric_statistics(
            Namespace='AWS/RDS',
            MetricName='CPUUtilization',
            Dimensions=[
                {
                    'Name': 'DBInstanceIdentifier',
                    'Value': instance_id
                },
            ],
            StartTime=(datetime.utcnow() - timedelta(days=days)).isoformat(),
            EndTime=datetime.utcnow().isoformat(),
            Period=86400,  # 1 day intervals
            Statistics=['Average', 'Maximum'],
            Unit='Percent'
        )

        response_memory = client.get_metric_statistics(
            Namespace='AWS/RDS',
            MetricName='FreeableMemory',
            Dimensions=[
                {
                    'Name': 'DBInstanceIdentifier',
                    'Value': instance_id
                },
            ],
            StartTime=(datetime.utcnow() - timedelta(days=30)).isoformat(),
            EndTime=datetime.utcnow().isoformat(),
            Period=86400,  # 1 day intervals
            Statistics=['Average', 'Maximum'],
            Unit='Bytes'
        )

        response_iops_read = client.get_metric_statistics(
            Namespace='AWS/RDS',
            MetricName='ReadIOPS',
            Dimensions=[
                {
                    'Name': 'DBInstanceIdentifier',
                    'Value': instance_id
                },
            ],
            StartTime=(datetime.utcnow() - timedelta(days=30)).isoformat(),
            EndTime=datetime.utcnow().isoformat(),
            Period=86400,  # 1 day intervals
            Statistics=['Maximum'],
            Unit='Count/Second'
        )

        response_iops_write = client.get_metric_statistics(
            Namespace='AWS/RDS',
            MetricName='WriteIOPS',
            Dimensions=[
                {
                    'Name': 'DBInstanceIdentifier',
                    'Value': instance_id
                },
            ],
            StartTime=(datetime.utcnow() - timedelta(days=30)).isoformat(),
            EndTime=datetime.utcnow().isoformat(),
            Period=86400,  # 1 day intervals
            Statistics=['Maximum'],
            Unit='Count/Second'
        )

        if 'Datapoints' in response_cpu and response_cpu['Datapoints'] and 'Datapoints' in response_memory and response_memory['Datapoints'] and 'Datapoints' in response_iops_read and response_iops_read['Datapoints'] and 'Datapoints' in response_iops_write and response_iops_write['Datapoints']:
            average_cpu = round(response_cpu['Datapoints'][0]['Average'], 2)
            max_cpu = round(response_cpu['Datapoints'][0]['Maximum'], 2)
            average_memory_gb = round(response_memory['Datapoints'][0]['Average'] / (1024 ** 3), 2)
            max_memory_gb = round(response_memory['Datapoints'][0]['Maximum'] / (1024 ** 3), 2)
            max_iops_read = round(response_iops_read['Datapoints'][0]['Maximum'], 2)
            max_iops_write = round(response_iops_write['Datapoints'][0]['Maximum'], 2)
            return average_cpu, max_cpu, average_memory_gb, max_memory_gb, max_iops_read, max_iops_write
        else:
            return None, None, None, None, None, None

    def get_instance_info(instance):
        engine = instance['Engine']
        size = instance['DBInstanceClass']
        default_iops = instance.get('AllocatedStorage', 0)

        return engine, size, default_iops

    def get_all_rds_instances():
        client = boto3.client('rds')
        response = client.describe_db_instances()
        instances = response['DBInstances']
        return instances

    def main():
        parser = argparse.ArgumentParser(description='Fetch RDS instance utilization data.')
        parser.add_argument('--days', type=int, default=30, help='Number of days to pull data (default: 30)')
        args = parser.parse_args()
        instances = get_all_rds_instances()

        if not instances:
            print("No RDS instances found.")
            return

        # CSV header
        csv_data = [['InstanceID', 'Engine', 'Size', 'AverageCPUUtilization', 'MaxCPUUtilization', 'AverageMemoryUtilization(GB)', 'MaxMemoryUtilization(GB)', 'DefaultIOPS', 'MaxReadIOPS', 'MaxWriteIOPS']]

        for instance in instances:
            instance_id = instance['DBInstanceIdentifier']
            average_cpu, max_cpu, average_memory_gb, max_memory_gb, max_iops_read, max_iops_write = get_rds_metrics(instance_id, args.days)

            if all(val is not None for val in [average_cpu, max_cpu, average_memory_gb, max_memory_gb, max_iops_read, max_iops_write]):
                engine, size, default_iops = get_instance_info(instance)
                csv_data.append([instance_id, engine, size, average_cpu, max_cpu, average_memory_gb, max_memory_gb, default_iops, max_iops_read, max_iops_write])
                print(f"Instance ID: {instance_id}, Engine: {engine}, Size: {size}, Average CPU Utilization: {average_cpu}%, Max CPU Utilization: {max_cpu}%, "
                    f"Average Memory Utilization: {average_memory_gb}GB, Max Memory Utilization: {max_memory_gb}GB, Default IOPS: {default_iops}, Max Read IOPS: {max_iops_read}, Max Write IOPS: {max_iops_write}")

        # Create a DataFrame from the CSV data
        df = pd.DataFrame(csv_data[1:], columns=csv_data[0])

        # Save data to an Excel file with the specified format
        current_date = time.strftime('%Y%m%d%H%M%S')
        excel_file = f"rds_database_instance_utilization_{current_date}_30days.xlsx"
        df.to_excel(excel_file, index=False)

        print(f"Data saved to {excel_file}")

    if __name__ == "__main__":
        main()
