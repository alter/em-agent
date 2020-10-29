class TimeConverter:
    def __init__(self, unit=0):
        self.unit = str(unit)

    def __str__(self):
        if 's' in self.unit:
            self.unit = self.unit.replace('s', '')
        elif 'm' in self.unit:
            self.unit = self.unit.replace('m', '')
            self.unit = int(self.unit) * 60
        elif 'h' in self.unit:
            self.unit = self.unit.replace('h', '')
            self.unit = int(self.unit) * 3600
        return str("{}".format(self.unit))

    def __int__(self):
        if 's' in self.unit:
            self.unit = self.unit.replace('s', '')
        elif 'm' in self.unit:
            self.unit = self.unit.replace('m', '')
            self.unit = int(self.unit) * 60
        elif 'h' in self.unit:
            self.unit = self.unit.replace('h', '')
            self.unit = int(self.unit) * 3600
        return int(self.unit)
