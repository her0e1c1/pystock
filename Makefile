sh:
	docker exec -it pystock /bin/bash

db:
	sqlite3 db.sqlite3

py:
	docker exec -it pystock ipython

jp:
	docker exec -it jupyter ./start_jupyter --allow-root

open:
	open http://localhost:10003

tor:
	docker exec -it tornado pystock tornado

prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up

deploy:
	git push
	cd ansible && ansible-playbook site.yml

deploy-service:
	cd ansible && ansible-playbook site.yml --start-at-task=docker_service
