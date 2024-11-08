import json
import os.path
import sys
from conf.config import SCHEDULE_FILE
from conf.config import CONFIG_FILE
from conf.config import slicer_configs

def load_printing_schedule(file_name=SCHEDULE_FILE):
    if not os.path.exists(file_name):
        print(f'the {file_name} not found')
        sys.exit(-1)

    f = open(file_name)
    json_data = json.load(f)
    f.close()
    return json_data


def get_conf_filename():
    return CONFIG_FILE

class ConfigParser:
    def __init__(self, logger, conf={}, conf_metadata={}):
        self.conf = conf
        self.conf_metadata = conf_metadata
        self.logger = logger
        print(self.logger)
        # Init the log with config file first
        for key, opts in slicer_configs.items():
            for name, typ, dflt, rng, desc in opts:
                self.conf[name] = dflt
                self.conf_metadata[name] = {
                    "type": typ,
                    "default": dflt,
                    "range": rng,
                    "descr": desc
                }
        # Load config from ini file
        self.load_configs()

    def set_config(self, key, valstr):
        key = key.strip()
        key = key.replace('-', '_')
        valstr = valstr.strip()
        if key not in self.conf_metadata:
            if self.logger is not None:
                self.logger.info("WARN: Ignoring unknown config option: {}".format(key))
            else:
                print("WARN: Ignoring unknown config option: {}".format(key))
            return
        typ = self.conf_metadata[key]["type"]
        rng = self.conf_metadata[key]["range"]
        badval = True
        typestr = ""
        errmsg = ""
        if typ is bool:
            typestr = "boolean "
            errmsg = "Value should be either True or False"
            if valstr in ["True", "False"]:
                self.conf[key] = valstr == "True"
                badval = False
        elif typ is int:
            typestr = "integer "
            errmsg = "Value should be between {} and {}, inclusive.".format(*rng)
            try:
                if int(valstr) >= rng[0] and int(valstr) <= rng[1]:
                    self.conf[key] = int(valstr)
                    badval = False
            except(ValueError):
                pass
        elif typ is float:
            typestr = "float "
            errmsg = "Value should be between {} and {}, inclusive.".format(*rng)
            try:
                if float(valstr) >= rng[0] and float(valstr) <= rng[1]:
                    self.conf[key] = float(valstr)
                    badval = False
            except(ValueError):
                pass
        elif typ is str:
            typestr = "string "
            self.conf[key] = valstr
            badval = False
        elif typ is list:
            typestr = ""
            errmsg = "Valid options are: {}".format(", ".join(rng))
            if valstr in rng:
                self.conf[key] = str(valstr)
                badval = False
        if badval:
            if self.logger is not None:
                self.logger.info("WARN: Ignoring bad {0}configuration value: {1}={2}".format(typestr, key, valstr))
                self.logger.info("ERROR", errmsg)
            else:
                print("WARN: Ignoring bad {0}configuration value: {1}={2}".format(typestr, key, valstr))
                print(errmsg)

    def load_configs(self, conffile=""):
        if conffile == "":
            conffile = get_conf_filename()
        # if self.args.verbose > 0:
        #     print("Checking configs \"{}\"".format(conffile))
        if not os.path.exists(conffile):
            if self.logger is not None:
                self.logger.info("WARN"+f"Your config {conffile} does not exist")
            else:
                print(f"Your config {conffile} does not exist")
            return
        if not os.path.isfile(conffile):
            if self.logger is not None:
                self.logger.info("WARN"+ f"Your input config {conffile} is invalid")
            else:
                print(f"Your input config {conffile} is invalid")
            return
        if self.logger is not None:
            self.logger.info("Loading configs from \"{}\"".format(conffile))
        else:
            print("Loading configs from \"{}\"".format(conffile))
        with open(conffile, "r") as f:
            for line in f.readlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, val = line.split("=")
                self.set_config(key, val)

    def save_configs(self):
        conffile = get_conf_filename()
        confdir = os.path.dirname(conffile)
        if not os.path.exists(confdir):
            os.makedirs(confdir)
        with open(conffile, "w") as f:
            for sect, opts in slicer_configs.items():
                f.write("# {}\n".format(sect))
                for name, typ, dflt, rng, desc in opts:
                    # Ignore start and end gcode to write into
                    if name == 'start_gcode' or name == 'end_gcode':
                        self.conf[name] = self.conf[name].replace("\n", "\\n")
                    f.write("{}={}\n".format(name, self.conf[name]))
                f.write("\n\n")
        if self.logger is not None:
            self.logger.info("INFO"+"Saving configs to {}".format(conffile))
        else:
            if self.logger is not None:
                self.logger.info("INFO"+"Saving configs to {}".format(conffile))
            else:
                print("Saving configs to {}".format(conffile))

    def display_configs_help(self, key=None, vals_only=False):
        keys = []

        if key:  # -- query
            key = key.strip()
            key = key.replace('-', '_')
            for s, opts in slicer_configs.items():
                for k in opts:
                    if re.search(key, k[0]):  # -- match partial name match
                        keys.append(k[0])
            if len(keys) == 0:
                if self.logger is not None:
                    self.logger.info("WARN"+"Unknown config option: {}".format(key))
                else:
                    print("Unknown config option: {}".format(key))
                return

        for sect, opts in slicer_configs.items():
            if not vals_only and not key:
                if self.logger is not None:
                    self.logger.info("WARN"+ "{}:".format(sect))
                else:
                    print("{}:".format(sect))
            for name, typ, dflt, rng, desc in opts:
                if key and name not in keys:
                    continue
                if typ is bool:
                    typename = "bool"
                    rngstr = "True/False"
                elif typ is int:
                    typename = "int"
                    rngstr = "{} ... {}".format(*rng)
                elif typ is float:
                    typename = "float"
                    rngstr = "{} ... {}".format(*rng)
                elif typ is list:
                    typename = "opt"
                    rngstr = ", ".join(rng)
                if self.logger is not None:
                    self.logger.info("INFO"+ "  {} = {}".format(name, self.conf[name]))
                else:
                    print("  {} = {}".format(name, self.conf[name]))
                if not vals_only:
                    if self.logger is not None:
                        self.logger.info("          Type: {}  ({})".format(typename, rngstr))
                        self.logger.info("          {}".format(desc))
                    else:
                        print("          Type: {}  ({})".format(typename, rngstr))
                        print("          {}".format(desc))