import time, multiprocessing
from accountpool.processors.server import app
from accountpool.processors import generator as generators
from accountpool.processors import tester as testers
from accountpool.settings import *
from loguru import logger

if IS_WINDOWS:
    multiprocessing.freeze_support()

tester_process, generator_process, server_process = None, None, None

class Scheduler(object):

    def run_tester(self, website, cycle=CYCLE_TESTER):
        """
        启动测试模块
        """
        if not ENABLE_TESTER:
            logger.info('tester not enable, exit')
            return
        
        # getattr(testers, TESTER_MAP[website] 获取tester下的TESTER_MAP[website]类，调用并传递website
        tester = getattr(testers, TESTER_MAP[website])(website)
        loop = 0
        while True:
            logger.debug(f'tester loop {loop} start ...')
            tester.run()
            loop += 1
            time.sleep(cycle)
    
    def run_generator(self, website, cycle=CYCLE_GENERATOR):
        """
        启动生成模块
        """
        if not ENABLE_GENERATOR:
            logger.info('generator not enable, exit')
            return
        
        # 获取generators下的GENERATOR_MAP['website']类，调用并传递website
        generator = getattr(generators, GENERATOR_MAP['website'])(website)
        loop = 0
        while True:
            logger.debug(f'getter loop {loop} start ...')
            generator.run()
            loop += 1
            time.sleep(cycle)

    def run_server(self, _):
        """
        启动接口模块
        """
        if not ENABLE_SERVER:
            logger.info('server not enable, exit')
            return 
        app.run(host=API_HOST, port=API_PORT, threaded=API_THREADED)
    
    def run(self, website):
        global tester_process, generator_process, server_process
        try:
            logger.info('starting account pool ...')
            if ENABLE_TESTER:
                # 创建一个测试模块的进程
                tester_process = multiprocessing.Process(target=self.run_tester, args=(website,))
                logger.info(f'starting tester, pid {tester_process.pid} ...')
                tester_process.start()
            
            if ENABLE_GENERATOR:
                # 创建一个生成模块的进程
                generator_process = multiprocessing.Process(target=self.run_generator, args=(website,))
                logger.info(f'starting generator, pid {generator_process.pid} ...')
                generator_process.start()
            
            if ENABLE_SERVER:
                # 创建一个接口模块的进程
                server_process = multiprocessing.Process(target=self.run_server, args=(website,))
                logger.info(f'starting server, pid {server_process.pid} ...')
                server_process.start()
            
            # 等待进程执行完毕
            tester_process.join()
            generator_process.join()
            server_process.join()
        except KeyboardInterrupt:
            logger.info('received keyboard interrupt signal')
            # 终止进程
            tester_process.terminate()
            generator_process.terminate()
            server_process.terminate()
        finally:
            tester_process.join()
            generator_process.join()
            server_process.join()
            logger.info(f'tester is {"alive" if tester_process.is_alive() else "dead"}')
            logger.info(f'generator is {"alive" if generator_process.is_alive() else "dead"}')
            logger.info(f'server is {"alive" if server_process.is_alive() else "dead"}')
            logger.info('accountpool terminated')
