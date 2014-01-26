#!/usr/bin/env python
# coding:utf-8

# deckorator do zerowania stanu pluginu


class PluginDec1(object):
    def __init__(self, func):
        self.dec_func = func
        self.dec_func

    def __get__(self, obj, objtype):
        """Support instance methods."""
        import functools
        return functools.partial(self.__call__, obj)

    def __call__(self, *args, **kwargs):
        resp = self.dec_func(*args, **kwargs)
        args[0].response = None
        return resp


# class TestDec(object):

    # @PluginDec2
    # def dec_meth(self):
        # print "Dec method !!!!!"


# def PluginDec1(func):
    # def wrap(*args):  # argumenty dekorowanej funkcji

        # resp = func(*args)
        # args[0].response = None
        # return resp
    # return wrap


class Worker(object):

    def __init__(self):
        pass

    def response(self):
        return self.factory.get_response(self.context)


class WorkerConvert(Worker):

    def __init__(self, res_factory):
        self.context = "convert"
        # tu będziemy przechowywać klasy
        self.plugin_cls = [PluginConvert()]
        # ale w samych workerach będą już używane instancje
        # jeżeli instance to mamy problem z przechowywaniem danych
        # potrzeba metod towrzenia pluginów z każdym razem.
        # ewnetulanie można użyc metod resetujących
        # lub coś innego ....

        # worker musi sam rozpoznawać typ napisów na podstawie danych
        # uzyskanych z klas pluginów
        # do dalszej pracy tylko jedna klasa
        # tworzy dwa pluginy do decompose i compose

        # dekorator chyba ??? może także ustawiać obiekt response dla pluginów
        # niestety potrzebna była by referencja do fabryki obiektów response co
        # może być trudne w realizacji

        # self.worker_plugin = PluginConvert()
        self.factory = res_factory

    def work_one(self):
        resp = self.response()
        plug = self.plugin_cls[0]
        plug.set_response(resp)
        res1 = plug.do_work_one()
        print res1.log
        print res1.data
        # resp = self.response() #tworzymy tu nowy obiekt response
        plug.set_response(self.response())
        res2 = plug.do_work_two()
        print res2.log
        print res2.data

    def work_two(self):
        resp = self.factory.get_response(self.context)
        plug = self.plugin_cls[0]
        res1 = plug.do_work_two()
        print res1.log
        print res1.data

    def work_three(self):
        resp = self.factory.get_response(self.context)
        plug = self.plugin_cls[0]
        res1 = plug.do_work_three()
        print res1.log
        print res1.data
        print type(res1)


class Response(object):

    def __init__(self):
        self.success = False
        self.log = []
        self.exception = []
        self.data = None

    def set_data(self, data):
        self.data = data


class ResponseConvert(Response):

    def __init__(self):
        super(ResponseConvert, self).__init__()
        self.context = 'convert'


class ResponseSubDownload(Response):

    def __init__(self):
        super(ResponseConvert, self).__init__()
        self.context = 'subdownload'


class ResponseFactory(object):

    def __init__(self):
        self.response_cls = {
            'convert': ResponseConvert,
            'subdownload': ResponseSubDownload,
        }

    def get_response(self, context):
        return self.response_cls.get(context, Response)()


class PluginConvert(object):

    def __init__(self):
        self.response = None

    def set_response(self, resp):
        self.response = resp

    @PluginDec1
    def do_work_one(self):
        if self.response is None:
            raise ResponseNotSet('Plugin Convert')
        resp = self.response
        resp.log.append("work 1")
        resp.set_data("po work one")
        return  resp

    @PluginDec1
    def do_work_two(self):
        if self.response is None:
            raise ResponseNotSet('Plugin Convert')
        resp = self.response
        resp.log.append("work 2")
        resp.set_data("po work two")
        return resp

    @PluginDec1
    def do_work_three(self):
        if self.response is None:
            raise ResponseNotSet('Plugin Convert')
        resp = self.response
        resp.log.append("work 3")
        resp.set_data("po work three")
        return resp

    def get_context():
        return 'mpl2'

    def get_context1(cls):
        g = cls
        g.context = 'sert'
        return g

class ResponseNotSet(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr("Respons not set in %s" % str(self.value))

if __name__ == "__main__":
    # test = TestDec()
    # test.dec_meth()

    factory = ResponseFactory()
    worker = WorkerConvert(factory)
    worker.work_one()
    worker.work_two()
    worker.work_three()
