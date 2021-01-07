class Bird:
    def fly(self):
        print('Flying')

    def make_noise(self):
        print('Sings')

    def swim(self):
        print('Swims')


class Duck(Bird):
    # Should not raise a warning
    def make_noise(self):
        print('Quacks')


class Penguin(Bird):
    # Should raise a warning
    def fly(self):
        raise NotImplementedError('Can\'t fly')


class BabyDuck(Duck):
    # Should raise a warning
    def fly(self):
        raise NotImplementedError('Can\'t fly yet')

    # Should not raise a warning
    def play(self):
        pass









