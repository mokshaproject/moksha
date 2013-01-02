import os
import ConfigParser


class EnvironmentConfigParser(ConfigParser.ConfigParser):
    """ConfigParser which is able to substitute environment variables.
    """

    def get(self, section, option, raw=0, vars=None):
        try:
            val = ConfigParser.ConfigParser.get(
                self, section, option, raw, vars)
        except Exception:
            val = ConfigParser.ConfigParser.get(
                self, section, option, 1, vars)
        return self._interpolate(section, option, val, vars)

    def _interpolate(self, section, option, rawval, vars):
        """Adds the additional key-value pairs to the interpolation.

        Also allows to use default values in %(KEY:-DEFAULT)s"""
        if not vars:
            vars = {}

        for k, v in os.environ.items():
            if not k in vars.keys():
                vars[k] = v

        value = rawval
        depth = ConfigParser.MAX_INTERPOLATION_DEPTH
        while depth:                    # Loop through this until it's done
            depth -= 1
            start = value.find("%(")
            if start > -1:
                end = value.find(")s", start)
                if end <= start:
                    raise ValueError(
                        "ConfigParser: no \")s\" found "
                        "after \"%(\" : " + rawval)
                    return ""

                rawkey = value[start + 2:end]
                default = None
                key = rawkey
                sep = rawkey.find(':-')
                if sep > -1:
                    default = rawkey[sep + 2:]
                    key = key[:sep]

                if key in vars:
                    value = value.replace("%(" + rawkey + ")s", vars[key], 1)
                else:
                    if default:
                        value = value.replace("%(" + rawkey + ")s", default, 1)
                    else:
                        raise ValueError(
                            "ConfigParser: Key %s not found in: %s" % (
                                rawval, key))
            else:
                break
        if value.find("%(") != -1:
            raise ValueError(
                "ConfigParser: Interpolation Depth error: %s" % rawval)
        return value
