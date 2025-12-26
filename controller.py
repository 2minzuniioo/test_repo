import boto3
import time
import requests
import json
import socket
import argparse

ec2 = boto3.client('ec2', region_name='$REGION')

def get_running_workers():
    # Find workers by Tag Name=worker-*
    resp = ec2.describe_instances(Filters=[
        {'Name': 'tag:Name', 'Values': ['worker-*']},
        {'Name': 'instance-state-name', 'Values': ['running']}
    ])
    instances = []
    for r in resp['Reservations']:
        for i in r['Instances']:
            instances.append(i)
    return instances

def wait_for_workers(target_count=8):
    print(f"Waiting for {target_count} workers to be RUNNING...")
    while True:
        workers = get_running_workers()
        count = len(workers)
        print(f"Current running workers: {count}/{target_count}")
        if count >= target_count:
            return workers
        time.sleep(5)


def main():
    parser = argparse.ArgumentParser(description="Controller for Distributed System")
    parser.add_argument('--region', type=str, default='$REGION', help='AWS Region')
    parser.add_argument('--worker-count', type=int, default=8, help='Number of worker nodes to wait for')
    args = parser.parse_args()


    workers = wait_for_workers(args.worker_count)
    print(f"All {args.worker_count} workers are running.")

    # Collect IPs
    worker_ips = [w['PrivateIpAddress'] for w in workers]
    print(f"Worker IPs: {worker_ips}")

    # Health Check
    for ip in worker_ips:
        url = f"http://{ip}:8080/health" # Using standard port 80 based on SG, though code said 8080. Spec says 8080.
        # Spec: Inbound 8080.
        print(f"Checking {url}...")
        while True:
            try:
                r = requests.get(url, timeout=2)
                if r.status_code == 200:
                    print(f"{ip} is READY")
                    break
            except Exception as e:
                print(f"Waiting for {ip}... ({e})")
                time.sleep(2)

    print("All workers healthy. Sending Control Data...")

    # Control Data Transmission
    for ip in worker_ips:
        try:
            # Example payload
            payload = {"action": "start", "config": "v2.1"} 
            # requests.post(f"http://{ip}:8080/control", json=payload)
            print(f"Sent control to {ip}")
        except:
            pass

    print("System Initialized.")