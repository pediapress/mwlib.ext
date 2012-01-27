GITVERSIONFILE = mwlib/ext/_gitversion.py

all::

sdist:: all
	@echo gitversion=\"$(shell git describe --tags)\" >$(GITVERSIONFILE)
	@echo gitid=\"$(shell git rev-parse HEAD)\" >>$(GITVERSIONFILE)
	@python setup.py -q build sdist
	@rm -f $(GITVERSIONFILE)*

clean::
	git clean -xfd mwlib
	rm -rf build dist

pip-install:: clean sdist
	pip uninstall -y mwlib.rl || true
	pip install dist/*

update::
	git pull
	make pip-install
