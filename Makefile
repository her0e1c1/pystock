sh:
	docker exec -it pystock /bin/bash

py:
	docker exec -it pystock ipython

jp:
	docker exec -it pystock ./start_jupyter --allow-root

prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up

deploy:
	cd ansible && ansible-playbook site.yml

deploy-service:
	cd ansible && ansible-playbook site.yml --start-at-task=docker_service
