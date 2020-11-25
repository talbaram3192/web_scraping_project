import logging
import sys

logger = logging.getLogger('car')
logger.setLevel(logging.DEBUG)

# Create Formatter
formatter = logging.Formatter('%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s')

# create a file handler and add it to logger
file_handler = logging.FileHandler('car_log_file.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class Car:
    def __init__(self, make, num_cylinders):
        self._make = make
        if not str(num_cylinders).isdigit():
            logger.error(f'Invalid number of cylinders: {num_cylinders}')
            return
        self._num_cylinders = int(num_cylinders)
        logger.info(f'Car successfully created, make: {make}, num_cylinders: {num_cylinders}')

    def get_num_cylinders(self):
        logger.debug(f'Returning number of cylinders: {self._num_cylinders}')
        return self._num_cylinders


car1 = Car('Honda', 4)
car1.get_num_cylinders()
car2 = Car('Honda', 6)
car3 = Car('Honda', 'hi')