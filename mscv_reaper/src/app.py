import sched, time, os, sys
from datetime import datetime
import pytz
import psycopg2
from psycopg2.extras import DictCursor

from kubernetes import client, config
from kubernetes.client.rest import ApiException
config.load_incluster_config() # Load the kubeconfig file
# Create a Kubernetes API client objects using the service account credentials
apps_api = client.AppsV1Api()
core_api = client.CoreV1Api()
autoscaling_api = client.AutoscalingV1Api()

def periodic(scheduler, interval, action, actionargs=()):
    action(*actionargs)
    scheduler.enter(interval, 1, periodic,
                    (scheduler, interval, action, actionargs))

def delete_service(service_user, func):
    namespace = 'default'
    delete_service_req = client.V1DeleteOptions(
        api_version = "v1",
        kind="DeleteOptions",
    )
    service_name = service_user + '-' + func + '-svc'
    try:
        core_api.delete_namespaced_service(
            name=service_name,
            namespace=namespace,
            propagation_policy="Background",
            body=delete_service_req, 
        )
    except ApiException as e:
        # Only throw error if resource found but not deleted.
        if e.status == 404:
            print("Service resource was not found.")
        else:
            raise e
    
    hpa_name = service_user + '-' + func + '-hpa'
    delete_hpa_req = client.V1DeleteOptions(
        api_version = "autoscaling/v1",
        kind="DeleteOptions",
    )
    try:
        autoscaling_api.delete_namespaced_horizontal_pod_autoscaler(
            name=hpa_name,
            namespace=namespace,
            propagation_policy="Background",
            body=delete_hpa_req,
        )
    except ApiException as e:
        # Only throw error if resource found but not deleted.
        if e.status == 404:
            print("HPA resource was not found.")
        else:
            raise e

    deployment_name = service_user + '-' + func + '-deployment'
    delete_deployment_req = client.V1DeleteOptions(
        api_version = "autoscaling/v1",
        kind="DeleteOptions",
    )
    try:
        apps_api.delete_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            propagation_policy="Background",
            body=delete_deployment_req,
        )
    except ApiException as e:
        # Only throw error if resource found but not deleted.
        if e.status == 404:
            print("HPA resource was not found.")
        else:
            raise e
    


def reap(psql_cursor: DictCursor, db_conn):
    psql_cursor.execute("SELECT * FROM services")
    rows = psql_cursor.fetchall()

    for row in rows:
        last_touched = row["last_touched"] 
        delta = (datetime.now(tz=pytz.timezone(os.getenv("TIMEZONE"))) - last_touched).total_seconds()
        if delta > int(os.getenv("SAVE_WINDOW")):
            try:
                delete_service(row["service_user"], row["func"])
                psql_cursor.execute("DELETE FROM services WHERE id=%s", [row["id"]])
            except ApiException as e:
                print(f'failed to delete service with id {row["id"]}. Error: {e}', file=sys.stderr)
    db_conn.commit()

if __name__ == "__main__":
    try:
        db_conn = psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME")
        )
    except Exception as e:
        print(f'Could not establish connection to db with error: {e}', file=sys.stderr)
        sys.exit(1)
    scheduler = sched.scheduler(timefunc=time.monotonic, delayfunc=time.sleep)
    cursor = db_conn.cursor(cursor_factory=DictCursor)
    periodic(scheduler, 5, reap, actionargs=[cursor, db_conn])
    scheduler.run()
    cursor.close()
    db_conn.close()
    
