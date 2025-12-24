import logging
import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "FS": 500,
    "FILTER": {
        "LOWCUT": 1,
        "HIGHCUT": 50,
        "ORDER": 5
    },
    "CLINICAL_THRESHOLDS": {
        "ACCEL_BPM": 15,
        "ACCEL_SEC": 15,
        "DECEL_BPM": 15,
        "DECEL_SEC": 15,
        "BASELINE_LOW": 110,
        "BASELINE_HIGH": 160
    },
    "PEAK_DETECTION": {
        "MIN_DIST_MS": 300,  # Minimum distance between peaks in ms (approx 200 bpm max)
        "INTEGRATION_WINDOW_MS": 150 # Window for moving integration
    },
    "MIN_SIMULATION_DURATION_SEC": 300, # 5 minutes
    "SIMULATION_WINDOW_SEC": 30 # 30 seconds moving window
}

class Config:
    _instance = None
    _config_data = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self._config_data = json.load(f)
                    # Simple merge with defaults to ensure all keys exist
                    self._merge_config(DEFAULT_CONFIG, self._config_data)
            except Exception as e:
                logging.error(f"Failed to load config, using defaults: {e}")
                self._config_data = DEFAULT_CONFIG.copy()
        else:
            self._config_data = DEFAULT_CONFIG.copy()
            self.save_config()

    def _merge_config(self, default, current):
        for key, value in default.items():
            if key not in current:
                current[key] = value
            elif isinstance(value, dict) and isinstance(current[key], dict):
                self._merge_config(value, current[key])

    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self._config_data, f, indent=4)
        except Exception as e:
            logging.error(f"Failed to save config: {e}")

    def get(self, key, default=None):
        return self._config_data.get(key, default)

    def set(self, key, value):
        self._config_data[key] = value
        self.save_config()

    @property
    def FS(self):
        return self._config_data.get("FS", 500)

    @property
    def FILTER(self):
        return self._config_data.get("FILTER", {})

    @property
    def CLINICAL_THRESHOLDS(self):
        return self._config_data.get("CLINICAL_THRESHOLDS", {})
    
    @property
    def PEAK_DETECTION(self):
        return self._config_data.get("PEAK_DETECTION", {})

    @property
    def MIN_SIMULATION_DURATION_SEC(self):
        return self._config_data.get("MIN_SIMULATION_DURATION_SEC", 300)

    @property
    def SIMULATION_WINDOW_SEC(self):
        return self._config_data.get("SIMULATION_WINDOW_SEC", 30)
