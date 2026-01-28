.PHONY: setup terraform-init terraform-apply terraform-destroy run-tests generate-report

terraform-init:
	terraform -chdir=terraform init

terraform-apply:
	terraform -chdir=terraform apply -auto-approve

terraform-destroy:
	terraform -chdir=terraform destroy -auto-approve

setup:
	pip install -r scripts/requirements.txt

run-tests: setup
	python3 scripts/run_tests.py

generate-report:
	python3 scripts/generate_report.py
