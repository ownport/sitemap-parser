# TODO generate final testing report

test-unittest:
	@ echo '***************************'
	@ echo '*       Unittests         *'
	@ echo '***************************'
	@ coverage -e
	@ coverage -x tests/test_sitemap_parser.py
	@ coverage -rm pywsinfo.py

test-all:
	make test-unittest

todo:
	@ echo 
	@ echo "*** TODO list ***"
	@ echo 
	@ awk '/# TODO/ { gsub(/^ /, ""); print }' sitemap.py
	@ echo 

graph:
	@ dot -T png docs/sitemap-parser.gv -o docs/sitemap-parser.png && eog docs/sitemap-parser.png

test-server-start:
	@ python tests/test_server.py start

test-server-restart:
	@ python tests/test_server.py restart

test-server-stop:
	@ python tests/test_server.py stop

test-env:
	@echo "* Create if not exists directory tests/"
	@if ! [ -d tests/log ];then mkdir tests/log; fi 
	@echo "* Create if not exists directory tests/log/"
	@if ! [ -d tests/log ];then mkdir tests/log; fi 
	@echo "* Create if not exists directory tests/run/"
	@if ! [ -d tests/run ];then mkdir tests/run; fi
	@echo "* Create if not exists directory tests/packages/"
	@if ! [ -d tests/packages ];then mkdir tests/packages; fi
	@echo "* Update packages for testing"
	@ wget "https://raw.github.com/defnull/bottle/master/bottle.py" --no-check-certificate -O tests/packages/bottle.py	
	@ wget "https://raw.github.com/ownport/pyservice/master/pyservice.py" --no-check-certificate -O tests/packages/pyservice.py	
