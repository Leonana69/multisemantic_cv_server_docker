MK = microk8s kubectl

apply-config:
	@-$(MK) delete configmap mscv-envs-config
	@$(MK) apply -f config-map.yaml

deploy-master:
	@$(MK) create -f deployment_master.yaml

deploy-example-service:
	@$(MK) create -f deployment_example_service.yaml

deploy-example-stateful-service:
	@$(MK) create -f deployment_example_stateful_service.yaml

deploy-human-pose:
	@$(MK) create -f deployment_human_pose.yaml

deploy-custom-tensorflow-serving:
	@$(MK) create -f deployment_custom_tensorflow_serving.yaml

import-master:
	@-microk8s ctr image delete docker.io/library/mscv-master:0.1
	docker save mscv-master > mscv-master.tar
	microk8s ctr image import mscv-master.tar

import-example-service:
	@-microk8s ctr image delete docker.io/library/mscv-example-service:0.1
	docker save mscv-example-service > mscv-example-service.tar
	microk8s ctr image import mscv-example-service.tar

import-example-stateful-service:
	@-microk8s ctr image delete docker.io/library/mscv-example-stateful-service:0.1
	docker save mscv-example-stateful-service > mscv-example-stateful-service.tar
	microk8s ctr image import mscv-example-stateful-service.tar

import-human-pose:
	@-microk8s ctr image delete docker.io/library/mscv-human-pose:0.1
	docker save mscv-human-pose > mscv-human-pose.tar
	microk8s ctr image import mscv-human-pose.tar

import-custom-tensorflow-serving:
	@-microk8s ctr image delete docker.io/library/mscv-custom-tensorflow-serving:0.1
	docker save mscv-custom-tensorflow-serving > mscv-custom-tensorflow-serving.tar
	microk8s ctr image import mscv-custom-tensorflow-serving.tar

clean-master:
	@-$(MK) delete deploy mscv-master
	@-$(MK) delete svc mscv-master-svc

clean:
	@-$(MK) delete deploy mscv-master
	@-$(MK) delete svc mscv-master-svc
	@-$(MK) delete deploy mscv-example-service
	@-$(MK) delete svc mscv-example-service-svc
	@-$(MK) delete deploy mscv-human-pose
	@-$(MK) delete svc mscv-human-pose-svc

clean-stateful:
	@-$(MK) delete sts mscv-example-stateful-service
	@-$(MK) delete svc mscv-example-stateful-service-lb

clean-custom-tensorflow-serving:
	@-$(MK) delete deploy mscv-custom-tensorflow-serving
	@-$(MK) delete svc mscv-human-pose-svc