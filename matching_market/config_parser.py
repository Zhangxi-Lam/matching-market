import csv


class ConfigParser:
    def _get_config_from_path(self, config_file_path):
        res = []
        keys = []
        with open(config_file_path) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                if not keys:
                    keys = row
                else:
                    if not row:
                        continue
                    tmp = {}
                    for i in range(len(row)):
                        value = row[i]
                        if value.isdigit():
                            tmp[keys[i]] = int(value)
                        elif value.upper() == 'TRUE':
                            tmp[keys[i]] = True
                        elif value.upper() == 'FALSE':
                            tmp[keys[i]] = False
                        else:
                            tmp[keys[i]] = value
                    res.append(tmp)

        return res

    def __init__(self, config_file_path):
        self.configs = self._get_config_from_path(config_file_path)

    def has_round_config(self, round):
        return round - 1 < len(self.configs)

    def get_round_config(self, round):
        if round - 1 < len(self.configs):
            return self.configs[round - 1]
        else:
            raise ValueError("Doesn't have config for round " + str(round))

    def get_num_round(self):
        return len(self.configs)


def main():
    config = ConfigParser("config/config.csv")
    print(config.configs)


if __name__ == "__main__":
    main()
