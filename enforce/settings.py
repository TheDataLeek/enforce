import enum
import collections

from typing import Optional, Dict, Any, List, Union, Generator

from .utils import merge_dictionaries


class ModeChoices(enum.Enum):
    """
    All possible values for the type checking mode
    """
    invariant = 0 # type: int
    covariant = 1 # type: int
    contravariant = 2 # type: int
    bivariant = 3 # type: int


class Settings:
    def __init__(self, enabled: Optional[bool]=None, group: Optional[str]=None) -> None:
        self.group = group or 'default' # type: str
        self._enabled = enabled # type: Optional[bool]

    @property
    def enabled(self) -> bool:
        """
        Returns if this instance of settings is enabled
        """
        if not _GLOBAL_SETTINGS['enabled']:
            return False

        if self._enabled is None:
            return _GLOBAL_SETTINGS['groups'].get(self.group, False)

        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Only changes the local enabled
        """
        self._enabled = value # type: bool

    @property
    def mode(self) -> int:
        """
        Returns currently selected type checking mode
        If it is None, then it will return invariant
        """
        return _GLOBAL_SETTINGS['mode'] or ModeChoices.invariant

    @property
    def covariant(self) -> bool:
        """
        Returns if covariant type checking mode is enabled
        """
        return _GLOBAL_SETTINGS['mode'] in (ModeChoices.covariant, ModeChoices.bivariant)

    @property
    def contravariant(self) -> bool:
        """
        Returns if contravariant type checking mode is enabled
        """
        return _GLOBAL_SETTINGS['mode'] in (ModeChoices.contravariant, ModeChoices.bivariant)

    def __bool__(self) -> bool:
        return bool(self.enabled)


def config(options=None, *, reset: Optional[bool]=False) -> None:
    """
    Starts the config update based on the provided dictionary of Options
    'None' value indicates no changes will be made
    """
    parsed_config = None # type: Optional[Dict[str, Any]]
    if not reset:
        parsed_config = parse_config(options)

    apply_config(parsed_config, reset)


def reset_config() -> None:
    """
    Resets the global config object to its original state
    """
    default_values = {
        'enabled': True,
        'default': True,
        'mode': ModeChoices.invariant,
        'groups': None
    } # type: Dict[str, Any]

    keys_to_remove = [] # type: List[str]

    for key in _GLOBAL_SETTINGS:
        if key not in default_values:
            keys_to_remove.append(key)

    for key in keys_to_remove:
        del _GLOBAL_SETTINGS[key]

    for key, value in default_values.items():
        if value is not None:
            _GLOBAL_SETTINGS[key] = value

    _GLOBAL_SETTINGS['groups'].clear()


def parse_config(options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates the default config update with a new values for config update
    """
    default_options = {
        'enabled': None,
        'groups': {
            'set': {},
            'disable_previous': False,
            'enable_previous': False,
            'clear_previous': False,
            'default': None
            },
        'mode': None
        }

    return merge_dictionaries(default_options, options)


def apply_config(options: Optional[Dict[str, Any]]=None, reset: Optional[bool]=False) -> None:
    """
    Modifies the global settings object with a provided config updates
    """
    if reset:
        reset_config()
    elif options is not None:
        for key, value in options.items():
            if key == 'enabled':
                if value is not None:
                    _GLOBAL_SETTINGS['enabled'] = value

            elif key == 'groups':
                # For x_previous options, the priority is as follows:
                # 1. Clear
                # 2. Enable
                # 3. Disable

                group_update = {}
                previous_update = []

                for k, v in value.items():
                    if k == 'disable_previous':
                        if v:
                            previous_update.append('d')

                    elif k == 'enable_previous':
                        if v:
                            previous_update.append('e')

                    elif k == 'clear_previous':
                        if v:
                            previous_update.append('c')

                    elif k == 'default':
                        if v is not None:
                            _GLOBAL_SETTINGS['default'] = value['default']

                    elif k == 'set':
                        for group_name, group_status in v.items():
                            if group_name == 'default':
                                raise KeyError('Cannot set \'default\' group status, use \'default\' option rather than \'set\'')
                            if group_status is not None:
                                group_update[group_name] = group_status

                    else:
                        raise KeyError('Unknown option for groups \'{}\''.format(k))
                
                if previous_update:
                    if 'd' in previous_update:
                        for group_name in _GLOBAL_SETTINGS['groups']:
                            _GLOBAL_SETTINGS['groups'][group_name] = False

                    if 'e' in previous_update:
                        for group_name in _GLOBAL_SETTINGS['groups']:
                            _GLOBAL_SETTINGS['groups'][group_name] = True

                    if 'c' in previous_update:
                        _GLOBAL_SETTINGS['groups'].clear()

                _GLOBAL_SETTINGS['groups'].update(group_update)

            elif key == 'mode':
                if value is not None:
                    try:
                        _GLOBAL_SETTINGS['mode'] = ModeChoices[value]
                    except KeyError:
                        raise KeyError('Mode must be one of mode choices')
            else:
                raise KeyError('Unknown option \'{}\''.format(key))


class GlobalSettingsObject(object):
    """
    Class instance to define global configurations
    
    Changing from the old dict in order to specify var types a little better

    _GLOBAL_SETTINGS = {
        'enabled': True,
        'default': True,
        'mode': ModeChoices.invariant,
        'groups': dict()
    }
    """
    def __init__(self):
        self.enabled = True # type: bool
        self.default = True # type: bool
        self.mode    = ModeChoices.invariant # type: int
        self.groups  = dict() # type: Dict[str, bool]

    def __getitem__(self, item: str) -> Any:
        return self.__dict__[item]

    def __setitem__(self, key: str, value: Union[bool, int, Dict]) -> None:
        self.__dict__[key] = value

    def __delitem__(self, key) -> None:
        del self.__dict__[key]

    def __iter__(self) -> Generator[str, None, None]:
        for key in self.__dict__.keys():
            yield key

    def __len__(self) -> int:
        return len(self.__dict__)


_GLOBAL_SETTINGS = GlobalSettingsObject()
