
sh:
	docker exec -it pystock bash

py:
	docker exec -it pystock ipython

# jupyter:
# 	docker exec -it pystock jupyter notebook --no-browser --no-mathjax --ip=* --port $PORT --NotebookApp.token='' notebooks

up:
	docker-compose up -d

down:
	docker-compose down
