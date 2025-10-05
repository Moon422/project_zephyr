cc=python3
mpy=manage.py

run:
	$(cc) $(mpy) runserver

startapp:
	$(cc) $(mpy) startapp $(name)
