from abc import abstractmethod, ABC


class SimpleCalculator:

    def __init__(self):
        print('Initialized')

    def add(self, num, num2):
        return num + num2

    def divide(self, num, num2):
        pass

    def multiply(self, num, num2):
        raise NotImplementedError()

    @abstractmethod
    def subtract(self, num, num2):
        return num - num2

    def log(self, message):
        print(message)


class CalculatorThatPrints(SimpleCalculator):

    def divide(self, num, num2):
        result = num / num2
        print(result)
        return result

    def multiply(self, num, num2):
        result = num * num2
        print(result)
        return result

    def subtract(self, num, num2):
        result = num - num2
        print(result)
        return result

    # Should cause warning
    def log(self, message):
        message += 'Modified'
        return super(SimpleCalculator).log(message)

    # Should not cause warning
    def add(self, num, num2):
        return super(CalculatorThatPrints, self).add(num, num2)


class DifferentCalculator(SimpleCalculator, ABC):

    # Should not cause warning
    def __init__(self):
        super(SimpleCalculator).__init__()
        print('Test')

    # Should cause warning
    def add(self, num, num2):
        return num + num2 + num2



