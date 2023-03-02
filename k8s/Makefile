MK = microk8s kubectl

apply-config:
	@-$(MK) delete configmap mscv-envs-config
	@$(MK) apply -f config_map.yaml

deploy-master:
	@-$(MK) delete deploy mscv-master
	@-$(MK) delete svc mscv-master-svc
	@$(MK) create -f deployment_master.yaml