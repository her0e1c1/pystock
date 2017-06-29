sh:
	docker exec -it pystock /bin/bash

py:
	docker exec -it pystock ipython

jp:
	docker exec -it pystock ./start_jupyter --allow-root

deploy:
	cd ansible && ansible-playbook site.yml
