import os

from six.moves import configparser


class EnvironmentConfigParser(configparser.ConfigParser):
    """ConfigParser which is able to substitute environment variables.
    """

    def get(self, section, option, raw=0, vars=None, **kwargs):
        try:
            val = configparser.ConfigParser.get(
                self, section, option, raw=raw, vars=vars)
        except Exception:
            val = configparser.ConfigParser.get(
                self, section, option, raw=1, vars=vars)

        return self._interpolate(section, option, val, vars)

    def _interpolate(self, section, option, rawval, vars):
        """Adds the additional key-value pairs to the interpolation.

        Also allows to use default values in %(KEY:-DEFAULT)s"""
        if not vars:
            vars = {}

        for k, v in os.environ.items():
            if k not in vars.keys():
                vars[k] = v

        value = rawval
        depth = configparser.MAX_INTERPOLATION_DEPTH
        while depth:                    # Loop through this until it's done
            depth -= 1
            start = value.find("%(")
            if start > -1:
                end = value.find(")s", start)
                if end <= start:
                    raise ValueError(
                        "configparser: no \")s\" found "
                        "after \"%(\" : " + rawval)

                rawkey = value[start + 2:end]
                default = None
                key = rawkey
                sep = rawkey.find(':-')
                if sep > -1:
                    default = rawkey[sep + 2:]
                    key = key[:sep]

                if key in vars:
                    value = value.replace("%(" + rawkey + ")s", vars[key], 1)
                elif rawkey in self.defaults():
                    value = value.replace("%(" + rawkey + ")s",
                                          self.defaults()[rawkey], 1)
                else:
                    if default:
                        value = value.replace("%(" + rawkey + ")s", default, 1)
                    else:
                        raise ValueError(
                            "configparser: Key %s not found in: %s" % (
                                rawval, key))
            else:
                break
        if value.find("%(") != -1:
            raise ValueError(
                "configparser: Interpolation Depth error: %s" % rawval)
        return value
