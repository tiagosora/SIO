#!/usr/bin/bash 
docker-compose down
docker-compose up -d db
echo "Atenção! Se os volumes estiverem em baixo, este programa dá erro, porque o container demora mais que 3 segundos a ser criado. Roda denovo depois quando o container inicializar por completo"
cd api
export FLASK_APP=api
export FLASK_ENV=development
sleep 3
flask run