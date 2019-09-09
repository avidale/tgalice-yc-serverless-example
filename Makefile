all: clean dependencies package

clean:
	rm -rf dist/

dirs:
	mkdir -p dist/

dependencies: dirs
	pip3 install -r requirements.txt --target dist/

install-code: dirs
	cp main.py dist/main.py

package: dirs install-code
	rm -f dist.zip
	cd dist && zip --exclude '*.pyc' -r ../dist.zip ./*

win:
	mkdir dist
	cp main.py dist
	cp form.yaml dist/form.yaml
	pip3 install -r requirements.txt --target dist/
	cd dist && zip --exclude '*.pyc' -r ../dist.zip ./*

.PHONY: clean dirs dependencies install-code package all win
