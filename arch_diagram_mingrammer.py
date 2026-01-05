from diagrams import Diagram, Cluster, Edge
from diagrams.k8s.compute import Pod
from diagrams.k8s.network import Service
from diagrams.k8s.storage import PVC
from diagrams.k8s.clusterconfig import HPA
from diagrams.onprem.database import PostgreSQL, MySQL
from diagrams.onprem.monitoring import Prometheus, Grafana
from diagrams.onprem.tracing import Tempo
from diagrams.onprem.logging import Loki

with Diagram(
    "Kubernetes Microservices Architecture",
    show=False,
    outformat="png"
):

    with Cluster("Kubernetes Cluster"):

        with Cluster("Observability"):
            prometheus = Prometheus("Prometheus")
            grafana = Grafana("Grafana")
            loki = Loki("Loki")
            tempo = Tempo("Tempo")

        with Cluster("Order Service"):
            order_hpa = HPA("order-hpa\nmin=2 max=5\nCPU > 50%")
            order_pod = Pod("order-service")
            order_svc = Service("order-svc")
            order_db = PostgreSQL("PostgreSQL")
            order_pvc = PVC("order-db-pvc")

            order_hpa >> Edge(label="scale") >> order_pod
            order_svc >> order_pod
            order_pod >> order_db
            order_db >> order_pvc

        with Cluster("Inventory Service"):
            inventory_hpa = HPA("inventory-hpa\nmin=2 max=5\nCPU > 50%")
            inventory_pod = Pod("inventory-service")
            inventory_svc = Service("inventory-svc")
            inventory_db = MySQL("MySQL")
            inventory_pvc = PVC("inventory-db-pvc")

            inventory_hpa >> Edge(label="scale") >> inventory_pod
            inventory_svc >> inventory_pod
            inventory_pod >> inventory_db
            inventory_db >> inventory_pvc

        order_pod >> Edge(
            label="Sync REST\nResilience4j\n(CB + Retry)",
            style="dashed"
        ) >> inventory_svc

        prometheus >> Edge(label="scrape /actuator/prometheus") >> order_svc
        prometheus >> Edge(label="scrape /actuator/prometheus") >> inventory_svc
        grafana >> Edge(label="PromQL queries") >> prometheus
        grafana >> Edge(label="TraceQL queries") >> tempo

        loki << order_pod
        loki << inventory_pod

        tempo << order_pod
        tempo << inventory_pod